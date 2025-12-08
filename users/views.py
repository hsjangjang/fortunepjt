from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from .models import User

class RegisterView(TemplateView):
    template_name = 'users/register.html'
    
    def post(self, request):
        # 폼 데이터 가져오기
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        last_name = request.POST.get('last_name', '')  # 성
        first_name = request.POST.get('first_name', '')  # 이름
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')

        # 비밀번호 확인
        if password1 != password2:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, self.template_name)

        # 사용자명 중복 확인
        if User.objects.filter(username=username).exists():
            messages.error(request, '이미 사용중인 아이디입니다.')
            return render(request, self.template_name)

        try:
            # 생년월일 검증
            if birth_date:
                parsed_birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                from datetime import date
                today = date.today()
                min_date = date(1900, 1, 1)

                if parsed_birth_date > today:
                    messages.error(request, '미래 날짜는 선택할 수 없습니다.')
                    return render(request, self.template_name)
                if parsed_birth_date < min_date:
                    messages.error(request, '1900년 이후 날짜를 선택해주세요.')
                    return render(request, self.template_name)
            else:
                parsed_birth_date = None

            # User 생성
            user = User.objects.create_user(
                username=username,
                email=request.POST.get('email', ''),  # 선택 입력
                password=password1,
                last_name=last_name,  # 성
                first_name=first_name,  # 이름
                birth_date=parsed_birth_date,
                calendar_type=request.POST.get('calendar_type', 'solar'),
                gender=gender,
                mbti=request.POST.get('mbti', ''),
                personal_color=request.POST.get('personal_color', ''),
                chinese_name=request.POST.get('chinese_name', '')
            )
            
            # 생년월일 시간이 있다면 추가
            birth_hour = request.POST.get('birth_hour')
            birth_minute = request.POST.get('birth_minute')
            
            if birth_hour and birth_minute:
                try:
                    birth_time_str = f"{birth_hour}:{birth_minute}"
                    user.birth_time = datetime.strptime(birth_time_str, '%H:%M').time()
                    user.save()
                except:
                    pass

            # 비로그인 사용자의 운세 데이터 삭제
            if 'fortune_data_v2' in request.session:
                del request.session['fortune_data_v2']
            if 'fortune_date_v2' in request.session:
                del request.session['fortune_date_v2']

            messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect('users:login')
            
        except Exception as e:
            messages.error(request, f'회원가입 중 오류가 발생했습니다: {str(e)}')
            return render(request, self.template_name)

class LoginView(TemplateView):
    template_name = 'users/login.html'
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 이메일로도 로그인 가능하도록 처리
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                pass
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            # 비로그인 사용자의 운세 데이터 삭제 (로그인 사용자와 충돌 방지)
            if 'fortune_data_v2' in request.session:
                del request.session['fortune_data_v2']
            if 'fortune_date_v2' in request.session:
                del request.session['fortune_date_v2']

            # 성 + 이름 조합으로 환영 메시지 (get_full_name() 사용)
            full_name = user.get_full_name() or user.username
            messages.success(request, f'{full_name}님, 환영합니다!')

            # next 파라미터가 있으면 해당 페이지로, 없으면 홈으로
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
            return render(request, self.template_name)

class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        messages.success(request, '로그아웃되었습니다.')
        return redirect('home')
    
    def post(self, request):
        logout(request)
        messages.success(request, '로그아웃되었습니다.')
        return redirect('home')

from django.contrib.auth.mixins import LoginRequiredMixin

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        # MBTI 선택지 추가
        mbti_choices = [
            ('ISTJ', 'ISTJ - 세상의 소금형'),
            ('ISFJ', 'ISFJ - 임금 뒤편의 권력형'),
            ('INFJ', 'INFJ - 예언자형'),
            ('INTJ', 'INTJ - 과학자형'),
            ('ISTP', 'ISTP - 백과사전형'),
            ('ISFP', 'ISFP - 성인군자형'),
            ('INFP', 'INFP - 잔다르크형'),
            ('INTP', 'INTP - 아이디어 뱅크형'),
            ('ESTP', 'ESTP - 수완좋은 활동가형'),
            ('ESFP', 'ESFP - 사교적인 유형'),
            ('ENFP', 'ENFP - 스파크형'),
            ('ENTP', 'ENTP - 발명가형'),
            ('ESTJ', 'ESTJ - 사업가형'),
            ('ESFJ', 'ESFJ - 친선도모형'),
            ('ENFJ', 'ENFJ - 언변능숙형'),
            ('ENTJ', 'ENTJ - 지도자형'),
        ]
        context['mbti_choices'] = mbti_choices

        return context

class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    """프로필 업데이트 뷰 (템플릿 기반)"""
    login_url = 'users:login'

    def post(self, request):
        user = request.user

        try:
            # 기본 정보 업데이트
            user.last_name = request.POST.get('last_name', user.last_name)  # 성
            user.first_name = request.POST.get('first_name', user.first_name)  # 이름
            user.email = request.POST.get('email', user.email)
            user.gender = request.POST.get('gender', user.gender)

            # 생년월일 업데이트
            birth_date_str = request.POST.get('birth_date')
            if birth_date_str:
                user.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()

            # 추가 정보 업데이트
            user.mbti = request.POST.get('mbti', '')
            user.personal_color = request.POST.get('personal_color', '')

            user.save()

            # 운세 데이터 초기화 (프로필 변경 시)
            if 'fortune_data_v2' in request.session:
                del request.session['fortune_data_v2']
            if 'fortune_date_v2' in request.session:
                del request.session['fortune_date_v2']

            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('users:profile')

        except Exception as e:
            messages.error(request, f'프로필 업데이트 중 오류가 발생했습니다: {str(e)}')
            return redirect('users:profile')


class PasswordResetView(TemplateView):
    template_name = 'users/password_reset.html'

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')

        try:
            user = User.objects.get(username=username, email=email)
            # 사용자 확인 성공 -> 세션에 사용자 ID 저장 후 비밀번호 재설정 페이지로 이동
            request.session['reset_user_id'] = user.id
            return redirect('users:password_reset_confirm')
        except User.DoesNotExist:
            messages.error(request, '일치하는 회원 정보가 없습니다.')
            return render(request, self.template_name)


class PasswordResetConfirmView(TemplateView):
    template_name = 'users/password_reset_confirm.html'

    def get(self, request):
        # 세션에 사용자 ID가 없으면 접근 불가
        if 'reset_user_id' not in request.session:
            messages.error(request, '잘못된 접근입니다.')
            return redirect('users:login')
        return render(request, self.template_name)

    def post(self, request):
        user_id = request.session.get('reset_user_id')
        if not user_id:
            messages.error(request, '세션이 만료되었습니다. 다시 시도해주세요.')
            return redirect('users:password_reset')

        password_1 = request.POST.get('new_password1')
        password_2 = request.POST.get('new_password2')

        if password_1 != password_2:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, self.template_name)

        try:
            user = User.objects.get(id=user_id)
            user.set_password(password_1)
            user.save()
            
            # 세션 정리
            del request.session['reset_user_id']
            
            messages.success(request, '비밀번호가 성공적으로 변경되었습니다. 로그인해주세요.')
            return redirect('users:login')
        except User.DoesNotExist:
            messages.error(request, '사용자를 찾을 수 없습니다.')
            return redirect('users:password_reset')
