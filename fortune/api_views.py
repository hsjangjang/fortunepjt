from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import date, datetime
from .services import FortuneCalculator
from .serializers import FortuneCalculateSerializer
from .models import DailyFortuneCache
from .cache_manager import FortuneCacheManager
import json


# ============================================================
# 캐시 함수 래퍼 (FortuneCacheManager 사용)
# ============================================================

def get_current_week():
    return FortuneCacheManager.get_current_week()


def get_current_month():
    return FortuneCacheManager.get_current_month()


def save_period_fortune_to_db(period_type, user, session_key, year, period_value, fortune_data, birth_date=None, gender=''):
    return FortuneCacheManager.save_period_fortune(period_type, user, session_key, year, period_value, fortune_data, birth_date, gender)


def find_same_condition_period_fortune(period_type, year, period_value, birth_date, gender=''):
    return FortuneCacheManager.find_same_condition_period(period_type, year, period_value, birth_date, gender)


def load_period_fortune_from_db(period_type, user, session_key, year, period_value):
    return FortuneCacheManager.load_period_fortune(period_type, user, session_key, year, period_value)


def save_fortune_to_db(user, session_key, fortune_date, fortune_data, birth_date=None, birth_time='', calendar_type='solar', chinese_name=''):
    return FortuneCacheManager.save_daily_fortune(user, session_key, fortune_date, fortune_data, birth_date, birth_time, calendar_type, chinese_name)


def find_same_condition_fortune(fortune_date, birth_date, birth_time='', calendar_type='solar', chinese_name=''):
    return FortuneCacheManager.find_same_condition_daily(fortune_date, birth_date, birth_time, calendar_type, chinese_name)


def load_fortune_from_db(user, session_key, fortune_date):
    """데이터베이스에서 운세 데이터 로드 (건강운 추가 로직 포함)"""
    fortune_data = FortuneCacheManager.load_daily_fortune(user, session_key, fortune_date)
    if fortune_data:
        # 건강운이 없는 기존 데이터에 건강운 추가
        cache = None
        if user and user.is_authenticated:
            cache = DailyFortuneCache.objects.filter(user=user, fortune_date=fortune_date).first()
        elif session_key:
            cache = DailyFortuneCache.objects.filter(session_key=session_key, fortune_date=fortune_date).first()
        fortune_data = add_health_fortune_if_missing(fortune_data, cache)
    return fortune_data


