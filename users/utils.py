"""
사용자 관련 유틸리티 함수
"""
from django.core.mail import send_mail
from django.conf import settings


def mask_email(email):
    """이메일 주소 일부 마스킹

    Args:
        email: 이메일 주소 (예: test@example.com)

    Returns:
        마스킹된 이메일 (예: tes*@example.com)
    """
    if not email or '@' not in email:
        return email

    email_parts = email.split('@')
    local_part = email_parts[0]
    domain_part = email_parts[1]

    if len(local_part) > 3:
        masked_local = local_part[:3] + '*' * (len(local_part) - 3)
    else:
        masked_local = local_part[0] + '*' * (len(local_part) - 1)

    return f"{masked_local}@{domain_part}"


def get_from_email():
    """이메일 발신자 주소 반환"""
    return getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@fortunelife.com')


def send_fortune_email(subject, message, recipient_email):
    """Fortune Life 이메일 전송

    Args:
        subject: 이메일 제목
        message: 이메일 본문
        recipient_email: 수신자 이메일

    Returns:
        bool: 전송 성공 여부
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=get_from_email(),
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return True
    except Exception:
        return False


def create_username_email(user, email):
    """아이디 찾기 이메일 내용 생성"""
    return f'''안녕하세요, {user.first_name}님.

요청하신 아이디 정보를 안내해 드립니다.

회원님의 아이디: {user.username}

본인이 요청하지 않으셨다면 이 메일을 무시해주세요.

감사합니다.
Fortune Life 팀'''


def create_verification_email(user, verification_code):
    """인증코드 이메일 내용 생성"""
    return f'''안녕하세요, {user.first_name or user.username}님.

비밀번호 찾기 인증코드를 안내해 드립니다.

인증코드: {verification_code}

이 인증코드는 5분 후 만료됩니다.
본인이 요청하지 않으셨다면 이 메일을 무시해주세요.

감사합니다.
Fortune Life 팀'''


def create_temp_password_email(user, temp_password):
    """임시 비밀번호 이메일 내용 생성"""
    return f'''안녕하세요, {user.first_name or user.username}님.

인증이 완료되어 임시 비밀번호를 안내해 드립니다.

임시 비밀번호: {temp_password}

로그인 후 반드시 비밀번호를 변경해주세요.
본인이 요청하지 않으셨다면 고객센터로 문의해주세요.

감사합니다.
Fortune Life 팀'''
