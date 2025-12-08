from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from datetime import date
import json
from .services import FortuneCalculator
from .api_views import save_fortune_to_db, load_fortune_from_db


class LoadingView(TemplateView):
    """운세 생성 중 로딩 페이지"""
    template_name = 'fortune/loading.html'

    def get(self, request):
        """로그인 사용자 자동 로딩 (GET 요청)"""
        if not request.user.is_authenticated:
            return redirect('fortune:calculate')

        # 로그인 사용자 정보 사용
        user = request.user
        context = {
            'birth_date': str(user.birth_date) if user.birth_date else '',
            'gender': user.gender or '',
            'mbti': user.mbti or '',
            'calendar_type': getattr(user, 'calendar_type', 'solar') or 'solar',
            'is_authenticated': True
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """비로그인 사용자 폼 제출 (POST 요청)"""
        # 폼 데이터 받기
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        mbti = request.POST.get('mbti')
        calendar_type = request.POST.get('calendar_type', 'solar')

        context = {
            'birth_date': birth_date,
            'gender': gender,
            'mbti': mbti,
            'calendar_type': calendar_type,
            'is_authenticated': request.user.is_authenticated
        }
        return render(request, self.template_name, context)


class ItemCheckView(LoginRequiredMixin, TemplateView):
    """아이템 행운도 측정 페이지"""
    template_name = 'fortune/item_check.html'
    login_url = '/users/login/'

    def get(self, request, *args, **kwargs):
        # 세션에서 운세 데이터 가져오기
        fortune_data = request.session.get('fortune_data_v2')
        fortune_date = request.session.get('fortune_date_v2')
        today_str = str(date.today())

        # 로그인 사용자이고 운세 데이터가 없거나 날짜가 다르면 로딩 페이지로 리다이렉트
        if request.user.is_authenticated and (not fortune_data or fortune_date != today_str):
            return redirect('fortune:loading_auto')

        # 기존 로직 사용
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 세션에서 운세 데이터 가져오기 (TodayFortuneView와 동일한 캐싱 전략)
        fortune_data = self.request.session.get('fortune_data_v2')
        fortune_date = self.request.session.get('fortune_date_v2')
        today_str = str(date.today())
        
        # 로그인한 사용자의 실제 운세 계산 (DB 캐시 사용)
        if self.request.user.is_authenticated:
            # 세션 키 확보
            if not self.request.session.session_key:
                self.request.session.create()
            session_key = self.request.session.session_key

            today = date.today()

            # DB 캐시에서 운세 로드
            fortune_data = load_fortune_from_db(self.request.user, session_key, today)

            if not fortune_data:
                # 캐시 미스 - 새로 계산
                try:
                    print(f"[ItemCheck View] DB 캐시 미스 - 새로 계산 시작... 사용자: {self.request.user.username}")

                    calculator = FortuneCalculator()
                    fortune_data = calculator.calculate_fortune(
                        birth_date=self.request.user.birth_date,
                        gender=self.request.user.gender,
                        birth_time=self.request.user.birth_time,
                        chinese_name=getattr(self.request.user, 'chinese_name', None),
                        calendar_type=getattr(self.request.user, 'calendar_type', 'solar'),
                        user_id=self.request.user.id,
                        session_key=session_key
                    )
                    # DB에 저장
                    save_fortune_to_db(self.request.user, session_key, today, fortune_data)
                    print("[ItemCheck View] 운세 계산 완료 및 DB 저장")
                except Exception as e:
                    import traceback
                    print(f"[ERROR] 운세 계산 실패: {e}")
                    print(f"[ERROR] Traceback: {traceback.format_exc()}")
                    # 기본값 사용
                    fortune_data = {
                        'lucky_colors': ['노란색', '베이지색', '빨간색'],
                        'lucky_item': {
                            'main': '미니 키링',
                            'zodiac': '실버 키링',
                            'today_special': '폰 스트랩'
                        }
                    }
            else:
                # 캐시 히트 - 기존 데이터 사용
                print("[ItemCheck View] DB 캐시 히트 - 기존 데이터 사용")

            context['fortune'] = fortune_data
        else:
            # 비로그인 사용자 기본값
            context['fortune'] = {
                'lucky_colors': ['노란색', '베이지색', '빨간색'],
                'lucky_item': {
                    'main': '미니 키링',
                    'zodiac': '실버 키링',
                    'today_special': '폰 스트랩'
                }
            }
        
        # 로그인한 사용자의 아이템 가져오기
        if self.request.user.is_authenticated:
            from items.models import UserItem
            import json
            
            user_items = UserItem.objects.filter(user=self.request.user).order_by('-created_at')

            # colors_json은 이미 모델의 property로 정의되어 있음
            context['user_items'] = list(user_items)
        else:
            context['user_items'] = []
        
        # 행운색 HEX 매핑 (Service의 정의 사용)
        color_hex_map = FortuneCalculator.NAME_TO_HEX
        
        # 행운색 HEX 변환
        if 'fortune' in context and 'lucky_colors' in context['fortune']:
            context['lucky_colors_with_hex'] = [
                {
                    'name': color,
                    'hex': color_hex_map.get(color, '#FF0000'),
                    'is_light': self._is_light_color(color_hex_map.get(color, '#FF0000'))
                }
                for color in context['fortune']['lucky_colors']
            ]
            # 행운색 목록 (이름만)
            context['lucky_colors'] = json.dumps(context['fortune']['lucky_colors'])

        # 행운 아이템 정보 (JSON)
        if 'fortune' in context and 'lucky_item' in context['fortune']:
            context['lucky_item'] = context['fortune']['lucky_item']
            context['lucky_item_json'] = json.dumps(context['fortune']['lucky_item'], ensure_ascii=False)

        return context

    def _is_light_color(self, hex_color):
        """밝은 색상인지 판별 (텍스트 색상 결정용)"""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            # YIQ 공식으로 밝기 계산
            yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
            return yiq >= 128
        except:
            return False


class TodayFortuneView(TemplateView):
    """오늘의 운세 페이지"""
    template_name = 'fortune/today.html'
    login_url = '/users/login/'

    def get(self, request, *args, **kwargs):
        # 세션 키 확보
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        today = date.today()
        today_str = str(today)

        # DB 캐시에서 운세 데이터 로드
        user = request.user if request.user.is_authenticated else None
        fortune_data = load_fortune_from_db(user, session_key, today)

        # 비로그인 사용자이고 운세 데이터가 없으면 계산 페이지로 리다이렉트
        if not request.user.is_authenticated and not fortune_data:
            return redirect('fortune:calculate')

        # 로그인 사용자이고 운세 데이터가 없으면 로딩 페이지로 리다이렉트
        if request.user.is_authenticated and not fortune_data:
            print(f"[Django Template View] DB 캐시 미스 - 로딩 페이지로 리다이렉트 (사용자: {request.user.username})")
            return redirect('fortune:loading_auto')

        # 세션에도 저장 (기존 호환성)
        if fortune_data:
            request.session['fortune_data_v2'] = fortune_data
            request.session['fortune_date_v2'] = today_str

        # 기존 로직 사용
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['fortune_date'] = today

        # 세션 키 확보
        if not self.request.session.session_key:
            self.request.session.create()
        session_key = self.request.session.session_key

        # DB 캐시에서 운세 데이터 로드
        user = self.request.user if self.request.user.is_authenticated else None
        fortune_data = load_fortune_from_db(user, session_key, today)

        print(f"[TodayFortuneView] DB 캐시 로드: user={user}, fortune_data={'있음' if fortune_data else '없음'}")

        if fortune_data:
            # 로그인 사용자는 user_id 기반, 비로그인은 session_key 기반
            # 로그인 사용자는 브라우저가 바뀌어도 같은 로또 번호
            stored_user_id = fortune_data.get('user_id')
            current_user_id = self.request.user.id if self.request.user.is_authenticated else None

            if not self.request.session.session_key:
                self.request.session.create()
            current_session_key = self.request.session.session_key
            stored_session_key = fortune_data.get('session_key')

            print(f"[DEBUG LOTTO] current_user_id: {current_user_id}, stored_user_id: {stored_user_id}")
            print(f"[DEBUG LOTTO] current_session_key: {current_session_key}")
            print(f"[DEBUG LOTTO] current lotto: {fortune_data.get('lotto_numbers')}")

            # 로또 번호 재생성이 필요한 경우:
            # 1. 로그인 사용자인데 user_id가 다른 경우 (다른 사람의 세션 데이터)
            # 2. 비로그인 사용자인데 session_key가 다른 경우
            need_regenerate = False
            if current_user_id:
                # 로그인 사용자: user_id가 없거나 다르면 재생성
                if not stored_user_id or stored_user_id != current_user_id:
                    need_regenerate = True
            else:
                # 비로그인 사용자: session_key가 없거나 다르면 재생성
                if not stored_session_key or stored_session_key != current_session_key:
                    need_regenerate = True

            if need_regenerate:
                from fortune.services import FortuneCalculator
                from datetime import datetime as dt

                print(f"[DEBUG LOTTO] 로또 번호 재생성 시작!")

                # 생년월일 파싱
                birth_str = fortune_data.get('birth_date')
                if birth_str:
                    try:
                        birth_date = dt.strptime(birth_str, '%Y-%m-%d').date()
                        calculator = FortuneCalculator()
                        # 새 로또 번호 생성
                        new_lotto = calculator._generate_lucky_lotto_numbers(
                            birth_date=birth_date,
                            today=date.today(),
                            fortune_scores=fortune_data.get('fortune_scores'),
                            gender=fortune_data.get('gender', 'M'),
                            user_id=current_user_id,
                            session_key=current_session_key
                        )
                        print(f"[DEBUG LOTTO] 새 로또 번호: {new_lotto}")
                        fortune_data['lotto_numbers'] = new_lotto
                        fortune_data['user_id'] = current_user_id
                        fortune_data['session_key'] = current_session_key
                        # 세션 업데이트
                        self.request.session['fortune_data_v2'] = fortune_data
                        self.request.session.modified = True
                    except Exception as e:
                        print(f"[ERROR] 로또 번호 재생성 실패: {e}")
                        import traceback
                        traceback.print_exc()

            # 운세 점수들 추가
            context['fortune'] = fortune_data
            context['fortune']['money_score'] = fortune_data.get('fortune_scores', {}).get('money', 0)
            context['fortune']['love_score'] = fortune_data.get('fortune_scores', {}).get('love', 0)
            context['fortune']['study_score'] = fortune_data.get('fortune_scores', {}).get('study', 0)
            context['fortune']['work_score'] = fortune_data.get('fortune_scores', {}).get('work', 0)

            # 운세 텍스트들 추가
            if 'fortune_texts' in fortune_data:
                context['fortune']['fortune_text'] = fortune_data['fortune_texts'].get('total', '')
                context['fortune']['money_text'] = fortune_data['fortune_texts'].get('money', '')
                context['fortune']['love_text'] = fortune_data['fortune_texts'].get('love', '')
                context['fortune']['study_text'] = fortune_data['fortune_texts'].get('study', '')
                context['fortune']['work_text'] = fortune_data['fortune_texts'].get('work', '')
        else:
            context['fortune'] = None

        # 미성년자 여부 확인 (만 19세 미만이면 로또 번호 숨김)
        context['is_minor'] = False
        from datetime import date as date_type, datetime as datetime_type
        today = date_type.today()

        birth = None
        if self.request.user.is_authenticated and self.request.user.birth_date:
            # 로그인 사용자: 저장된 생년월일 사용
            birth = self.request.user.birth_date
        elif fortune_data and fortune_data.get('birth_date'):
            # 비로그인 사용자: 세션의 운세 데이터에서 생년월일 가져오기
            birth_str = fortune_data.get('birth_date')
            try:
                if isinstance(birth_str, str):
                    # YYYY-MM-DD 형식
                    birth = datetime_type.strptime(birth_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        if birth:
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            context['is_minor'] = age < 19

        return context


class CalculateFortuneView(TemplateView):
    template_name = 'fortune/calculate.html'

    def get(self, request):
        # 강제 새로고침 파라미터 체크 (?refresh=1)
        force_refresh = request.GET.get('refresh') == '1'

        # 강제 새로고침이면 세션 초기화
        if force_refresh:
            if 'fortune_data_v2' in request.session:
                del request.session['fortune_data_v2']
            if 'fortune_date_v2' in request.session:
                del request.session['fortune_date_v2']

        # 로그인 사용자만 세션 체크 (비로그인은 항상 입력 가능)
        if request.user.is_authenticated:
            today_str = str(date.today())
            if (not force_refresh and
                request.session.get('fortune_date_v2') == today_str and
                request.session.get('fortune_data_v2')):
                # 로그인 사용자는 이미 오늘 운세가 있으면 바로 보여주기
                return redirect('fortune:today')
            else:
                # 로그인 사용자는 바로 로딩 페이지로 이동 (저장된 정보 사용)
                return redirect('fortune:loading_auto')

        # 비로그인 사용자는 입력 페이지 표시
        return render(request, self.template_name)
    
    def post(self, request):
        if request.user.is_authenticated:
            # 로그인 사용자는 저장된 정보 사용
            birth_date = request.user.birth_date
            gender = request.user.gender
            mbti = request.user.mbti
        else:
            # 비로그인 사용자는 폼 데이터 사용
            birth_date_str = request.POST.get('birth_date')
            gender = request.POST.get('gender')
            mbti = request.POST.get('mbti')
            
            if not birth_date_str or not gender:
                messages.error(request, '필수 정보를 입력해주세요.')
                return redirect('fortune:calculate')
                
            from datetime import datetime
            try:
                # 8자리 숫자 형식 (YYYYMMDD) 시도
                birth_date = datetime.strptime(birth_date_str, '%Y%m%d').date()
            except ValueError:
                try:
                    # 기존 형식 (YYYY-MM-DD) 시도
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, '올바른 생년월일 형식이 아닙니다. (예: 19990101)')
                    return redirect('fortune:calculate')

            # 날짜 유효성 검증
            today = date.today()
            min_date_obj = date(1900, 1, 1)

            if birth_date > today:
                messages.error(request, '미래 날짜는 선택할 수 없습니다.')
                return redirect('fortune:calculate')
            if birth_date < min_date_obj:
                messages.error(request, '1900년 이후 날짜를 선택해주세요.')
                return redirect('fortune:calculate')

        # 양력/음력 구분 가져오기
        calendar_type = request.POST.get('calendar_type', 'solar')

        # 세션 키 확보 (없으면 생성)
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        # 운세 계산
        calculator = FortuneCalculator()
        user_id = request.user.id if request.user.is_authenticated else None
        user = request.user if request.user.is_authenticated else None
        today = date.today()

        fortune_data = calculator.calculate_fortune(
            birth_date=birth_date,
            gender=gender,
            mbti=mbti,
            calendar_type=calendar_type,
            user_id=user_id,
            session_key=session_key
        )

        # DB에 저장 (Django와 Vue가 공유)
        save_fortune_to_db(user, session_key, today, fortune_data)
        print(f"[Django Template View] 운세 계산 완료 및 DB 저장: user={user}, session={session_key}")

        # 세션에도 저장 (기존 호환성)
        request.session['fortune_data_v2'] = fortune_data
        request.session['fortune_date_v2'] = str(today)

        # 운세 결과 페이지로 이동
        return redirect('fortune:today')


class DetailFortuneView(LoginRequiredMixin, TemplateView):
    """상세 운세 페이지 (로그인 필수)"""
    template_name = 'fortune/detail.html'
    login_url = '/users/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 세션에서 운세 데이터 가져오기
        fortune_data = self.request.session.get('fortune_data')

        if not fortune_data:
            # 세션 키 확보
            if not self.request.session.session_key:
                self.request.session.create()
            session_key = self.request.session.session_key

            # 운세 계산
            calculator = FortuneCalculator()
            fortune_data = calculator.calculate_fortune(
                birth_date=self.request.user.birth_date,
                gender=self.request.user.gender,
                birth_time=self.request.user.birth_time,
                chinese_name=self.request.user.chinese_name,
                calendar_type=getattr(self.request.user, 'calendar_type', 'solar'),
                user_id=self.request.user.id,
                session_key=session_key
            )

            # 세션에 저장
            self.request.session['fortune_data'] = fortune_data
            self.request.session['fortune_date'] = str(date.today())

        context['fortune'] = fortune_data
        return context


class ResetFortuneView(View):
    """운세 세션 초기화 (비로그인 사용자용)"""

    def post(self, request):
        # DB 캐시에서 운세 데이터 삭제
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        user = request.user if request.user.is_authenticated else None
        today = date.today()

        from .models import DailyFortuneCache
        if user:
            DailyFortuneCache.objects.filter(user=user, fortune_date=today).delete()
            print(f"[Reset] DB 캐시 삭제 완료: user={user}")
        else:
            DailyFortuneCache.objects.filter(session_key=session_key, fortune_date=today).delete()
            print(f"[Reset] DB 캐시 삭제 완료: session={session_key}")

        # 세션에서도 운세 데이터 삭제
        if 'fortune_data_v2' in request.session:
            del request.session['fortune_data_v2']
        if 'fortune_date_v2' in request.session:
            del request.session['fortune_date_v2']

        return JsonResponse({'status': 'success', 'message': '운세가 초기화되었습니다.'})