def add_health_fortune_if_missing(fortune_data, cache=None):
    """기존 운세 데이터에 건강운이 없으면 추가"""
    import random

    fortune_scores = fortune_data.get('fortune_scores', {})
    fortune_texts = fortune_data.get('fortune_texts', {})

    # 이미 건강운이 있으면 그대로 반환
    if 'health' in fortune_scores and 'health' in fortune_texts:
        return fortune_data

    print("[DB Cache] 건강운 없음 - 추가 생성")

    # 건강운 점수 생성 (기존 점수들의 평균 기반)
    existing_scores = [v for k, v in fortune_scores.items() if k != 'total' and isinstance(v, (int, float))]
    if existing_scores:
        base = int(sum(existing_scores) / len(existing_scores))
    else:
        base = 70

    health_score = max(50, min(100, base + random.randint(-10, 10)))
    fortune_scores['health'] = health_score

    # 총운 점수 재계산 (5개 운세 평균)
    sub_scores = [fortune_scores.get(k, 70) for k in ['money', 'love', 'study', 'work', 'health']]
    fortune_scores['total'] = round(sum(sub_scores) / 5)
    fortune_data['fortune_score'] = fortune_scores['total']

    # 건강운 텍스트 생성
    if health_score >= 80:
        fortune_texts['health'] = (
            "건강운이 매우 좋은 날입니다. 몸과 마음 모두 활력이 넘치며 평소보다 에너지가 넘칠 것입니다. "
            "운동을 시작하거나 새로운 건강 습관을 들이기에 최적의 시기입니다. "
            "오전에 가벼운 스트레칭이나 조깅을 하면 하루 종일 상쾌한 기분을 유지할 수 있습니다. "
            "면역력도 좋은 상태이니 평소 미뤄왔던 야외 활동이나 스포츠를 즐겨보세요. "
            "충분한 수분 섭취와 균형 잡힌 식사를 병행하면 건강이 더욱 좋아질 것입니다. "
            "오늘의 좋은 컨디션을 유지하기 위해 규칙적인 생활 패턴을 이어가세요."
        )
    elif health_score >= 60:
        fortune_texts['health'] = (
            "건강운이 안정적인 날입니다. 큰 문제는 없지만 자기 관리에 신경 쓰면 더 좋아질 수 있습니다. "
            "규칙적인 식사와 적당한 운동이 건강 유지의 핵심이 될 것입니다. "
            "장시간 앉아있는 것은 피하고, 틈틈이 스트레칭을 해주는 것이 좋습니다. "
            "카페인이나 자극적인 음식은 자제하고, 따뜻한 차나 물을 자주 마시세요. "
            "피로가 쌓이지 않도록 충분한 수면을 취하고, 스트레스 관리에도 신경 쓰세요. "
            "오늘은 무리하지 않고 자신의 페이스를 유지하는 것이 중요합니다."
        )
    else:
        fortune_texts['health'] = (
            "건강 관리에 특별히 주의가 필요한 날입니다. 무리한 활동은 피하고 충분한 휴식을 취하세요. "
            "면역력이 다소 떨어져 있을 수 있으니 손 씻기와 개인 위생에 신경 써주세요. "
            "소화가 잘 안 될 수 있으니 기름진 음식보다는 담백하고 따뜻한 음식을 선택하세요. "
            "두통이나 피로감이 느껴진다면 잠시 눈을 감고 휴식을 취하는 것이 좋습니다. "
            "격한 운동보다는 가벼운 산책이나 요가 같은 저강도 활동이 적합합니다. "
            "오늘은 몸의 신호에 귀 기울이고, 자신을 돌보는 시간을 가져보세요."
        )

    fortune_data['fortune_scores'] = fortune_scores
    fortune_data['fortune_texts'] = fortune_texts

    # DB 캐시 업데이트 (건강운이 추가된 데이터로)
    if cache:
        try:
            cache.full_fortune_data = json.dumps(fortune_data, ensure_ascii=False)
            cache.fortune_score = fortune_scores['total']
            cache.save()
            print("[DB Cache] 건강운 추가 후 DB 업데이트 완료")
        except Exception as e:
            print(f"[DB Cache] 건강운 DB 업데이트 실패: {e}")

    return fortune_data


