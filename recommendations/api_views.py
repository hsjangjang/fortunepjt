from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import date
from django.conf import settings
from django.core.cache import cache
import random
import json
import os
from .models import DailyRecommendation
from .weather_service import get_weather_info
from fortune.constants import (
    get_lucky_color_to_ootd,
    get_food_color_keywords,
    get_korean_color,
    get_color_gradient,
    PERSONAL_COLOR_PALETTES,
    PERSONAL_COLOR_AVOID,
)
from config.weather_config import DEFAULT_LOCATION


def summarize_fortune_with_llm(total_text: str, zodiac_sign: str, user_id: int = None) -> str:
    """GMS GPT-5-nano를 사용해 종합운을 한 문장으로 요약"""
    if not total_text:
        print("[Fortune Summary] Empty total_text received")
        return ''

    # 캐시 키 생성 (오늘 날짜 + 별자리 + 유저ID 기반)
    cache_key = f"fortune_summary_v2_{zodiac_sign}_{user_id}_{date.today()}"
    cached_result = cache.get(cache_key)
    if cached_result:
        print(f"[Fortune Summary] Using cached result: {cached_result}")
        return cached_result

    # GMS API 설정 (OpenAI 모델용 URL 사용)
    gms_api_key = getattr(settings, 'GMS_API_KEY', '')
    gms_api_base = getattr(settings, 'GMS_OPENAI_BASE_URL', 'https://gms.ssafy.io/gmsapi/api.openai.com/v1')

    print(f"[Fortune Summary] GMS API Key exists: {bool(gms_api_key)}, Base URL: {gms_api_base}")

    if not gms_api_key:
        print("[Fortune Summary] No GMS API key, using fallback")
        return total_text.split('.')[0] + '.' if total_text else ''

    try:
        from openai import OpenAI
        client = OpenAI(api_key=gms_api_key, base_url=gms_api_base)

        prompt = f"""다음 오늘의 종합운세 텍스트를 읽고, 핵심 키워드를 뽑아서 **한 문장(30자 이내)**으로 요약해주세요.

종합운세:
{total_text}

요구사항:
- 오늘 하루의 핵심 메시지를 담은 짧은 한 문장
- "~할 것입니다", "~좋습니다" 같은 운세 말투 사용
- 구체적인 행동 조언이나 주의사항 포함
- 별자리 이름 언급하지 않기
- 30자 이내로 작성

예시:
- "적극적인 행동이 좋은 결과로 이어질 것입니다"
- "주변의 조언에 귀 기울이면 기회가 찾아옵니다"
- "차분한 마음으로 중요한 결정을 내리세요"

한 문장만 출력하세요:"""

        print(f"[Fortune Summary] Calling GMS API with gpt-5-nano...")
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=100
        )
        summary = response.choices[0].message.content.strip().strip('"').strip("'")
        print(f"[Fortune Summary] GMS API success: {summary}")

        # 캐시에 저장 (24시간)
        cache.set(cache_key, summary, 60 * 60 * 24)

        return summary
    except Exception as e:
        print(f"[Fortune Summary LLM Error] {e}")
        import traceback
        traceback.print_exc()
        # 실패 시 첫 문장 반환
        fallback = total_text.split('.')[0] + '.' if total_text else ''
        print(f"[Fortune Summary] Using fallback: {fallback}")
        return fallback


