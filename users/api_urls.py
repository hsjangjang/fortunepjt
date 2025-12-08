from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

app_name = 'auth'

urlpatterns = [
    # 회원가입
    path('register/', api_views.RegisterAPIView.as_view(), name='register'),

    # 로그인 (JWT 토큰 발급)
    path('login/', api_views.CustomTokenObtainPairView.as_view(), name='login'),

    # 토큰 갱신
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 로그아웃
    path('logout/', api_views.LogoutAPIView.as_view(), name='logout'),

    # 현재 사용자 정보
    path('me/', api_views.UserMeAPIView.as_view(), name='me'),

    # 비밀번호 변경
    path('password/change/', api_views.PasswordChangeAPIView.as_view(), name='password_change'),

    # 아이디 중복 확인
    path('check-username/', api_views.CheckUsernameAPIView.as_view(), name='check_username'),

    # 이메일 중복 확인
    path('check-email/', api_views.CheckEmailAPIView.as_view(), name='check_email'),

    # 아이디 찾기
    path('find-username/', api_views.FindUsernameAPIView.as_view(), name='find_username'),

    # 비밀번호 찾기 (임시 비밀번호 발급)
    path('find-password/', api_views.FindPasswordAPIView.as_view(), name='find_password'),
]
