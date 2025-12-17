"""
날씨 정보 조회 서비스
"""
from datetime import datetime, timedelta
from django.conf import settings
import requests
import pytz
from .utils import get_korean_address
from config.weather_config import latlon_to_grid, get_weather_description, DEFAULT_LOCATION


def get_weather_info(lat: float = None, lon: float = None):
    """날씨 정보 조회 - 기상청 API 사용

    Args:
        lat: 위도 (기본값: DEFAULT_LOCATION에서 가져옴)
        lon: 경도 (기본값: DEFAULT_LOCATION에서 가져옴)

    Returns:
        dict: 날씨 정보
    """
    # 기본값 설정
    if lat is None:
        lat = DEFAULT_LOCATION['lat']
    if lon is None:
        lon = DEFAULT_LOCATION['lon']

    api_key = settings.KMA_API_KEY

    # 위경도 -> 격자 좌표 변환
    nx, ny = latlon_to_grid(lat, lon)

    # 기상청 API용 시간 계산 (base_time: 0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300)
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    base_times = ['0200', '0500', '0800', '1100', '1400', '1700', '2000', '2300']
    current_hour = now.hour * 100 + now.minute

    # 현재 시간보다 이전의 가장 가까운 base_time 찾기 (API는 발표시간+10분 후 제공)
    base_time = '2300'
    base_date = now - timedelta(days=1)
    for bt in base_times:
        # 발표시간 + 10분 이후에 데이터 사용 가능
        available_time = int(bt) + 10
        if current_hour >= available_time:
            base_time = bt
            base_date = now

    base_date_str = base_date.strftime('%Y%m%d')

    # 주소 가져오기 (기본값 설정)
    korean_address = get_korean_address(lat, lon)
    city_name = korean_address if korean_address else '대전 유성구'

    try:
        # 단기예보 API 호출
        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        params = {
            'serviceKey': api_key,
            'numOfRows': 300,
            'pageNo': 1,
            'dataType': 'JSON',
            'base_date': base_date_str,
            'base_time': base_time,
            'nx': nx,
            'ny': ny
        }

        response = requests.get(url, params=params, timeout=10)

        try:
            data = response.json()
        except Exception as json_err:
            raise Exception(f"JSON parse error: {json_err}")

        # 응답 파싱
        items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])

        if not items:
            raise Exception("No weather data")

        # 데이터 정리 (시간별로 그룹화)
        weather_by_time = {}
        for item in items:
            fcst_date = item['fcstDate']
            fcst_time = item['fcstTime']
            category = item['category']
            value = item['fcstValue']
            key = f"{fcst_date}_{fcst_time}"

            if key not in weather_by_time:
                weather_by_time[key] = {}
            weather_by_time[key][category] = value

        # 현재 시간에 가장 가까운 데이터 찾기
        current_key = None
        current_time_str = now.strftime('%Y%m%d_%H00')
        for key in sorted(weather_by_time.keys()):
            if key >= current_time_str:
                current_key = key
                break
        if not current_key and weather_by_time:
            current_key = sorted(weather_by_time.keys())[0]

        current_data = weather_by_time.get(current_key, {})

        # 오늘 최고/최저 기온 계산
        today_str = now.strftime('%Y%m%d')
        today_temps = []
        for key, values in weather_by_time.items():
            if key.startswith(today_str) and 'TMP' in values:
                try:
                    today_temps.append(float(values['TMP']))
                except:
                    pass

        temp = float(current_data.get('TMP', 15))
        temp_max = max(today_temps) if today_temps else temp + 3
        temp_min = min(today_temps) if today_temps else temp - 3

        # 날씨 설명 생성
        sky = current_data.get('SKY', '1')
        pty = current_data.get('PTY', '0')
        description = get_weather_description(sky, pty)

        # 습도
        humidity = int(current_data.get('REH', 50))

        # 강수확률과 강수량
        rain_probability = int(current_data.get('POP', 0))
        rain_amount = _parse_rain_amount(current_data.get('PCP', '강수없음'))

        # 풍속
        wind_speed = float(current_data.get('WSD', 0))

        # 아이콘
        icon = _get_weather_icon(sky, pty)

        weather_data = {
            'temp': round(temp, 1),
            'temp_max': round(temp_max),
            'temp_min': round(temp_min),
            'description': description,
            'humidity': humidity,
            'city': city_name,
            'icon': icon,
            'current': {
                'rain_probability': rain_probability,
                'wind_speed': wind_speed,
                'rain_amount': rain_amount
            }
        }

        # 시간별 예보 (12시간)
        hourly_forecast = _build_hourly_forecast(
            weather_by_time, current_time_str, temp, humidity
        )
        weather_data['hourly'] = hourly_forecast

        return weather_data

    except Exception as e:
        print(f"[KMA API Error] {e}")
        return _get_fallback_weather(city_name)


def _parse_rain_amount(rain_amount_str: str) -> float:
    """강수량 문자열을 숫자로 변환"""
    if rain_amount_str == '강수없음':
        return 0
    elif rain_amount_str == '1mm 미만':
        return 0.5
    else:
        try:
            return float(rain_amount_str.replace('mm', ''))
        except:
            return 0


def _build_hourly_forecast(weather_by_time: dict, current_time_str: str,
                           temp: float, humidity: int) -> list:
    """시간별 예보 데이터 구성"""
    hourly_forecast = []
    sorted_keys = sorted(weather_by_time.keys())

    start_idx = 0
    for i, key in enumerate(sorted_keys):
        if key >= current_time_str:
            start_idx = i
            break

    for key in sorted_keys[start_idx:start_idx + 12]:
        data = weather_by_time[key]
        fcst_time = key.split('_')[1]
        hour_str = f"{fcst_time[:2]}시"

        sky_val = data.get('SKY', '1')
        pty_val = data.get('PTY', '0')
        weather_desc = get_weather_description(sky_val, pty_val)

        # 아이콘 매핑 (기상청 코드 -> 간단한 아이콘)
        icon = _get_weather_icon(sky_val, pty_val)

        pop = int(data.get('POP', 0))
        pcp = _parse_rain_amount(data.get('PCP', '강수없음'))

        hourly_forecast.append({
            'time': hour_str,
            'temp': round(float(data.get('TMP', temp)), 1),
            'weather': weather_desc,
            'icon': icon,
            'sky': int(sky_val),
            'pty': int(pty_val),
            'rain_probability': pop,
            'rain_amount': round(pcp, 1),
            'humidity': int(data.get('REH', humidity))
        })

    return hourly_forecast


def _get_weather_icon(sky: str, pty: str) -> str:
    """기상청 코드에서 날씨 아이콘 반환"""
    if pty in ['1', '2', '4', '5', '6']:
        return '🌧️'
    elif pty in ['3', '7']:
        return '🌨️'
    elif sky == '1':
        return '☀️'
    elif sky == '3':
        return '⛅'
    else:
        return '☁️'


def _get_fallback_weather(city_name: str = None) -> dict:
    """API 실패 시 기본 날씨 데이터 반환"""
    if city_name is None:
        city_name = DEFAULT_LOCATION['city']
    return {
        'temp': 15,
        'temp_max': 18,
        'temp_min': 10,
        'description': '날씨 정보 없음',
        'humidity': 50,
        'city': city_name,
        'icon': '☁️',
        'current': {
            'rain_probability': 0,
            'wind_speed': 0,
            'rain_amount': 0
        },
        'hourly': []
    }