def load_ootd_data(gender=None):
    """ootd.json 파일 로드 (성별에 따라 다른 파일)"""
    # 성별에 따른 파일 선택
    if gender == 'M':
        filenames = ['ootd_male.json', 'ootd.json']
    elif gender == 'F':
        filenames = ['ootd_female.json', 'ootd.json']
    else:
        filenames = ['ootd.json']

    for filename in filenames:
        possible_paths = [
            os.path.join(settings.BASE_DIR, filename),
            os.path.join(settings.BASE_DIR, 'data', filename),
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


def get_clothes_by_temp_and_category(temp, category, weather_condition="맑음", gender=None):
    """온도와 카테고리에 맞는 옷 필터링 (성별 반영)"""
    ootd_data = load_ootd_data(gender)
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


# get_lucky_color_korean_to_ootd -> fortune.constants.get_lucky_color_to_ootd로 대체


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
        mbti=getattr(user, 'mbti', None),
        personal_color=getattr(user, 'personal_color', None),
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
        lat = float(request.query_params.get('lat', DEFAULT_LOCATION['lat']))
        lon = float(request.query_params.get('lon', DEFAULT_LOCATION['lon']))
        weather_data = get_weather_info(lat, lon)

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

        # 운세 요약 (한줄)
        fortune_summary = fortune_data.get('overall_fortune', {}).get('summary', '')

        # 오늘 날짜로 기존 추천이 있는지 확인
        today = date.today()
        existing_recommendation = DailyRecommendation.objects.filter(
            user=request.user,
            recommendation_date=today,
            recommendation_type='OOTD'
        ).first()

        # 사용자 성별 및 퍼스널 컬러 가져오기
        user_gender = getattr(request.user, 'gender', None)
        user_personal_color = getattr(request.user, 'personal_color', None)

        if existing_recommendation:
            # 기존 추천이 있으면 DB에서 가져오기
            outfit = existing_recommendation.recommendation_data
        else:
            # 새로 생성하고 DB에 저장 (성별, 퍼스널 컬러 반영)
            outfit = self._generate_ootd(weather_data, lucky_colors, user_gender, user_personal_color)
            DailyRecommendation.objects.create(
                user=request.user,
                recommendation_date=today,
                recommendation_type='OOTD',
                recommendation_data=outfit,
                weather_data=weather_data
            )

        return Response({
            'success': True,
            'weather': weather_data,
            'lucky_colors': lucky_colors,
            'fortune_summary': fortune_summary,
            'outfit': outfit,
            'date': str(today)
        })

    def _generate_ootd(self, weather, lucky_colors, gender=None, personal_color=None):
        """OOTD 추천 생성 (성별, 퍼스널 컬러 반영)"""
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

        # 온도에 맞는 옷 가져오기 (성별 반영)
        tops = get_clothes_by_temp_and_category(current_temp, '상의', weather_condition, gender)
        bottoms = get_clothes_by_temp_and_category(current_temp, '하의', weather_condition, gender)
        outers = get_clothes_by_temp_and_category(current_temp, '아우터', weather_condition, gender)
        accessories = get_clothes_by_temp_and_category(current_temp, '액세서리', weather_condition, gender)

        # 퍼스널 컬러에 맞는 색상 팔레트 가져오기
        personal_color_palette = []
        avoid_colors = []
        if personal_color:
            personal_color_palette = PERSONAL_COLOR_PALETTES.get(personal_color, [])
            avoid_colors = PERSONAL_COLOR_AVOID.get(personal_color, [])

        # 행운색 변환 (퍼스널 컬러 필터링 적용)
        lucky_color_variants = []
        if lucky_colors:
            for lc in lucky_colors:
                # 퍼스널 컬러가 있으면 피해야 할 색상 제외
                if personal_color and lc in avoid_colors:
                    continue

                variants = get_lucky_color_to_ootd(lc)
                if variants and variants[0] not in lucky_color_variants:
                    lucky_color_variants.append(variants[0])

        # 퍼스널 컬러가 있는데 행운색이 모두 필터링된 경우, 퍼스널 컬러 팔레트에서 선택
        if personal_color and not lucky_color_variants and personal_color_palette:
            for palette_color in personal_color_palette[:3]:
                variants = get_lucky_color_to_ootd(palette_color)
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

        lucky_colors = fortune_data.get('lucky_colors', [])[:3]
        zodiac_sign = fortune_data.get('zodiac_sign', '')

        # fortune_texts에서 종합운(total) 가져오기
        fortune_texts = fortune_data.get('fortune_texts', {})
        total_text = fortune_texts.get('total', '')
        # LLM으로 종합운 한줄 요약 생성 (유저ID 포함하여 캐시 분리)
        fortune_summary = summarize_fortune_with_llm(total_text, zodiac_sign, request.user.id)

        # 오늘 날짜로 기존 추천이 있는지 확인
        today = date.today()
        existing_recommendation = DailyRecommendation.objects.filter(
            user=request.user,
            recommendation_date=today,
            recommendation_type='MENU'
        ).first()

        if existing_recommendation:
            # 기존 추천이 있으면 DB에서 가져오기
            saved_data = existing_recommendation.recommendation_data
            recommendations = saved_data.get('recommendations', [])
            other_recommendations = saved_data.get('other_recommendations', [])
        else:
            # 새로 생성
            all_foods = load_food_data()

            # 3개 행운색 모두 고려하여 음식 찾기
            matching_foods = []
            for lucky_color in lucky_colors:
                color_foods = self._get_food_by_color(lucky_color, all_foods)
                for food in color_foods:
                    if food not in matching_foods:
                        matching_foods.append(food)

            # 추천 음식 선택 (최소 2개)
            if len(matching_foods) >= 2:
                # 행운색 음식이 2개 이상이면 그 중에서 2개 선택
                recommended_list = random.sample(matching_foods, 2)
            else:
                # 행운색 음식이 부족하면 전체에서 2개 선택
                recommended_list = random.sample(all_foods, min(2, len(all_foods)))

            # 추천 형식화
            recommendations = []
            for idx, food in enumerate(recommended_list, 1):
                food_color = self._get_korean_color(food.get('color_category', ''))
                # 순환하며 행운색 3개 모두 사용
                lucky_color_idx = (idx - 1) % len(lucky_colors) if lucky_colors else 0
                lucky_color = lucky_colors[lucky_color_idx] if lucky_colors else '노란색'

                recommendations.append({
                    'rank': idx,
                    'color': food_color,
                    'menu': {
                        'name': food.get('name_ko', ''),
                        'category': food.get('type', '기타'),
                        'icon': self._get_emoji_for_food(food),
                        'desc': food.get('desc', f"행운의 색상 에너지를 담은 음식입니다.")
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

            # DB에 저장
            DailyRecommendation.objects.create(
                user=request.user,
                recommendation_date=today,
                recommendation_type='MENU',
                recommendation_data={
                    'recommendations': recommendations,
                    'other_recommendations': other_recommendations
                }
            )

        return Response({
            'success': True,
            'lucky_colors': lucky_colors,
            'recommendations': recommendations,
            'other_recommendations': other_recommendations,
            'fortune_data': {
                'lucky_colors': lucky_colors,
                'fortune_summary': fortune_summary,
            },
            'date': str(today)
        })

    def _get_food_by_color(self, lucky_color, foods):
        """행운색에 맞는 음식 필터링"""
        target_keywords = get_food_color_keywords(lucky_color)
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
        return get_korean_color(eng_color)

    def _get_gradient_for_color(self, color):
        """색상별 그라데이션 배경"""
        return get_color_gradient(color)


class WeatherAPIView(APIView):
    """날씨 정보 API - 기상청 API 사용"""
    permission_classes = [AllowAny]

    def get(self, request):
        lat = float(request.query_params.get('lat', DEFAULT_LOCATION['lat']))
        lon = float(request.query_params.get('lon', DEFAULT_LOCATION['lon']))

        weather_data = get_weather_info(lat, lon)

        # weather_service의 응답을 WeatherAPIView 형식으로 변환
        current_weather = {
            'temp': weather_data.get('temp'),
            'temp_max': weather_data.get('temp_max'),
            'temp_min': weather_data.get('temp_min'),
            'description': weather_data.get('description'),
            'humidity': weather_data.get('humidity'),
            'wind_speed': weather_data.get('current', {}).get('wind_speed', 0),
            'icon': weather_data.get('icon', '☁️'),
            'rain_probability': weather_data.get('current', {}).get('rain_probability', 0),
            'rain_amount': weather_data.get('current', {}).get('rain_amount', 0)
        }

        return Response({
            'success': True,
            'current': current_weather,
            'hourly': weather_data.get('hourly', []),
            'city': weather_data.get('city', DEFAULT_LOCATION['city'])
        })

    def post(self, request):
        """위치 기반 날씨 (POST로 좌표 전송)"""
        lat = request.data.get('lat', DEFAULT_LOCATION['lat'])
        lon = request.data.get('lon', DEFAULT_LOCATION['lon'])
        request.query_params._mutable = True
        request.query_params['lat'] = lat
        request.query_params['lon'] = lon
        return self.get(request)
