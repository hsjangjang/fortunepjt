from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from datetime import date
from django.conf import settings
import json
import os
import random
from django.conf import settings
from .utils import get_korean_address
from fortune.api_views import load_fortune_from_db


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
            except Exception as e:
                print(f"OOTD JSON 로드 오류 ({json_path}): {e}")

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

        # 온도 범위 체크
        if min_temp <= temp <= max_temp:
            # 날씨 조건 체크 (조건이 맞거나, 조건이 없으면 통과)
            if not weather_conditions or weather_condition in weather_conditions:
                matching_clothes.append(item)

    return matching_clothes


def get_lucky_color_korean_to_ootd(lucky_color):
    """행운색(한글) -> OOTD에서 사용 가능한 색상으로 매핑"""
    color_mapping = {
        # 기본 색상
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

class OOTDRecommendationView(LoginRequiredMixin, TemplateView):
    template_name = 'recommendations/ootd.html'
    login_url = '/users/login/'

    def get(self, request, *args, **kwargs):
        # DB 캐시에서 운세 데이터 확인
        if request.user.is_authenticated:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            today = date.today()

            fortune_data = load_fortune_from_db(request.user, session_key, today)

            # 운세 데이터가 없으면 로딩 페이지로 리다이렉트
            if not fortune_data:
                return redirect('fortune:loading_auto')

        # 기존 로직 사용
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 로그인한 사용자만 날씨와 OOTD 정보 제공
        if self.request.user.is_authenticated:
            # 실제 날씨 정보 가져오기
            weather_data = self.get_weather_info()

            # 테스트용: ?test_temp=25 파라미터로 기온 오버라이드
            test_temp = self.request.GET.get('test_temp')
            if test_temp:
                try:
                    temp = float(test_temp)
                    weather_data['temp'] = temp
                    weather_data['temp_max'] = temp + 3
                    weather_data['temp_min'] = temp - 3
                    weather_data['description'] = f'테스트 모드 ({temp}°C)'
                except ValueError:
                    pass

            context['weather'] = weather_data

            # 행운색 가져오기 (3개)
            lucky_colors = get_lucky_colors_for_user(self.request)
            context['lucky_colors'] = lucky_colors  # 3개 리스트
            context['lucky_color'] = lucky_colors[0] if lucky_colors else None  # 첫 번째 (하위 호환)

            # OOTD 추천 로직 (날씨 + 행운색 기반)
            context['outfit'] = self.generate_ootd_recommendation(weather_data, lucky_colors)

        return context
    
    def get_weather_info(self):
        """실제 날씨 정보 가져오기 - 기본값: 대전 유성구"""
        # API 키 가져오기
        api_key = settings.WEATHER_API_KEY
        
        # 대전광역시 유성구 좌표
        lat = 36.3621  # 대전 유성구 위도
        lon = 127.3565  # 대전 유성구 경도
        city = "Daejeon, Yuseong-gu"
        
        try:
            # OpenWeatherMap API 호출
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
            response = requests.get(url)
            data = response.json()
            
            # 한글 주소 변환
            korean_address = get_korean_address(lat, lon)
            city_name = korean_address if korean_address else data.get('name', city)

            # API 응답 파싱
            weather_info = {
                'temp': round(data['main']['temp'], 1), # 현재 기온 추가
                'temp_max': round(data['main']['temp_max']),
                'temp_min': round(data['main']['temp_min']),
                'description': data['weather'][0]['description'],
                'rain_probability': 0,
                'is_cold': data['main']['temp'] < 10,
                'season': 'winter' if data['main']['temp'] < 10 else 'summer',
                'city': city_name,
                'lat': data['coord']['lat'],
                'lon': data['coord']['lon']
            }
            return weather_info
        except:
            # API 호출 실패 시 기본값 (대전 유성구)
            return {
                'temp_max': 10,
                'temp_min': 0,
                'description': '날씨 정보 없음',
                'rain_probability': 0,
                'is_cold': True,
                'season': 'winter',
                'city': '대전 유성구',
                'lat': lat,
                'lon': lon
            }
    
    def generate_ootd_recommendation(self, weather, lucky_colors=None):
        """날씨 + 행운색 기반 OOTD 추천 (ootd.json 활용)"""
        current_temp = weather.get('temp', (weather['temp_max'] + weather['temp_min']) / 2)

        # 날씨 상태 파싱
        description = weather.get('description', '맑음')
        if '비' in description or '소나기' in description:
            weather_condition = '비'
        elif '눈' in description:
            weather_condition = '눈'
        elif '흐' in description or '구름' in description:
            weather_condition = '흐림'
        else:
            weather_condition = '맑음'

        # 온도에 맞는 상의/하의/아우터 가져오기
        tops = get_clothes_by_temp_and_category(current_temp, '상의', weather_condition)
        bottoms = get_clothes_by_temp_and_category(current_temp, '하의', weather_condition)
        outers = get_clothes_by_temp_and_category(current_temp, '아우터', weather_condition)

        # 행운색 관련 색상 목록 (3개 행운색 각각 변환 후 병합)
        lucky_color_variants = []
        if lucky_colors:
            for lc in lucky_colors:
                variants = get_lucky_color_korean_to_ootd(lc)
                # 첫 번째 변형만 추가 (중복 방지)
                if variants and variants[0] not in lucky_color_variants:
                    lucky_color_variants.append(variants[0])

        # 상의 선택 (랜덤으로 1개)
        if tops:
            selected_top = random.choice(tops)
            top_name = selected_top.get('name', '니트')
            top_desc = selected_top.get('description', '따뜻하고 포근한 느낌')
        else:
            top_name = '니트'
            top_desc = '따뜻하고 포근한 느낌'

        # 하의 선택 (랜덤으로 1개)
        if bottoms:
            selected_bottom = random.choice(bottoms)
            bottom_name = selected_bottom.get('name', '청바지')
            bottom_desc = selected_bottom.get('description', '편안한 일상 바지')
        else:
            bottom_name = '청바지'
            bottom_desc = '편안한 일상 바지'

        # 아우터 선택
        outer_required = current_temp < 20
        if outers and outer_required:
            selected_outer = random.choice(outers)
            outer_name = selected_outer.get('name', '코트')
            outer_desc = selected_outer.get('description', '바람을 막아주는 아우터')
        else:
            outer_name = '불필요'
            outer_desc = ''
            outer_required = False

        # 행운색 기반 색상 추천
        if lucky_color_variants:
            # 상의: 첫 번째 행운색을 메인 색상으로
            top_color = lucky_color_variants[0]
            # 상의 대체 색상: 나머지 행운색들 (중복 제거)
            top_alt_colors = [c for c in lucky_color_variants[1:] if c != top_color]

            # 하의: 행운색과 어울리는 무채색/기본색 계열
            bottom_color = '블랙'
            bottom_alt_colors = ['네이비', '차콜']
        else:
            # 기본 색상 (온도 기반)
            if current_temp >= 23:
                top_color = '화이트'
                top_alt_colors = ['베이지', '스카이블루']
                bottom_color = '베이지'
                bottom_alt_colors = ['블랙', '카키']
            elif current_temp >= 15:
                top_color = '베이지'
                top_alt_colors = ['그레이', '네이비']
                bottom_color = '블랙'
                bottom_alt_colors = ['네이비', '진청']
            else:
                top_color = '그레이'
                top_alt_colors = ['블랙', '차콜']
                bottom_color = '블랙'
                bottom_alt_colors = ['네이비', '차콜']

        # 스타일 태그 생성
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

        # 액세서리 추천 (날씨 + 온도 기반)
        accessories = get_clothes_by_temp_and_category(current_temp, '액세서리', weather_condition)
        recommended_accessories = []

        # 액세서리 이모지 매핑
        accessory_emoji = {
            '머플러': '🧣',
            '장갑': '🧤',
            '비니': '🎿',
            '모자': '🧢',
            '우산': '☂️'
        }

        for acc in accessories:
            acc_name = acc.get('name', '')
            recommended_accessories.append({
                'name': acc_name,
                'description': acc.get('description', ''),
                'emoji': accessory_emoji.get(acc_name, '✨')
            })

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

    
def load_food_data():
    """food.json 파일 로드"""
    # food.json의 가능한 경로들
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'food.json'),
        os.path.join(settings.BASE_DIR, 'data', 'food.json'),
        os.path.join(settings.BASE_DIR, 'recommendations', 'data', 'food.json'),
        # 절대 경로로도 시도 (현재 작업 디렉토리 기준)
        os.path.abspath('food.json'),
    ]
    
    for json_path in possible_paths:
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # print(f"Successfully loaded food data from {json_path}") # 디버깅용
                    return data
            except Exception as e:
                print(f"JSON 로드 오류 ({json_path}): {e}")
    
    print("Warning: food.json not found in any expected location.")
    # 파일이 없으면 기존 하드코딩 데이터 사용
    return get_default_food_data()


