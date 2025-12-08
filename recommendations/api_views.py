from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import date
from django.conf import settings
import requests
import random
import json
import os
from .utils import get_korean_address


def load_ootd_data():
    """ootd.json 파일 로드"""
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'ootd.json'),
        os.path.join(settings.BASE_DIR, 'data', 'ootd.json'),
    ]
    for json_path in possible_paths:
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
    return []


def load_food_data():
    """food.json 파일 로드 (인기 음식 75종)"""
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'food.json'),
        os.path.join(settings.BASE_DIR, 'data', 'food.json'),
    ]
    for json_path in possible_paths:
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
    return []


def get_clothes_by_temp_and_category(temp, category, weather_condition="맑음"):
    """온도와 카테고리에 맞는 옷 필터링"""
    ootd_data = load_ootd_data()
    matching_clothes = []
    for item in ootd_data:
        if item.get('category') != category:
            continue
        min_temp = item.get('min_temp', -50)
        max_temp = item.get('max_temp', 50)
        weather_conditions = item.get('weather_conditions', [])
        if min_temp <= temp <= max_temp:
            if not weather_conditions or weather_condition in weather_conditions:
                matching_clothes.append(item)
    return matching_clothes


def get_lucky_color_korean_to_ootd(lucky_color):
    """행운색 -> OOTD 색상 매핑"""
    color_mapping = {
        '빨간색': ['레드', '와인', '버건디'],
        '진한 빨간색': ['버건디', '와인', '다크레드'],
        '주황색': ['오렌지', '코랄', '피치'],
        '노란색': ['옐로우', '머스타드', '골드'],
        '초록색': ['그린', '카키', '올리브'],
        '연두색': ['라임', '민트', '그린'],
        '파란색': ['블루', '네이비', '스카이블루'],
        '하늘색': ['스카이블루', '블루', '네이비'],
        '남색': ['네이비', '블루', '다크블루'],
        '보라색': ['퍼플', '라벤더', '바이올렛'],
        '연보라색': ['라벤더', '퍼플', '바이올렛'],
        '분홍색': ['핑크', '로즈', '코랄'],
        '검은색': ['블랙', '차콜', '다크그레이'],
        '흰색': ['화이트', '아이보리', '크림'],
        '회색': ['그레이', '실버', '차콜'],
        '은색': ['실버', '그레이', '화이트'],
        '갈색': ['브라운', '카멜', '탄'],
        '베이지색': ['베이지', '오트밀', '샌드'],
        '금색': ['골드', '옐로우', '머스타드'],
    }
    return color_mapping.get(lucky_color, [lucky_color])


def get_fortune_data_for_user(user):
    """사용자 운세 데이터 계산"""
    from fortune.services import FortuneCalculator
    if not user.birth_date:
        return None
    calculator = FortuneCalculator()
    return calculator.calculate_fortune(
        birth_date=user.birth_date,
        gender=user.gender,
        birth_time=getattr(user, 'birth_time', None),
        chinese_name=getattr(user, 'chinese_name', None),
        calendar_type=getattr(user, 'calendar_type', 'solar'),
        user_id=user.id,
        session_key=None
    )


