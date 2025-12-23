"""
사용자 관련 유틸리티 함수
"""
import os
from email.mime.image import MIMEImage
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings


def get_logo_path():
    """로고 파일 경로 반환"""
    return os.path.join(settings.BASE_DIR, 'static', 'images', 'email', 'logo.png')


def get_logo_html():
    """로고 HTML 반환 (외부 URL 이미지)"""
    # Vercel 배포 URL의 public 폴더 로고 이미지 사용 (캐시 무효화용 버전 파라미터 추가)
    logo_url = "https://frontend-wheat-three-93.vercel.app/logo.png?v=2"
    return f'<img src="{logo_url}" alt="Lucky Picky" style="width: 80px; height: 80px; margin-bottom: 12px;">'


def attach_logo(email_message):
    """이메일에 로고 이미지 첨부"""
    logo_path = get_logo_path()
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            logo_image = MIMEImage(f.read())
            logo_image.add_header('Content-ID', '<logo>')
            logo_image.add_header('Content-Disposition', 'inline', filename='logo.png')
            email_message.attach(logo_image)


def get_email_base_template(content, title="Lucky Picky"):
    """HTML 이메일 기본 템플릿"""
    logo_html = get_logo_html()
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; background-color: #0f1419;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 0;">
                <table role="presentation" style="max-width: 520px; margin: 0 auto; background: linear-gradient(135deg, #1a1d29 0%, #16182a 50%, #0f1419 100%); border-radius: 20px; overflow: hidden; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); border: 1px solid rgba(167, 139, 250, 0.1);">
                    <!-- Header with Logo -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e1b3c 0%, #2d2650 50%, #1a1733 100%); padding: 40px; text-align: center; position: relative;">
                            {logo_html}
                            <h1 style="margin: 0; color: #a78bfa; font-size: 28px; font-weight: 700; letter-spacing: 0.5px;">Lucky Picky</h1>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px; background: linear-gradient(to bottom, #1a1d29 0%, #16182a 100%);">
                            {content}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background: #0f1419; padding: 28px 40px; text-align: center; border-top: 1px solid rgba(167, 139, 250, 0.15);">
                            <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 13px; line-height: 1.5;">본인이 요청하지 않으셨다면 이 메일을 무시해주세요.</p>
                            <p style="margin: 0; color: #4b5563; font-size: 12px;">© 2025 Lucky Picky. All rights reserved.</p>
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
    """Lucky Picky 이메일 전송

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
            email.mixed_subtype = 'related'
            attach_logo(email)
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
Lucky Picky 팀'''

    # HTML 버전
    content = f'''
        <p style="margin: 0 0 28px 0; color: #e5e7eb; font-size: 17px; line-height: 1.6;">
            안녕하세요, <strong style="color: #c4b5fd;">{name}</strong>님.
        </p>
        <p style="margin: 0 0 28px 0; color: #9ca3af; font-size: 15px; line-height: 1.7;">
            요청하신 아이디 정보를 안내해 드립니다.
        </p>
        <div style="background: linear-gradient(135deg, #1e1b3c 0%, #2d2650 100%); border-radius: 16px; padding: 32px; text-align: center; margin: 28px 0; border: 2px solid rgba(167, 139, 250, 0.3); box-shadow: 0 4px 16px rgba(167, 139, 250, 0.1);">
            <p style="margin: 0 0 12px 0; color: #9ca3af; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">회원님의 아이디</p>
            <p style="margin: 0; color: #c4b5fd; font-size: 32px; font-weight: 700; letter-spacing: 1.5px;">{user.username}</p>
        </div>
        <p style="margin: 28px 0 0 0; color: #9ca3af; font-size: 15px; line-height: 1.6;">
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
Lucky Picky 팀'''

    # HTML 버전
    content = f'''
        <p style="margin: 0 0 28px 0; color: #e5e7eb; font-size: 17px; line-height: 1.6;">
            안녕하세요, <strong style="color: #c4b5fd;">{name}</strong>님.
        </p>
        <p style="margin: 0 0 28px 0; color: #9ca3af; font-size: 15px; line-height: 1.7;">
            비밀번호 찾기 인증코드를 안내해 드립니다.
        </p>
        <div style="background: linear-gradient(135deg, #1e1b3c 0%, #2d2650 100%); border-radius: 16px; padding: 32px; text-align: center; margin: 28px 0; border: 2px solid rgba(167, 139, 250, 0.3); box-shadow: 0 4px 16px rgba(167, 139, 250, 0.1);">
            <p style="margin: 0 0 12px 0; color: #9ca3af; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">인증코드</p>
            <p style="margin: 0; color: #c4b5fd; font-size: 40px; font-weight: 700; letter-spacing: 10px;">{verification_code}</p>
        </div>
        <div style="background: linear-gradient(135deg, #2d2416 0%, #1f1a0f 100%); border-radius: 12px; padding: 16px 20px; margin: 28px 0; border: 1px solid rgba(251, 191, 36, 0.3); box-shadow: 0 2px 8px rgba(251, 191, 36, 0.1);">
            <p style="margin: 0; color: #fbbf24; font-size: 14px; line-height: 1.5;">
                ⏱️ 이 인증코드는 <strong>5분 후 만료</strong>됩니다.
            </p>
        </div>
        <p style="margin: 28px 0 0 0; color: #9ca3af; font-size: 15px; line-height: 1.6;">
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
Lucky Picky 팀'''

    # HTML 버전
    content = f'''
        <p style="margin: 0 0 28px 0; color: #e5e7eb; font-size: 17px; line-height: 1.6;">
            안녕하세요, <strong style="color: #c4b5fd;">{name}</strong>님.
        </p>
        <p style="margin: 0 0 28px 0; color: #9ca3af; font-size: 15px; line-height: 1.7;">
            인증이 완료되어 임시 비밀번호를 안내해 드립니다.
        </p>
        <div style="background: linear-gradient(135deg, #1e1b3c 0%, #2d2650 100%); border-radius: 16px; padding: 32px; text-align: center; margin: 28px 0; border: 2px solid rgba(167, 139, 250, 0.3); box-shadow: 0 4px 16px rgba(167, 139, 250, 0.1);">
            <p style="margin: 0 0 12px 0; color: #9ca3af; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">임시 비밀번호</p>
            <p style="margin: 0; color: #c4b5fd; font-size: 28px; font-weight: 700; letter-spacing: 3px; font-family: 'Courier New', monospace;">{temp_password}</p>
        </div>
        <div style="background: linear-gradient(135deg, #2d1616 0%, #1f0f0f 100%); border-radius: 12px; padding: 16px 20px; margin: 28px 0; border: 1px solid rgba(248, 113, 113, 0.3); box-shadow: 0 2px 8px rgba(248, 113, 113, 0.1);">
            <p style="margin: 0; color: #f87171; font-size: 14px; line-height: 1.5;">
                🔐 로그인 후 <strong>반드시 비밀번호를 변경</strong>해주세요.
            </p>
        </div>
        <p style="margin: 28px 0 0 0; color: #9ca3af; font-size: 15px; line-height: 1.6;">
            감사합니다.
        </p>
    '''
    html = get_email_base_template(content, "임시 비밀번호 안내")

    return text, html