def get_default_food_data():
    """기본 음식 데이터 (기존 하드코딩 데이터 활용)"""
    return [
        {"name_ko": "토마토 파스타", "color_category": "Red", "emoji": "🍝", "description": "활력을 높여주는 토마토가 운세를 상승시킵니다."},
        {"name_ko": "김치찌개", "color_category": "Red", "emoji": "🍲", "description": "매콤한 국물이 스트레스를 날려버립니다."},
        {"name_ko": "카레라이스", "color_category": "Yellow", "emoji": "🍛", "description": "따뜻한 카레가 금전운을 부릅니다."},
        {"name_ko": "샐러드", "color_category": "Green", "emoji": "🥗", "description": "신선한 야채로 만든 건강한 샐러드"},
        {"name_ko": "짜장면", "color_category": "Black", "emoji": "🍜", "description": "깊은 맛이 하루를 든든하게 합니다."},
    ]


def get_color_mapping():
    """한글 색상명 → food.json의 color_category 매핑 (확장됨)"""
    return {
        '노란색': ['yellow', 'gold', 'amber', 'pale yellow', 'yellow/gold', 'yellow/brown', 'yellow/red', 'yellow/clear', 'yellow/white', 'white/yellow'],
        '베이지색': ['beige', 'tan', 'cream', 'beige/green', 'beige/black', 'beige/red', 'white/beige'],
        '검은색': ['black', 'dark', 'black/dark brown', 'black/white', 'black/purple', 'black/gray', 'dark brown/black'],
        '빨간색': ['red', 'crimson', 'dark red', 'red/yellow', 'red/brown', 'red/purple', 'red/white', 'red/green', 'red/clear', 'pink/red'],
        '주황색': ['orange', 'coral', 'orange/brown', 'pink/orange', 'yellow/orange', 'brown/orange'],
        '초록색': ['green', 'lime', 'dark green', 'light green', 'green/white', 'green/brown', 'green/red', 'cyan/green', 'white/green', 'red/green'],
        '파란색': ['blue', 'navy', 'cyan', 'sky blue', 'pink/blue'],
        '보라색': ['purple', 'violet', 'dark red/brown', 'purple/brown', 'purple/red', 'purple/white', 'black/purple'],
        '흰색': ['white', 'ivory', 'cream', 'clear', 'milky white', 'white/brown', 'white/red', 'white/green', 'white/clear', 'clear/white', 'white/pink', 'gray/white'],
        '분홍색': ['pink', 'rose', 'pink/brown', 'pink/white', 'pink/gray'],
        '갈색': ['brown', 'chocolate', 'dark brown', 'light brown', 'golden brown', 'brown/silver', 'brown/pink', 'brown/yellow', 'brown/white', 'brown/green', 'gray/brown'],
        '회색': ['gray', 'grey', 'silver', 'black/gray', 'pink/gray', 'white/gray', 'clear/gray'],
        '금색': ['gold', 'golden', 'pale gold', 'clear/gold'],
    }


