"""
사용자 관련 유틸리티 함수
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings


def get_logo_html():
    """로고 HTML 반환 (로고 URL이 있으면 이미지, 없으면 텍스트 로고)"""
    logo_url = getattr(settings, 'EMAIL_LOGO_URL', '')
    if logo_url:
        return f'<img src="{logo_url}" alt="Lucky Pick it" style="width: 80px; height: 80px; margin-bottom: 10px;">'
    else:
        # 텍스트 기반 로고 (크리스탈 볼 이모지 사용)
        return '<div style="font-size: 48px; margin-bottom: 8px;">🔮</div>'


def get_email_base_template(content, title="Lucky Pick it"):
    """HTML 이메일 기본 템플릿"""
    logo_html = get_logo_html()
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; background-color: #1a1a2e;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 0;">
                <table role="presentation" style="max-width: 480px; margin: 0 auto; background-color: #16213e; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
                    <!-- Header with Logo -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 30px 40px; text-align: center;">
                            {logo_html}
                            <h1 style="margin: 0; color: #a78bfa; font-size: 24px; font-weight: 600;">Lucky Pick it</h1>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px; background-color: #1e2746;">
                            {content}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #16213e; padding: 24px 40px; text-align: center; border-top: 1px solid #2d3a5c;">
                            <p style="margin: 0 0 8px 0; color: #8892b0; font-size: 12px;">본인이 요청하지 않으셨다면 이 메일을 무시해주세요.</p>
                            <p style="margin: 0; color: #5a6785; font-size: 11px;">© 2025 Lucky Pick it. All rights reserved.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''


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


def send_fortune_email(subject, message, recipient_email, html_message=None):
    """Fortune Life 이메일 전송

    Args:
        subject: 이메일 제목
        message: 이메일 본문 (텍스트)
        recipient_email: 수신자 이메일
        html_message: HTML 본문 (선택)

    Returns:
        bool: 전송 성공 여부
    """
    try:
        if html_message:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=get_from_email(),
                to=[recipient_email],
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)
        else:
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
    """아이디 찾기 이메일 내용 생성 (텍스트 + HTML)"""
    name = user.first_name or user.username

    # 텍스트 버전
    text = f'''안녕하세요, {name}님.

요청하신 아이디 정보를 안내해 드립니다.

회원님의 아이디: {user.username}

본인이 요청하지 않으셨다면 이 메일을 무시해주세요.

감사합니다.
Lucky Pick it 팀'''

    # HTML 버전
    content = f'''
        <p style="margin: 0 0 24px 0; color: #e2e8f0; font-size: 16px; line-height: 1.6;">
            안녕하세요, <strong style="color: #a78bfa;">{name}</strong>님.
        </p>
        <p style="margin: 0 0 24px 0; color: #94a3b8; font-size: 14px; line-height: 1.6;">
            요청하신 아이디 정보를 안내해 드립니다.
        </p>
        <div style="background: linear-gradient(135deg, #1e1e3f 0%, #2d2a4a 100%); border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0; border: 1px solid #3d3a5c;">
            <p style="margin: 0 0 8px 0; color: #8892b0; font-size: 12px;">회원님의 아이디</p>
            <p style="margin: 0; color: #a78bfa; font-size: 28px; font-weight: 700; letter-spacing: 1px;">{user.username}</p>
        </div>
        <p style="margin: 24px 0 0 0; color: #94a3b8; font-size: 14px; line-height: 1.6;">
            감사합니다.
        </p>
    '''
    html = get_email_base_template(content, "아이디 찾기 안내")

    return text, html


def create_verification_email(user, verification_code):
    """인증코드 이메일 내용 생성 (텍스트 + HTML)"""
    name = user.first_name or user.username

    # 텍스트 버전
    text = f'''안녕하세요, {name}님.

비밀번호 찾기 인증코드를 안내해 드립니다.

인증코드: {verification_code}

이 인증코드는 5분 후 만료됩니다.
본인이 요청하지 않으셨다면 이 메일을 무시해주세요.

감사합니다.
Lucky Pick it 팀'''

    # HTML 버전
    content = f'''
        <p style="margin: 0 0 24px 0; color: #e2e8f0; font-size: 16px; line-height: 1.6;">
            안녕하세요, <strong style="color: #a78bfa;">{name}</strong>님.
        </p>
        <p style="margin: 0 0 24px 0; color: #94a3b8; font-size: 14px; line-height: 1.6;">
            비밀번호 찾기 인증코드를 안내해 드립니다.
        </p>
        <div style="background: linear-gradient(135deg, #1e1e3f 0%, #2d2a4a 100%); border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0; border: 1px solid #3d3a5c;">
            <p style="margin: 0 0 8px 0; color: #8892b0; font-size: 12px;">인증코드</p>
            <p style="margin: 0; color: #a78bfa; font-size: 36px; font-weight: 700; letter-spacing: 8px;">{verification_code}</p>
        </div>
        <div style="background-color: #2d2a1a; border-radius: 8px; padding: 12px 16px; margin: 24px 0; border: 1px solid #4a4520;">
            <p style="margin: 0; color: #fbbf24; font-size: 13px;">
                ⏱️ 이 인증코드는 <strong>5분 후 만료</strong>됩니다.
            </p>
        </div>
        <p style="margin: 24px 0 0 0; color: #94a3b8; font-size: 14px; line-height: 1.6;">
            감사합니다.
        </p>
    '''
    html = get_email_base_template(content, "비밀번호 찾기 인증코드")

    return text, html


def create_temp_password_email(user, temp_password):
    """임시 비밀번호 이메일 내용 생성 (텍스트 + HTML)"""
    name = user.first_name or user.username

    # 텍스트 버전
    text = f'''안녕하세요, {name}님.

인증이 완료되어 임시 비밀번호를 안내해 드립니다.

임시 비밀번호: {temp_password}

로그인 후 반드시 비밀번호를 변경해주세요.
본인이 요청하지 않으셨다면 고객센터로 문의해주세요.

감사합니다.
Lucky Pick it 팀'''

    # HTML 버전
    content = f'''
        <p style="margin: 0 0 24px 0; color: #e2e8f0; font-size: 16px; line-height: 1.6;">
            안녕하세요, <strong style="color: #a78bfa;">{name}</strong>님.
        </p>
        <p style="margin: 0 0 24px 0; color: #94a3b8; font-size: 14px; line-height: 1.6;">
            인증이 완료되어 임시 비밀번호를 안내해 드립니다.
        </p>
        <div style="background: linear-gradient(135deg, #1e1e3f 0%, #2d2a4a 100%); border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0; border: 1px solid #3d3a5c;">
            <p style="margin: 0 0 8px 0; color: #8892b0; font-size: 12px;">임시 비밀번호</p>
            <p style="margin: 0; color: #a78bfa; font-size: 24px; font-weight: 700; letter-spacing: 2px; font-family: 'Courier New', monospace;">{temp_password}</p>
        </div>
        <div style="background-color: #2d1a1a; border-radius: 8px; padding: 12px 16px; margin: 24px 0; border: 1px solid #4a2020;">
            <p style="margin: 0; color: #f87171; font-size: 13px;">
                🔐 로그인 후 <strong>반드시 비밀번호를 변경</strong>해주세요.
            </p>
        </div>
        <p style="margin: 24px 0 0 0; color: #94a3b8; font-size: 14px; line-height: 1.6;">
            감사합니다.
        </p>
    '''
    html = get_email_base_template(content, "임시 비밀번호 안내")

    return text, html
