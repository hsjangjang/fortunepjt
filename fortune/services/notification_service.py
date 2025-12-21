"""
알림 서비스 - 이메일 및 알림 관련 기능
"""
from datetime import datetime
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings


def send_api_quota_alert(api_name: str, error_message: str):
    """API 크레딧 소진 시 이메일 알림 발송"""
    cache_key = f"api_quota_alert_{api_name}"
    if cache.get(cache_key):
        print(f"[API Alert] {api_name} 알림 이미 발송됨, 스킵")
        return

    try:
        subject = f"[Lucky Picky] {api_name} API 크레딧 소진 알림"
        message = f"""안녕하세요,

Lucky Picky 서비스에서 {api_name} API 크레딧이 소진되었습니다.

발생 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
API: {api_name}
오류 메시지: {error_message}

빠른 시일 내에 크레딧을 충전해 주세요.

감사합니다.
Lucky Picky 시스템
"""
        from_email = getattr(settings, 'ALERT_FROM_EMAIL', 'sinhyeongman634@gmail.com')
        recipient_list = getattr(settings, 'ALERT_RECIPIENT_LIST', ['99gktjs2937@naver.com'])

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=True,
        )
        cache.set(cache_key, True, 60 * 60)
        print(f"[API Alert] {api_name} 크레딧 소진 알림 이메일 발송 완료")
    except Exception as e:
        print(f"[API Alert Error] 이메일 발송 실패: {e}")