def get_food_by_color(lucky_color):
    """행운색에 맞는 음식 필터링 (개선됨)"""
    foods = load_food_data()
    color_mapping = get_color_mapping()
    
    # 행운색에 해당하는 영어 색상 키워드 목록
    target_keywords = color_mapping.get(lucky_color, [lucky_color.lower()])
    
    # 매칭되는 음식 필터링
    matching_foods = []
    for food in foods:
        food_color = food.get('color_category', '').lower()
        
        # 1. 정확한 매칭 또는 매핑된 키워드 포함 여부 확인
        is_match = False
        
        # 매핑된 키워드 중 하나라도 food_color에 포함되거나 일치하면 매칭
        for keyword in target_keywords:
            if keyword in food_color:
                is_match = True
                break
        
        # 2. 역방향 매칭 (food_color가 복합 색상일 경우, 예를 들어 'Red/Yellow'는 'Red'에도 매칭되어야 함)
        # 이미 위에서 처리됨 (keyword in food_color)
        
        if is_match:
            matching_foods.append(food)
            
    return matching_foods


def get_emoji_for_food(food):
    """음식별 이모지 반환 (food.json에서 직접 가져오기)"""
    # food.json에 icon 필드가 있으면 그대로 사용
    if 'icon' in food and food['icon']:
        return food['icon']

    # icon이 없으면 타입별 기본 이모지 사용
    type_emoji_map = {
        'Fruit': '🍎',
        'Vegetable': '🥬',
        'Dish': '🍲',
        'Beverage': '🥤',
        'Dessert': '🍰',
        'Seafood': '🦐',
        'Dairy': '🧀',
        'Grain': '🍚',
        'Ingredient': '🥘',
        'Vegetable/Fruit': '🍅'
    }
    food_type = food.get('type', '')
    return type_emoji_map.get(food_type, '🍽️')


