# 날씨 API 설정 파일
import math

# 기본 위치 설정 (대전광역시 유성구)
DEFAULT_LOCATION = {
    'city': '대전광역시 유성구',
    'city_en': 'Daejeon, Yuseong-gu',
    'lat': 36.3621,  # 위도
    'lon': 127.3565,  # 경도
    'nx': 67,  # 기상청 격자 X
    'ny': 100,  # 기상청 격자 Y
    'country': 'KR'
}

# API 호출 설정
API_CONFIG = {
    'timeout': 5  # 타임아웃 5초
}


def latlon_to_grid(lat, lon):
    """
    위경도 -> 기상청 격자 좌표(nx, ny) 변환
    기상청 격자 변환 공식 사용
    """
    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1 = 30.0  # 투영 위도1(degree)
    SLAT2 = 60.0  # 투영 위도2(degree)
    OLON = 126.0  # 기준점 경도(degree)
    OLAT = 38.0  # 기준점 위도(degree)
    XO = 43  # 기준점 X좌표(GRID)
    YO = 136  # 기준점 Y좌표(GRID)

    DEGRAD = math.pi / 180.0

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)

    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn

    nx = int(ra * math.sin(theta) + XO + 0.5)
    ny = int(ro - ra * math.cos(theta) + YO + 0.5)

    return nx, ny


# 기상청 날씨 코드 매핑
SKY_CODE = {
    '1': '맑음',
    '3': '구름많음',
    '4': '흐림'
}

PTY_CODE = {
    '0': '',  # 없음
    '1': '비',
    '2': '비/눈',
    '3': '눈',
    '4': '소나기',
    '5': '빗방울',
    '6': '빗방울눈날림',
    '7': '눈날림'
}


def get_weather_description(sky, pty):
    """SKY와 PTY 코드로 날씨 설명 생성"""
    if pty and pty != '0':
        return PTY_CODE.get(pty, '비')
    return SKY_CODE.get(sky, '맑음')

# 날씨 상태별 옷차림 추천
WEATHER_OUTFIT = {
    'very_cold': {  # -5도 이하
        'description': '매우 추운 날씨',
        'top': '두꺼운 니트, 기모 후드티',
        'bottom': '기모 바지, 두꺼운 청바지',
        'outer': '롱패딩, 헤비 다운',
        'accessory': '목도리, 장갑, 귀마개 필수'
    },
    'cold': {  # -5도 ~ 5도
        'description': '추운 날씨',
        'top': '니트, 맨투맨',
        'bottom': '청바지, 면바지',
        'outer': '패딩, 두꺼운 코트',
        'accessory': '목도리, 장갑 권장'
    },
    'cool': {  # 5도 ~ 15도
        'description': '쌀쌀한 날씨',
        'top': '긴팔 티셔츠, 얇은 니트',
        'bottom': '청바지, 면바지',
        'outer': '가디건, 자켓',
        'accessory': '가벼운 스카프'
    },
    'mild': {  # 15도 ~ 23도
        'description': '온화한 날씨',
        'top': '긴팔/반팔 티셔츠',
        'bottom': '청바지, 면바지',
        'outer': '얇은 가디건 (선택)',
        'accessory': '모자'
    },
    'warm': {  # 23도 ~ 28도
        'description': '따뜻한 날씨',
        'top': '반팔 티셔츠, 블라우스',
        'bottom': '반바지, 얇은 바지',
        'outer': '불필요',
        'accessory': '선글라스, 모자'
    },
    'hot': {  # 28도 이상
        'description': '더운 날씨',
        'top': '반팔, 민소매',
        'bottom': '반바지, 린넨 바지',
        'outer': '불필요',
        'accessory': '선글라스, 모자 필수'
    }
}