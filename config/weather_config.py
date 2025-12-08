# 날씨 API 설정 파일

# OpenWeatherMap API 키
WEATHER_API_KEY = "your-api-key-here"

# 기본 위치 설정 (대전광역시 유성구)
DEFAULT_LOCATION = {
    'city': '대전광역시 유성구',
    'city_en': 'Daejeon, Yuseong-gu',
    'lat': 36.3621,  # 위도
    'lon': 127.3565,  # 경도
    'country': 'KR'
}

# 대전 유성구 주요 지점 좌표
YUSEONG_LOCATIONS = {
    'kaist': {
        'name': 'KAIST',
        'lat': 36.3721,
        'lon': 127.3604
    },
    'chungnam_univ': {
        'name': '충남대학교',
        'lat': 36.3698,
        'lon': 127.3466
    },
    'yuseong_hot_spring': {
        'name': '유성온천',
        'lat': 36.3553,
        'lon': 127.3429
    },
    'daedeok_innopolis': {
        'name': '대덕특구',
        'lat': 36.3784,
        'lon': 127.3877
    }
}

# API 호출 설정
API_CONFIG = {
    'units': 'metric',  # 섭씨 온도 사용
    'lang': 'kr',       # 한국어 응답
    'timeout': 5        # 타임아웃 5초
}

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