def get_lucky_colors_for_user(request):
    """사용자의 오늘 행운색 가져오기 (3개 반환)"""
    from fortune.services import FortuneCalculator

    today_str = str(date.today())

    # 세션에서 운세 데이터 가져오기 (v2 버전 사용)
    fortune_data = request.session.get('fortune_data_v2')
    fortune_date = request.session.get('fortune_date_v2')

    # 운세 데이터가 없거나 날짜가 다르면 새로 계산
    if not fortune_data or fortune_date != today_str:
        if request.user.is_authenticated and request.user.birth_date:
            # 로그인 사용자: 자동 계산
            try:
                # 세션 키 확보
                if not request.session.session_key:
                    request.session.create()
                session_key = request.session.session_key

                calculator = FortuneCalculator()
                fortune_data = calculator.calculate_fortune(
                    birth_date=request.user.birth_date,
                    gender=request.user.gender,
                    birth_time=getattr(request.user, 'birth_time', None),
                    chinese_name=getattr(request.user, 'chinese_name', None),
                    calendar_type=getattr(request.user, 'calendar_type', 'solar'),
                    user_id=request.user.id,
                    session_key=session_key
                )
                # 세션에 저장
                request.session['fortune_data_v2'] = fortune_data
                request.session['fortune_date_v2'] = today_str
            except Exception as e:
                print(f"[OOTD] 운세 자동 계산 실패: {e}")
                return None
        else:
            # 비로그인 또는 생년월일 없음
            return None

    # 행운색 반환 (최대 3개)
    lucky_colors = fortune_data.get('lucky_colors', [])
    if isinstance(lucky_colors, list) and lucky_colors:
        return lucky_colors[:3]  # 상위 3개
    elif lucky_colors:
        return [lucky_colors]

    return None


def get_lucky_color_for_user(request):
    """사용자의 오늘 행운색 가져오기 (첫 번째만 - 하위 호환)"""
    colors = get_lucky_colors_for_user(request)
    return colors[0] if colors else None