class FortuneCalculateAPIView(APIView):
    """운세 계산 API (비로그인도 가능)"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FortuneCalculateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': '유효하지 않은 데이터입니다', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            today = date.today()

            # 세션 키 확보
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            user = request.user if request.user.is_authenticated else None
            user_id = user.id if user else None

            # 입력 값 추출
            birth_date = serializer.validated_data['birth_date']
            birth_time = serializer.validated_data.get('birth_time') or ''
            chinese_name = serializer.validated_data.get('chinese_name') or ''
            calendar_type = serializer.validated_data.get('calendar_type', 'solar')

            # 1. 본인 캐시 확인 (user/session 기반)
            fortune_data = load_fortune_from_db(user, session_key, today)

            if not fortune_data:
                # 2. 동일 조건 캐시 확인 (생년월일+시간+이름+날짜)
                fortune_data = find_same_condition_fortune(
                    today, birth_date, birth_time, calendar_type, chinese_name
                )

            if not fortune_data:
                # 3. 캐시 미스 - 새로 계산
                calculator = FortuneCalculator()
                fortune_data = calculator.calculate_fortune(
                    birth_date=birth_date,
                    gender=serializer.validated_data['gender'],
                    birth_time=birth_time,
                    chinese_name=chinese_name,
                    mbti=serializer.validated_data.get('mbti'),
                    personal_color=serializer.validated_data.get('personal_color'),
                    calendar_type=calendar_type,
                    user_id=user_id,
                    session_key=session_key
                )

            # DB에 저장 (본인 캐시 생성/갱신)
            save_fortune_to_db(
                user, session_key, today, fortune_data,
                birth_date=birth_date, birth_time=birth_time,
                calendar_type=calendar_type, chinese_name=chinese_name
            )

            # 세션에도 저장 (Django 템플릿 호환성)
            request.session['fortune_data_v2'] = fortune_data
            request.session['fortune_date_v2'] = str(today)

            return Response({
                'success': True,
                'fortune': fortune_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'success': False, 'error': f'운세 계산 중 오류가 발생했습니다: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TodayFortuneAPIView(APIView):
    """
    오늘의 운세 조회 API
    - 캐시 확인만 수행, 없으면 need_calculate 반환
    - 실제 계산은 FortuneCalculateAPIView 또는 GenerateFortuneAPIView에서 수행
    """
    permission_classes = [AllowAny]

    def get(self, request):
        today = date.today()
        today_str = str(today)

        # 로그인 사용자: DB 캐시 확인
        if request.user.is_authenticated:
            if not request.user.birth_date:
                return Response({
                    'success': False,
                    'error': '생년월일 정보가 없습니다. 프로필을 업데이트해주세요.',
                    'need_profile': True
                }, status=status.HTTP_400_BAD_REQUEST)

            # 세션 키 확보
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            # DB 캐시 확인만 (계산 안함)
            fortune_data = load_fortune_from_db(request.user, session_key, today)

            # 캐시 미스 - 계산 필요 응답
            if not fortune_data:
                print(f"[API] DB 캐시 미스 - 계산 필요 (사용자: {request.user.username})")
                return Response({
                    'success': False,
                    'need_calculate': True,
                    'message': '오늘의 운세가 아직 생성되지 않았습니다.'
                }, status=status.HTTP_200_OK)

            # 세션에도 저장 (Django 템플릿 호환성)
            request.session['fortune_data_v2'] = fortune_data
            request.session['fortune_date_v2'] = today_str

            return Response({
                'success': True,
                'fortune': fortune_data,
                'date': today_str
            }, status=status.HTTP_200_OK)

        # 비로그인: 세션 기반 캐시 확인
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        # DB 캐시 확인 (비로그인 사용자는 세션 키로 조회)
        fortune_data = load_fortune_from_db(None, session_key, today)

        if not fortune_data:
            # 비로그인 사용자는 계산 페이지로 가야 함
            return Response({
                'success': False,
                'need_calculate': True,
                'message': '운세 계산이 필요합니다.'
            }, status=status.HTTP_200_OK)

        return Response({
            'success': True,
            'fortune': fortune_data,
            'date': today_str
        }, status=status.HTTP_200_OK)


class GenerateFortuneAPIView(APIView):
    """로그인 사용자 운세 생성 API (로딩 페이지에서 호출)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        today = date.today()
        today_str = str(today)

        if not request.user.birth_date:
            return Response({
                'success': False,
                'error': '생년월일 정보가 없습니다. 프로필을 업데이트해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 세션 키 확보
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        # 사용자 정보 추출
        birth_date = request.user.birth_date
        birth_time = getattr(request.user, 'birth_time', None) or ''
        chinese_name = getattr(request.user, 'chinese_name', None) or ''
        calendar_type = getattr(request.user, 'calendar_type', 'solar')

        # 1. 동일 조건 캐시 확인 (생년월일+시간+이름+날짜)
        fortune_data = find_same_condition_fortune(
            today, birth_date, birth_time, calendar_type, chinese_name
        )

        if not fortune_data:
            # 2. 캐시 미스 - 새로 계산
            print(f"[API] 운세 생성 시작 (사용자: {request.user.username})")
            calculator = FortuneCalculator()
            fortune_data = calculator.calculate_fortune(
                birth_date=birth_date,
                gender=request.user.gender,
                birth_time=birth_time,
                chinese_name=chinese_name,
                mbti=getattr(request.user, 'mbti', None),
                personal_color=getattr(request.user, 'personal_color', None),
                calendar_type=calendar_type,
                user_id=request.user.id,
                session_key=session_key
            )
        else:
            print(f"[API] 동일 조건 캐시 사용 (사용자: {request.user.username})")

        # DB에 저장 (본인 캐시 생성/갱신)
        save_fortune_to_db(
            request.user, session_key, today, fortune_data,
            birth_date=birth_date, birth_time=birth_time,
            calendar_type=calendar_type, chinese_name=chinese_name
        )

        # 세션에도 저장 (Django 템플릿 호환성)
        request.session['fortune_data_v2'] = fortune_data
        request.session['fortune_date_v2'] = today_str

        print(f"[API] 운세 생성 완료 (사용자: {request.user.username})")

        return Response({
            'success': True,
            'fortune': fortune_data,
            'date': today_str
        }, status=status.HTTP_200_OK)


class ItemCheckAPIView(APIView):
    """아이템 행운도 측정 API (로그인 필수)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today_str = str(date.today())

        # 운세 계산
        if not request.user.birth_date:
            return Response({
                'success': False,
                'error': '생년월일 정보가 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        calculator = FortuneCalculator()
        fortune_data = calculator.calculate_fortune(
            birth_date=request.user.birth_date,
            gender=request.user.gender,
            birth_time=getattr(request.user, 'birth_time', None),
            chinese_name=getattr(request.user, 'chinese_name', None),
            mbti=getattr(request.user, 'mbti', None),
            personal_color=getattr(request.user, 'personal_color', None),
            user_id=request.user.id,
            session_key=None
        )

        # 사용자 아이템 목록 가져오기
        from items.models import UserItem
        user_items_qs = UserItem.objects.filter(user=request.user).order_by('-created_at')
        user_items = [
            {
                'id': item.id,
                'name': item.item_name,
                'image_url': item.image_full_url,
                'dominant_colors': item.dominant_colors or [],
                'created_at': item.created_at.isoformat()
            }
            for item in user_items_qs
        ]

        return Response({
            'success': True,
            'fortune': fortune_data,
            'user_items': user_items
        }, status=status.HTTP_200_OK)


# ============================================================
# 기간별 운세 API 베이스 클래스
# ============================================================

class BasePeriodFortuneAPIView(APIView):
    """주간/월간 운세 공통 베이스 클래스"""
    permission_classes = [AllowAny]
    period_type = None  # 'weekly' 또는 'monthly' - 서브클래스에서 설정

    def _get_period_info(self):
        """현재 기간 정보 반환 - 서브클래스에서 구현"""
        raise NotImplementedError

    def _get_period_response_key(self):
        """응답에 포함할 기간 키 (week 또는 month)"""
        return 'week' if self.period_type == 'weekly' else 'month'

    def _get_period_label(self, year, period_value):
        """기간 라벨 생성"""
        if self.period_type == 'weekly':
            return f'{year}년 {period_value}주차'
        return f'{year}년 {period_value}월'

    def _get_message(self):
        """캐시 없음 메시지"""
        if self.period_type == 'weekly':
            return '이 주의 운세가 아직 생성되지 않았습니다.'
        return '이 달의 운세가 아직 생성되지 않았습니다.'

    def _ensure_session(self, request):
        """세션 키 확보"""
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    def _extract_user_info(self, request):
        """사용자 정보 추출 (로그인/비로그인 공통)"""
        user = request.user if request.user.is_authenticated else None

        if user and user.is_authenticated:
            if not user.birth_date:
                return None, None, {'error': '생년월일 정보가 없습니다.'}
            return user, {
                'birth_date': user.birth_date,
                'gender': user.gender,
                'birth_time': getattr(user, 'birth_time', None),
                'chinese_name': getattr(user, 'chinese_name', None),
                'mbti': getattr(user, 'mbti', None),
                'personal_color': getattr(user, 'personal_color', None)
            }, None

        # 비로그인 사용자
        birth_date = request.data.get('birth_date')
        gender = request.data.get('gender')

        if not birth_date or not gender:
            return None, None, {'error': '생년월일과 성별 정보가 필요합니다.'}

        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()

        return None, {
            'birth_date': birth_date,
            'gender': gender,
            'birth_time': request.data.get('birth_time'),
            'chinese_name': request.data.get('chinese_name'),
            'mbti': request.data.get('mbti'),
            'personal_color': request.data.get('personal_color')
        }, None

    def get(self, request):
        year, period_value = self._get_period_info()
        session_key = self._ensure_session(request)
        user = request.user if request.user.is_authenticated else None
        period_key = self._get_period_response_key()

        # 로그인 사용자 생년월일 체크
        if user and not user.birth_date:
            return Response({
                'success': False,
                'error': '생년월일 정보가 없습니다.',
                'need_profile': True
            }, status=status.HTTP_400_BAD_REQUEST)

        # DB 캐시 확인
        fortune_data = load_period_fortune_from_db(self.period_type, user, session_key, year, period_value)

        if fortune_data:
            return Response({
                'success': True,
                'fortune': fortune_data,
                'period_type': self.period_type,
                'year': year,
                period_key: period_value
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'need_calculate': True,
            'message': self._get_message(),
            'period_type': self.period_type,
            'year': year,
            period_key: period_value
        }, status=status.HTTP_200_OK)

    def post(self, request):
        year, period_value = self._get_period_info()
        session_key = self._ensure_session(request)
        period_key = self._get_period_response_key()

        user, user_info, error = self._extract_user_info(request)
        if error:
            return Response({'success': False, **error}, status=status.HTTP_400_BAD_REQUEST)

        birth_date = user_info['birth_date']
        gender = user_info['gender']

        # 1. 본인 캐시 확인
        fortune_data = load_period_fortune_from_db(self.period_type, user, session_key, year, period_value)

        if not fortune_data:
            # 2. 동일 조건 캐시 확인
            fortune_data = find_same_condition_period_fortune(self.period_type, year, period_value, birth_date, gender)

        if not fortune_data:
            # 3. 새로 생성
            calculator = FortuneCalculator()
            fortune_data = calculator.calculate_fortune(
                birth_date=birth_date,
                gender=gender,
                birth_time=user_info['birth_time'],
                chinese_name=user_info['chinese_name'],
                mbti=user_info['mbti'],
                personal_color=user_info['personal_color'],
                user_id=user.id if user else None,
                session_key=session_key,
                fortune_seed=f"{self.period_type}_{year}_{period_value}",
                period_type=self.period_type
            )
            fortune_data['period_type'] = self.period_type
            fortune_data['period_label'] = self._get_period_label(year, period_value)

        # DB에 저장
        save_period_fortune_to_db(self.period_type, user, session_key, year, period_value, fortune_data, birth_date, gender)

        return Response({
            'success': True,
            'fortune': fortune_data,
            'period_type': self.period_type,
            'year': year,
            period_key: period_value
        }, status=status.HTTP_200_OK)


class WeeklyFortuneAPIView(BasePeriodFortuneAPIView):
    """이 주의 운세 조회/생성 API"""
    period_type = 'weekly'

    def _get_period_info(self):
        return get_current_week()


class MonthlyFortuneAPIView(BasePeriodFortuneAPIView):
    """이 달의 운세 조회/생성 API"""
    period_type = 'monthly'

    def _get_period_info(self):
        return get_current_month()