class OOTDRecommendationAPIView(APIView):
    """OOTD 추천 API (로그인 필수)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 운세 데이터 가져오기
        fortune_data = get_fortune_data_for_user(request.user)
        if not fortune_data:
            return Response({
                'success': False,
                'error': '생년월일 정보가 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 날씨 정보 가져오기
        weather_data = self._get_weather_info(request)

        # 테스트용 온도 오버라이드
        test_temp = request.query_params.get('test_temp')
        if test_temp:
            try:
                temp = float(test_temp)
                weather_data['temp'] = temp
                weather_data['temp_max'] = temp + 3
                weather_data['temp_min'] = temp - 3
            except ValueError:
                pass

        # 행운색
        lucky_colors = fortune_data.get('lucky_colors', [])[:3]

        # OOTD 추천 생성
        outfit = self._generate_ootd(weather_data, lucky_colors)

        return Response({
            'success': True,
            'weather': weather_data,
            'lucky_colors': lucky_colors,
            'outfit': outfit,
            'date': str(date.today())
        })

    def _get_weather_info(self, request):
        """날씨 정보 조회 (시간별 예보 포함)"""
        from datetime import datetime
        lat = request.query_params.get('lat', 36.3621)
        lon = request.query_params.get('lon', 127.3565)
        api_key = settings.WEATHER_API_KEY

        try:
            # 현재 날씨
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
            response = requests.get(url, timeout=5)
            data = response.json()
            korean_address = get_korean_address(lat, lon)
            city_name = korean_address if korean_address else data.get('name', '대전 유성구')

            # 강수량: rain 또는 snow (눈)
            rain_1h = data.get('rain', {}).get('1h', 0)
            snow_1h = data.get('snow', {}).get('1h', 0)
            precipitation = rain_1h + snow_1h

            weather_data = {
                'temp': round(data['main']['temp'], 1),
                'temp_max': round(data['main']['temp_max']),
                'temp_min': round(data['main']['temp_min']),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'city': city_name,
                'current': {
                    'rain_probability': 0,
                    'wind_speed': data.get('wind', {}).get('speed', 0),
                    'rain_amount': precipitation
                }
            }

            # 시간별 예보 (12시간, 1시간 간격으로 보간)
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
            forecast_response = requests.get(forecast_url, timeout=5)
            hourly_forecast = []

            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                # 오늘 날짜의 데이터만 필터링해서 최고/최저 계산
                from datetime import timedelta
                today = datetime.now().date()
                today_temps = []

                for item in forecast_data['list']:
                    item_date = datetime.fromtimestamp(item['dt']).date()
                    if item_date == today:
                        today_temps.append(item['main']['temp'])

                # 오늘 예보 데이터가 있으면 최고/최저 업데이트
                if today_temps:
                    weather_data['temp_max'] = round(max(today_temps))
                    weather_data['temp_min'] = round(min(today_temps))

                # 3시간 간격 데이터 5개를 가져와서 1시간 간격으로 보간
                raw_data = forecast_data['list'][:5]

                for i in range(len(raw_data) - 1):
                    current = raw_data[i]
                    next_item = raw_data[i + 1]

                    current_dt = datetime.fromtimestamp(current['dt'])
                    current_temp = current['main']['temp']
                    next_temp = next_item['main']['temp']
                    current_pop = current.get('pop', 0)
                    next_pop = next_item.get('pop', 0)
                    # rain + snow (눈) 합산
                    current_rain = current.get('rain', {}).get('3h', 0) + current.get('snow', {}).get('3h', 0)
                    next_rain = next_item.get('rain', {}).get('3h', 0) + next_item.get('snow', {}).get('3h', 0)

                    # 3시간을 1시간 간격으로 보간 (0, 1, 2시간)
                    for h in range(3):
                        if len(hourly_forecast) >= 12:
                            break
                        ratio = h / 3.0
                        interp_temp = current_temp + (next_temp - current_temp) * ratio
                        interp_pop = current_pop + (next_pop - current_pop) * ratio
                        interp_rain = (current_rain + (next_rain - current_rain) * ratio) / 3  # 3시간 강수량을 1시간으로

                        interp_dt = current_dt + timedelta(hours=h)

                        hourly_forecast.append({
                            'time': interp_dt.strftime('%H시'),
                            'temp': round(interp_temp, 1),
                            'weather': current['weather'][0]['description'],
                            'icon': current['weather'][0]['icon'],
                            'rain_probability': int(interp_pop * 100),
                            'rain_amount': round(interp_rain, 1)
                        })

            weather_data['hourly'] = hourly_forecast
            return weather_data

        except Exception:
            return {
                'temp': 15,
                'temp_max': 18,
                'temp_min': 10,
                'description': '날씨 정보 없음',
                'humidity': 50,
                'city': '대전 유성구',
                'current': {
                    'rain_probability': 0,
                    'wind_speed': 0,
                    'rain_amount': 0
                },
                'hourly': []
            }

    def _generate_ootd(self, weather, lucky_colors):
        """OOTD 추천 생성"""
        current_temp = weather.get('temp', 15)
        description = weather.get('description', '맑음')

        if '비' in description or '소나기' in description:
            weather_condition = '비'
        elif '눈' in description:
            weather_condition = '눈'
        elif '흐' in description or '구름' in description:
            weather_condition = '흐림'
        else:
            weather_condition = '맑음'

        # 온도에 맞는 옷 가져오기
        tops = get_clothes_by_temp_and_category(current_temp, '상의', weather_condition)
        bottoms = get_clothes_by_temp_and_category(current_temp, '하의', weather_condition)
        outers = get_clothes_by_temp_and_category(current_temp, '아우터', weather_condition)
        accessories = get_clothes_by_temp_and_category(current_temp, '액세서리', weather_condition)

        # 행운색 변환
        lucky_color_variants = []
        if lucky_colors:
            for lc in lucky_colors:
                variants = get_lucky_color_korean_to_ootd(lc)
                if variants and variants[0] not in lucky_color_variants:
                    lucky_color_variants.append(variants[0])

        # 상의 선택
        if tops:
            selected_top = random.choice(tops)
            top_name = selected_top.get('name', '니트')
            top_desc = selected_top.get('description', '따뜻하고 포근한 느낌')
        else:
            top_name, top_desc = '니트', '따뜻하고 포근한 느낌'

        # 하의 선택
        if bottoms:
            selected_bottom = random.choice(bottoms)
            bottom_name = selected_bottom.get('name', '청바지')
            bottom_desc = selected_bottom.get('description', '편안한 일상 바지')
        else:
            bottom_name, bottom_desc = '청바지', '편안한 일상 바지'

        # 아우터 선택
        outer_required = current_temp < 20
        if outers and outer_required:
            selected_outer = random.choice(outers)
            outer_name = selected_outer.get('name', '코트')
            outer_desc = selected_outer.get('description', '바람을 막아주는 아우터')
        else:
            outer_name, outer_desc = '불필요', ''
            outer_required = False

        # 색상 추천
        if lucky_color_variants:
            top_color = lucky_color_variants[0]
            top_alt_colors = lucky_color_variants[1:] if len(lucky_color_variants) > 1 else []
        else:
            top_color = '베이지'
            top_alt_colors = ['그레이', '네이비']

        bottom_color = '블랙'
        bottom_alt_colors = ['네이비', '차콜']

        # 스타일 태그
        if current_temp >= 28:
            style_tags = ['한여름', '시원한', '가벼운']
        elif current_temp >= 23:
            style_tags = ['초여름', '활동적인', '캐주얼']
        elif current_temp >= 17:
            style_tags = ['간절기', '편안한', '깔끔한']
        elif current_temp >= 9:
            style_tags = ['가을', '레이어드', '포근한']
        else:
            style_tags = ['겨울', '따뜻한', '방한']

        # 액세서리
        accessory_emoji = {'머플러': '🧣', '장갑': '🧤', '비니': '🎿', '모자': '🧢', '우산': '☂️'}
        recommended_accessories = [
            {
                'name': acc.get('name', ''),
                'description': acc.get('description', ''),
                'emoji': accessory_emoji.get(acc.get('name', ''), '✨')
            }
            for acc in accessories
        ]

        return {
            'top': top_name,
            'top_desc': top_desc,
            'bottom': bottom_name,
            'bottom_desc': bottom_desc,
            'outer': outer_name,
            'outer_desc': outer_desc,
            'outer_required': outer_required,
            'style_tags': style_tags,
            'top_color': top_color,
            'top_alt_colors': top_alt_colors,
            'bottom_color': bottom_color,
            'bottom_alt_colors': bottom_alt_colors,
            'accessories': recommended_accessories,
        }


class MenuRecommendationAPIView(APIView):
    """메뉴 추천 API (로그인 필수)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 운세 데이터 가져오기
        fortune_data = get_fortune_data_for_user(request.user)
        if not fortune_data:
            return Response({
                'success': False,
                'error': '생년월일 정보가 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        lucky_color = fortune_data.get('lucky_colors', ['노란색'])[0]

        # 음식 데이터 로드
        all_foods = load_food_data()
        matching_foods = self._get_food_by_color(lucky_color, all_foods)

        # 추천 음식 선택
        if len(matching_foods) >= 2:
            recommended_list = random.sample(matching_foods, 2)
        elif len(matching_foods) == 1:
            recommended_list = matching_foods
        else:
            recommended_list = random.sample(all_foods, min(2, len(all_foods)))

        # 추천 형식화
        recommendations = []
        for idx, food in enumerate(recommended_list, 1):
            recommendations.append({
                'rank': idx,
                'color': lucky_color,
                'menu': {
                    'name': food.get('name_ko', ''),
                    'category': food.get('type', '기타'),
                    'icon': self._get_emoji_for_food(food),
                    'desc': food.get('desc', f"행운의 {lucky_color} 에너지를 담은 음식입니다.")
                },
                'bg_gradient': self._get_gradient_for_color(lucky_color)
            })

        # 다른 추천
        recommended_ids = [f.get('id') for f in recommended_list]
        other_foods = [f for f in all_foods if f.get('id') not in recommended_ids]
        other_list = random.sample(other_foods, min(6, len(other_foods))) if other_foods else []

        other_recommendations = [
            {
                'color': self._get_korean_color(food.get('color_category', '')),
                'menu': {
                    'name': food.get('name_ko', ''),
                    'category': food.get('type', '기타'),
                    'icon': self._get_emoji_for_food(food),
                }
            }
            for food in other_list
        ]

        return Response({
            'success': True,
            'lucky_color': lucky_color,
            'recommendations': recommendations,
            'other_recommendations': other_recommendations,
            'date': str(date.today())
        })

    def _get_food_by_color(self, lucky_color, foods):
        """행운색에 맞는 음식 필터링"""
        color_mapping = {
            '노란색': ['yellow', 'gold', 'amber'],
            '베이지색': ['beige', 'tan', 'cream'],
            '검은색': ['black', 'dark'],
            '빨간색': ['red', 'crimson'],
            '주황색': ['orange', 'coral'],
            '초록색': ['green', 'lime'],
            '파란색': ['blue', 'navy', 'cyan'],
            '보라색': ['purple', 'violet'],
            '흰색': ['white', 'ivory', 'cream'],
            '분홍색': ['pink', 'rose'],
            '갈색': ['brown', 'chocolate'],
            '회색': ['gray', 'grey', 'silver'],
            '금색': ['gold', 'golden'],
        }
        target_keywords = color_mapping.get(lucky_color, [lucky_color.lower()])
        matching = []
        for food in foods:
            food_color = food.get('color_category', '').lower()
            for keyword in target_keywords:
                if keyword in food_color:
                    matching.append(food)
                    break
        return matching

    def _get_emoji_for_food(self, food):
        """음식별 이모지 반환 (food.json에서 직접 가져오기)"""
        # food.json에 icon 필드가 있으면 그대로 사용
        if 'icon' in food and food['icon']:
            return food['icon']

        # icon이 없으면 타입별 기본 이모지 사용
        type_emoji_map = {
            'Fruit': '🍎', 'Vegetable': '🥬', 'Dish': '🍲',
            'Beverage': '🥤', 'Dessert': '🍰', 'Seafood': '🦐',
            'Dairy': '🧀', 'Grain': '🍚', 'Ingredient': '🥘'
        }
        return type_emoji_map.get(food.get('type', ''), '🍽️')

    def _get_korean_color(self, eng_color):
        """영어 색상 -> 한글"""
        mapping = {
            'yellow': '노란색', 'red': '빨간색', 'green': '초록색',
            'blue': '파란색', 'black': '검은색', 'white': '흰색',
            'brown': '갈색', 'orange': '주황색', 'pink': '분홍색',
            'multi': '다양', 'pink': '분홍색'
        }
        eng_color = eng_color.split('/')[0].lower()
        for k, v in mapping.items():
            if k in eng_color:
                return v
        return '기타'

    def _get_gradient_for_color(self, color):
        """색상별 그라데이션 배경"""
        gradients = {
            '빨간색': 'linear-gradient(135deg, #ff6b6b, #ee5a5a)',
            '주황색': 'linear-gradient(135deg, #ffa726, #ff9800)',
            '노란색': 'linear-gradient(135deg, #ffeb3b, #ffc107)',
            '초록색': 'linear-gradient(135deg, #66bb6a, #43a047)',
            '파란색': 'linear-gradient(135deg, #42a5f5, #1e88e5)',
            '보라색': 'linear-gradient(135deg, #ab47bc, #8e24aa)',
            '분홍색': 'linear-gradient(135deg, #f48fb1, #ec407a)',
            '갈색': 'linear-gradient(135deg, #8d6e63, #6d4c41)',
            '흰색': 'linear-gradient(135deg, #fafafa, #e0e0e0)',
            '검은색': 'linear-gradient(135deg, #424242, #212121)',
            '회색': 'linear-gradient(135deg, #9e9e9e, #757575)',
        }
        return gradients.get(color, 'linear-gradient(135deg, #667eea, #764ba2)')


class WeatherAPIView(APIView):
    """날씨 정보 API"""
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get('lat', 36.3621)
        lon = request.query_params.get('lon', 127.3565)
        api_key = settings.WEATHER_API_KEY

        try:
            # 현재 날씨
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
            response = requests.get(url, timeout=5)
            data = response.json()

            current_weather = {
                'temp': round(data['main']['temp'], 1),
                'temp_max': round(data['main']['temp_max']),
                'temp_min': round(data['main']['temp_min']),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'icon': data['weather'][0]['icon'],
            }

            # 시간별 예보
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
            forecast_response = requests.get(forecast_url, timeout=5)
            hourly_forecast = []

            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                for item in forecast_data['list'][:8]:  # 24시간 (3시간 간격)
                    from datetime import datetime
                    dt = datetime.fromtimestamp(item['dt'])
                    hourly_forecast.append({
                        'time': dt.strftime('%H:%M'),
                        'temp': round(item['main']['temp'], 1),
                        'weather': item['weather'][0]['description'],
                        'icon': item['weather'][0]['icon'],
                        'rain_probability': int(item.get('pop', 0) * 100),
                    })

            korean_address = get_korean_address(lat, lon)
            city_name = korean_address if korean_address else data.get('name', 'Unknown')

            return Response({
                'success': True,
                'current': current_weather,
                'hourly': hourly_forecast,
                'city': city_name
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """위치 기반 날씨 (POST로 좌표 전송)"""
        lat = request.data.get('lat', 36.3621)
        lon = request.data.get('lon', 127.3565)
        request.query_params._mutable = True
        request.query_params['lat'] = lat
        request.query_params['lon'] = lon
        return self.get(request)