@login_required(login_url='/users/login/')
def menu_recommendation(request):
    """
    오늘의 메뉴 추천 (함수 기반 뷰)
    DailyRecommendation 모델을 사용하여 일별 추천 결과를 캐싱
    """
    from .models import DailyRecommendation

    today = date.today()
    user = request.user if request.user.is_authenticated else None

    # 세션 키 확보
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # DB 캐시에서 운세 데이터 확인
    if request.user.is_authenticated:
        fortune_data = load_fortune_from_db(user, session_key, today)

        # 운세 데이터가 없으면 로딩 페이지로 리다이렉트
        if not fortune_data:
            return redirect('fortune:loading_auto')
    
    # 기존 추천 조회
    existing = DailyRecommendation.objects.filter(
        recommendation_date=today,
        recommendation_type='MENU'
    )
    
    if user:
        existing = existing.filter(user=user)
    else:
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        existing = existing.filter(session_key=session_key)
    
    if existing.exists():
        # DB에서 로드
        rec_data = existing.first().recommendation_data
        recommendations = rec_data['recommendations']
        other_recommendations = rec_data['other_recommendations']
        lucky_color = rec_data['lucky_color']
    else:
        # 새로운 추천 생성
        lucky_color = get_lucky_color_for_user(request)
        matching_foods = get_food_by_color(lucky_color)
        
        # 추천 음식 선택 (랜덤으로 2개)
        if len(matching_foods) >= 2:
            recommended_list = random.sample(matching_foods, 2)
        elif len(matching_foods) == 1:
            recommended_list = matching_foods
        else:
            all_foods = load_food_data()
            recommended_list = random.sample(all_foods, min(2, len(all_foods)))
        
        # 템플릿 형식에 맞게 변환
        recommendations = []
        for idx, food in enumerate(recommended_list, 1):
            desc = food.get('description', '')
            if not desc:
                name = food.get('name_ko', '이 음식')
                desc = f"행운의 {lucky_color} 에너지를 담은 {name}입니다."

            recommendations.append({
                'rank': idx,
                'color': lucky_color,
                'menu': {
                    'name': food.get('name_ko', ''),
                    'category': food.get('type', '기타'),
                    'icon': get_emoji_for_food(food),  # 타입별 이모지
                    'desc': desc
                },
                'bg_gradient': _get_gradient(lucky_color)
            })
        
        # 그 외 추천 메뉴
        all_foods = load_food_data()
        recommended_ids = [f.get('id') for f in recommended_list]
        other_foods = [f for f in all_foods if f.get('id') not in recommended_ids]
        
        if len(other_foods) >= 6:
            other_list = random.sample(other_foods, 6)
        else:
            other_list = other_foods
        
        other_recommendations = []
        for food in other_list:
            eng_color = food.get('color_category', '').split('/')[0].lower()
            kor_color = '기타'
            for k, v in get_color_mapping().items():
                if any(c in eng_color for c in v):
                    kor_color = k
                    break
                    
            other_recommendations.append({
                'color': kor_color,
                'menu': {
                    'name': food.get('name_ko', ''),
                    'category': food.get('type', '기타'),
                    'icon': get_emoji_for_food(food),  # 타입별 이모지
                    'desc': food.get('description', '')
                }
            })
        
        # DB에 저장
        DailyRecommendation.objects.create(
            user=user,
            session_key=session_key or '',
            recommendation_date=today,
            recommendation_type='MENU',
            recommendation_data={
                'recommendations': recommendations,
                'other_recommendations': other_recommendations,
                'lucky_color': lucky_color
            }
        )
    
    context = {
        'recommendations': recommendations,
        'other_recommendations': other_recommendations,
        'lucky_color': lucky_color,
        'date': today,
    }
    
    return render(request, 'recommendations/menu.html', context)


def _get_gradient(color):
    """색상별 그라디언트"""
    gradients = {
        '빨간색': 'linear-gradient(135deg, #ef4444, #f87171)',
        '주황색': 'linear-gradient(135deg, #f97316, #fb923c)',
        '노란색': 'linear-gradient(135deg, #eab308, #facc15)',
        '초록색': 'linear-gradient(135deg, #22c55e, #4ade80)',
        '파란색': 'linear-gradient(135deg, #3b82f6, #60a5fa)',
        '보라색': 'linear-gradient(135deg, #a855f7, #c084fc)',
        '검은색': 'linear-gradient(135deg, #1f2937, #4b5563)',
        '흰색': 'linear-gradient(135deg, #9ca3af, #d1d5db)',
        '갈색': 'linear-gradient(135deg, #78350f, #92400e)',
        '분홍색': 'linear-gradient(135deg, #ec4899, #f472b6)',
        '회색': 'linear-gradient(135deg, #6b7280, #9ca3af)',
        '금색': 'linear-gradient(135deg, #eab308, #fde047)',
        '베이지색': 'linear-gradient(135deg, #d6d3d1, #e7e5e4)',
    }
    return gradients.get(color, 'linear-gradient(135deg, #6366f1, #8b5cf6)')


class ItemRecommendationView(APIView):
    def get(self, request):
        return Response({"message": "Item recommendation endpoint"})

class FeedbackView(APIView):
    def post(self, request):
        return Response({"message": "Feedback endpoint"})

