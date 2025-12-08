from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve


class LoginRequiredMessageMiddleware:
    """로그인이 필요한 페이지 접근 시 메시지를 표시하는 미들웨어"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 로그인 페이지로 리다이렉트되는 경우
        if (response.status_code == 302 and
            '/users/login/' in response.url and
            not request.user.is_authenticated):

            # 회원가입이나 비밀번호 재설정 완료 후 리다이렉트되는 경우는 제외
            excluded_paths = ['/users/register/', '/users/password-reset/confirm/']
            if request.path not in excluded_paths:
                # 메시지 추가
                messages.warning(request, '로그인 후 이용해주세요.')

        return response
