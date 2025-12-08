import secrets
import string
import random
from datetime import timedelta
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import EmailVerificationCode
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)

User = get_user_model()


class RegisterAPIView(APIView):
    """회원가입 API"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # 회원가입 성공 시 토큰 발급
            refresh = RefreshToken.for_user(user)

            return Response({
                'success': True,
                'message': '회원가입이 완료되었습니다.',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """로그인 API (JWT 토큰 발급)"""
    serializer_class = CustomTokenObtainPairSerializer


class LogoutAPIView(APIView):
    """로그아웃 API (Refresh 토큰 블랙리스트 등록)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({
                'success': True,
                'message': '로그아웃되었습니다.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserMeAPIView(APIView):
    """현재 로그인한 사용자 정보 조회/수정 API"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data
        })

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '회원정보가 수정되었습니다.',
                'user': UserSerializer(request.user).data
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """회원 탈퇴"""
        user = request.user
        user.is_active = False
        user.save()

        return Response({
            'success': True,
            'message': '회원 탈퇴가 완료되었습니다.'
        }, status=status.HTTP_200_OK)


class PasswordChangeAPIView(APIView):
    """비밀번호 변경 API"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            # 임시 비밀번호 플래그 해제
            request.user.must_change_password = False
            request.user.save()

            return Response({
                'success': True,
                'message': '비밀번호가 변경되었습니다.'
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CheckUsernameAPIView(APIView):
    """아이디 중복 확인 API"""
    permission_classes = [AllowAny]

    def get(self, request):
        username = request.query_params.get('username', '')
        if not username:
            return Response({
                'success': False,
                'error': '아이디를 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        exists = User.objects.filter(username=username).exists()
        return Response({
            'success': True,
            'available': not exists,
            'message': '이미 사용중인 아이디입니다.' if exists else '사용 가능한 아이디입니다.'
        })


class CheckEmailAPIView(APIView):
    """이메일 중복 확인 API"""
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email', '')
        if not email:
            return Response({
                'success': False,
                'error': '이메일을 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 빈 문자열 이메일은 중복 체크 안함
        exists = User.objects.filter(email=email).exclude(email='').exists()
        return Response({
            'success': True,
            'available': not exists,
            'message': '이미 사용중인 이메일입니다.' if exists else '사용 가능한 이메일입니다.'
        })


class FindUsernameAPIView(APIView):
    """아이디 찾기 API - 이메일로 아이디 전송"""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '')

        if not email:
            return Response({
                'success': False,
                'error': '이메일을 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 이메일로 사용자 찾기
            user = User.objects.get(email=email)

            # 이메일로 아이디 전송
            send_mail(
                subject='[Fortune Life] 아이디 찾기 안내',
                message=f'''안녕하세요, {user.first_name}님.

요청하신 아이디 정보를 안내해 드립니다.

회원님의 아이디: {user.username}

본인이 요청하지 않으셨다면 이 메일을 무시해주세요.

감사합니다.
Fortune Life 팀''',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@fortunelife.com',
                recipient_list=[email],
                fail_silently=False,
            )

            # 이메일 일부 마스킹
            email_parts = email.split('@')
            if len(email_parts[0]) > 3:
                masked_email = email_parts[0][:3] + '*' * (len(email_parts[0]) - 3) + '@' + email_parts[1]
            else:
                masked_email = email_parts[0][0] + '*' * (len(email_parts[0]) - 1) + '@' + email_parts[1]

            return Response({
                'success': True,
                'message': f'{masked_email}로 아이디 정보를 전송했습니다.'
            })

        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': '해당 이메일로 가입된 계정이 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'success': False,
                'error': '이메일 전송에 실패했습니다. 잠시 후 다시 시도해주세요.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendPasswordResetCodeAPIView(APIView):
    """비밀번호 찾기 1단계 - 인증코드 이메일 전송"""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '')
        email = request.data.get('email', '')

        if not username:
            return Response({
                'success': False,
                'error': '아이디를 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response({
                'success': False,
                'error': '이메일을 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 아이디와 이메일로 사용자 찾기
            user = User.objects.get(username=username, email=email)

            # 기존 인증코드 삭제
            EmailVerificationCode.objects.filter(username=username, email=email).delete()

            # 6자리 인증코드 생성
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            # 인증코드 저장 (5분 후 만료)
            EmailVerificationCode.objects.create(
                email=email,
                username=username,
                code=verification_code,
                expires_at=timezone.now() + timedelta(minutes=5)
            )

            # 이메일로 인증코드 전송
            send_mail(
                subject='[Fortune Life] 비밀번호 찾기 인증코드',
                message=f'''안녕하세요, {user.first_name or user.username}님.

비밀번호 찾기 인증코드를 안내해 드립니다.

인증코드: {verification_code}

이 인증코드는 5분 후 만료됩니다.
본인이 요청하지 않으셨다면 이 메일을 무시해주세요.

감사합니다.
Fortune Life 팀''',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@fortunelife.com',
                recipient_list=[email],
                fail_silently=False,
            )

            # 이메일 일부 마스킹
            email_parts = email.split('@')
            if len(email_parts[0]) > 3:
                masked_email = email_parts[0][:3] + '*' * (len(email_parts[0]) - 3) + '@' + email_parts[1]
            else:
                masked_email = email_parts[0][0] + '*' * (len(email_parts[0]) - 1) + '@' + email_parts[1]

            return Response({
                'success': True,
                'message': f'{masked_email}로 인증코드를 전송했습니다.',
                'masked_email': masked_email
            })

        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': '아이디와 이메일이 일치하는 계정이 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"[SendPasswordResetCodeAPIView] Error: {e}")
            return Response({
                'success': False,
                'error': '이메일 전송에 실패했습니다. 잠시 후 다시 시도해주세요.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyCodeAndResetPasswordAPIView(APIView):
    """비밀번호 찾기 2단계 - 인증코드 확인 후 임시 비밀번호 발송"""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '')
        email = request.data.get('email', '')
        code = request.data.get('code', '')

        if not username or not email or not code:
            return Response({
                'success': False,
                'error': '아이디, 이메일, 인증코드를 모두 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 인증코드 확인
            verification = EmailVerificationCode.objects.get(
                username=username,
                email=email,
                code=code,
                is_verified=False
            )

            # 만료 확인
            if verification.is_expired:
                verification.delete()
                return Response({
                    'success': False,
                    'error': '인증코드가 만료되었습니다. 다시 요청해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 인증 완료 처리
            verification.is_verified = True
            verification.save()

            # 사용자 찾기
            user = User.objects.get(username=username, email=email)

            # 임시 비밀번호 생성 (영문+숫자 10자리)
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))

            # 비밀번호 변경 및 플래그 설정
            user.set_password(temp_password)
            user.must_change_password = True
            user.save()

            # 인증코드 삭제
            verification.delete()

            # 이메일로 임시 비밀번호 전송
            send_mail(
                subject='[Fortune Life] 임시 비밀번호 안내',
                message=f'''안녕하세요, {user.first_name or user.username}님.

인증이 완료되어 임시 비밀번호를 안내해 드립니다.

임시 비밀번호: {temp_password}

로그인 후 반드시 비밀번호를 변경해주세요.
본인이 요청하지 않으셨다면 고객센터로 문의해주세요.

감사합니다.
Fortune Life 팀''',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@fortunelife.com',
                recipient_list=[email],
                fail_silently=False,
            )

            # 이메일 일부 마스킹
            email_parts = email.split('@')
            if len(email_parts[0]) > 3:
                masked_email = email_parts[0][:3] + '*' * (len(email_parts[0]) - 3) + '@' + email_parts[1]
            else:
                masked_email = email_parts[0][0] + '*' * (len(email_parts[0]) - 1) + '@' + email_parts[1]

            return Response({
                'success': True,
                'message': f'{masked_email}로 임시 비밀번호를 전송했습니다.'
            })

        except EmailVerificationCode.DoesNotExist:
            return Response({
                'success': False,
                'error': '인증코드가 올바르지 않습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': '사용자를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"[VerifyCodeAndResetPasswordAPIView] Error: {e}")
            return Response({
                'success': False,
                'error': '임시 비밀번호 발송에 실패했습니다. 잠시 후 다시 시도해주세요.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 기존 API 유지 (호환성)
class FindPasswordAPIView(APIView):
    """비밀번호 찾기 API - 레거시 (인증코드 없이 바로 임시비밀번호 발송)"""
    permission_classes = [AllowAny]

    def post(self, request):
        # 새 API로 리다이렉트 안내
        return Response({
            'success': False,
            'error': '새로운 비밀번호 찾기 방식을 사용해주세요.',
            'redirect': '/auth/find-password'
        }, status=status.HTTP_400_BAD_REQUEST)