class WeatherLocationView(APIView):
    """위치 기반 날씨 정보 API - 시간별 예보 포함"""

    def post(self, request):
        from datetime import datetime, timedelta
        lat = request.data.get('lat')
        lon = request.data.get('lon')

        if not lat or not lon:
            # 기본값: 대전 유성구
            lat = 36.3621
            lon = 127.3565

        # 한글 주소 가져오기 (카카오 API)
        korean_address = get_korean_address(lat, lon)

        # OpenWeatherMap API 호출
        api_key = settings.WEATHER_API_KEY

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code != 200:
                raise Exception(data.get('message', 'API Error'))

            # 현재 날씨
            current_weather = {
                'temp': round(data['main']['temp'], 1),
                'temp_max': round(data['main']['temp_max']),
                'temp_min': round(data['main']['temp_min']),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
            
            # 시간별 예보 (5일/3시간 간격) -> 1시간 간격으로 보간
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
            forecast_response = requests.get(forecast_url)
            
            hourly_forecast = []
            daily_temps = [] # 하루(24시간) 동안의 기온을 모아서 최저/최고 계산

            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                items = forecast_data['list']
                
                # 현재 시간부터 24시간 데이터 생성
                current_time = datetime.now()
                
                # 3시간 간격 데이터를 순회하며 1시간 간격으로 보간
                # 12시간 데이터만 필요하므로 범위를 줄임 (약 4-5개 구간이면 충분)
                for i in range(min(5, len(items) - 1)): 
                    item_curr = items[i]
                    item_next = items[i+1]
                    
                    t_curr = item_curr['main']['temp']
                    t_next = item_next['main']['temp']
                    
                    pop_curr = int(item_curr.get('pop', 0) * 100)
                    pop_next = int(item_next.get('pop', 0) * 100)
                    
                    rain_curr = item_curr.get('rain', {}).get('3h', 0)
                    rain_next = item_next.get('rain', {}).get('3h', 0)
                    
                    # 3시간 구간을 1시간 단위로 쪼개기 (0, 1, 2)
                    for hour_offset in range(3):
                        # 선형 보간 (Linear Interpolation)
                        ratio = hour_offset / 3.0
                        interp_temp = t_curr + (t_next - t_curr) * ratio
                        interp_pop = int(pop_curr + (pop_next - pop_curr) * ratio)
                        # 강수량은 3시간 누적이므로 1/3로 나눔 (단순화)
                        interp_rain = (rain_curr * (1-ratio) + rain_next * ratio) / 3.0
                        
                        target_time = datetime.fromtimestamp(item_curr['dt']) + timedelta(hours=hour_offset)
                        
                        # 현재 시간보다 이전 데이터는 스킵 (단, 첫 번째 구간은 포함될 수 있음)
                        if target_time < current_time - timedelta(minutes=30) and i > 0:
                            continue
                            
                        hourly_forecast.append({
                            'time': target_time.strftime('%H:%M'),
                            'temp': round(interp_temp, 1),
                            'weather': item_curr['weather'][0]['description'], # 날씨 상태는 현재 구간 따라감
                            'icon': item_curr['weather'][0]['icon'],
                            'rain_probability': interp_pop,
                            'rain_amount': round(interp_rain, 1)
                        })
                        daily_temps.append(interp_temp)
                        
                        if len(hourly_forecast) >= 12: # 12시간 데이터만 확보
                            break
                    if len(hourly_forecast) >= 12:
                        break
            
            # 예보 데이터 기반으로 최저/최고 기온 재설정 (현재 API의 min/max는 현재 시점의 지역 min/max라 하루 전체와 다를 수 있음)
            if daily_temps:
                current_weather['temp_max'] = round(max(daily_temps))
                current_weather['temp_min'] = round(min(daily_temps))

            # 한글 주소가 있으면 사용, 없으면 OpenWeatherMap 도시명 사용
            city_name = korean_address if korean_address else data.get('name', '위치 정보 없음')

            return Response({
                'success': True,
                'current': current_weather,
                'hourly': hourly_forecast,
                'temp': current_weather['temp'],
                'temp_max': current_weather['temp_max'],
                'temp_min': current_weather['temp_min'],
                'description': current_weather['description'],
                'city': city_name,
                'korean_address': korean_address  # 디버깅용
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'city': '대전 유성구'
            })
