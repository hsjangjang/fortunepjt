from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import date, datetime
from .services import FortuneCalculator
from .serializers import FortuneCalculateSerializer
from .models import DailyFortuneCache
import json


def save_fortune_to_db(user, session_key, fortune_date, fortune_data, birth_date=None, birth_time='', calendar_type='solar', chinese_name=''):
    """데이터베이스에 운세 데이터 저장"""
    try:
        # 기존 데이터 삭제 후 새로 저장
        if user and user.is_authenticated:
            # 로그인 사용자: user 기반 + session_key 기반 모두 삭제 (충돌 방지)
            DailyFortuneCache.objects.filter(user=user, fortune_date=fortune_date).delete()
            if session_key:
                DailyFortuneCache.objects.filter(session_key=session_key, fortune_date=fortune_date).delete()
            cache = DailyFortuneCache(user=user, fortune_date=fortune_date, session_key=session_key)
        elif session_key:
            DailyFortuneCache.objects.filter(session_key=session_key, fortune_date=fortune_date).delete()
            cache = DailyFortuneCache(session_key=session_key, fortune_date=fortune_date)
        else:
            return False

        # 전체 운세 데이터를 JSON으로 저장
        cache.full_fortune_data = json.dumps(fortune_data, ensure_ascii=False)

        # 운세 계산 키 저장 (동일 조건 캐시용)
        cache.birth_date = birth_date
        cache.birth_time = birth_time or ''
        cache.calendar_type = calendar_type or 'solar'
        cache.chinese_name = chinese_name or ''

        # 기본 필드도 저장 (검색/필터링용)
        cache.fortune_score = fortune_data.get('fortune_score', 50)
        cache.fortune_text = fortune_data.get('fortune_texts', {}).get('total', '')
        cache.lucky_color = fortune_data.get('lucky_color', '#7c3aed')
        cache.lucky_colors = fortune_data.get('lucky_colors', [])
        cache.lucky_number = fortune_data.get('lotto_numbers', [None])[0]
        cache.lucky_direction = fortune_data.get('lucky_item', {}).get('direction', '')
        cache.zodiac_sign = fortune_data.get('zodiac_sign', '')
        cache.chinese_zodiac = fortune_data.get('chinese_zodiac', '')
        cache.saju_data = json.dumps(fortune_data.get('saju_data', {}), ensure_ascii=False)

        cache.save()
        print(f"[DB Cache] 저장 완료: user={user}, session={session_key}, date={fortune_date}, birth={birth_date}")
        return True
    except Exception as e:
        print(f"[DB Cache] 저장 실패: {e}")
        return False


def find_same_condition_fortune(fortune_date, birth_date, birth_time='', calendar_type='solar', chinese_name=''):
    """동일 조건의 운세 캐시 찾기 (생년월일+시간+양음력+한자이름+날짜)"""
    try:
        cache = DailyFortuneCache.objects.filter(
            fortune_date=fortune_date,
            birth_date=birth_date,
            birth_time=birth_time or '',
            calendar_type=calendar_type or 'solar',
            chinese_name=chinese_name or ''
        ).order_by('created_at').first()  # 가장 먼저 생성된 것 사용

        if cache and cache.full_fortune_data:
            fortune_data = json.loads(cache.full_fortune_data)
            print(f"[DB Cache] 동일 조건 캐시 히트: birth={birth_date}, time={birth_time}, name={chinese_name}")
            return fortune_data
        return None
    except Exception as e:
        print(f"[DB Cache] 동일 조건 조회 실패: {e}")
        return None


def load_fortune_from_db(user, session_key, fortune_date):
    """데이터베이스에서 운세 데이터 로드"""
    try:
        if user and user.is_authenticated:
            cache = DailyFortuneCache.objects.filter(user=user, fortune_date=fortune_date).first()
        elif session_key:
            cache = DailyFortuneCache.objects.filter(session_key=session_key, fortune_date=fortune_date).first()
        else:
            return None

        if not cache:
            print(f"[DB Cache] 미스: user={user}, session={session_key}, date={fortune_date}")
            return None

        # full_fortune_data에서 전체 데이터 복원
        if cache.full_fortune_data:
            fortune_data = json.loads(cache.full_fortune_data)
            print(f"[DB Cache] 히트: user={user}, session={session_key}, date={fortune_date}")
            return fortune_data

        # 레거시 데이터 처리 (full_fortune_data가 없는 경우)
        print(f"[DB Cache] 레거시 데이터 - 재계산 필요")
        return None
    except Exception as e:
        print(f"[DB Cache] 로드 실패: {e}")
        return None


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
                calendar_type=calendar_type,
                mbti=getattr(request.user, 'mbti', None),
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
                'image_url': item.image.url if item.image else None,
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
