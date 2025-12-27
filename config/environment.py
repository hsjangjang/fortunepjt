"""
환경 설정 분리 - 하드코딩된 값들을 환경변수로 통합 관리
settings.py에서 import하여 사용
"""
import os
from pathlib import Path


# ============================================================
# 기본 경로 설정
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# 보안 설정
# ============================================================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-here')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'


# ============================================================
# 허용 호스트
# ============================================================
ALLOWED_HOSTS_DEFAULT = [
    'localhost',
    '127.0.0.1',
    '.elasticbeanstalk.com',
    '.amazonaws.com',
]

def get_allowed_hosts():
    """환경변수에서 허용 호스트 목록 가져오기"""
    hosts = os.environ.get('ALLOWED_HOSTS', '')
    if hosts:
        return [h.strip() for h in hosts.split(',') if h.strip()]
    return ALLOWED_HOSTS_DEFAULT


# ============================================================
# 데이터베이스 설정
# ============================================================
def get_database_config():
    """환경변수에서 DB 설정 가져오기"""
    return {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('RDS_DB_NAME', 'fortune_db'),
        'USER': os.environ.get('RDS_USERNAME', 'postgres'),
        'PASSWORD': os.environ.get('RDS_PASSWORD', ''),
        'HOST': os.environ.get('RDS_HOSTNAME', 'localhost'),
        'PORT': os.environ.get('RDS_PORT', '5432'),
    }


# ============================================================
# API 설정
# ============================================================
class APIConfig:
    """API 관련 설정"""

    # Google Gemini API (운세 생성, 요약, 임베딩에 사용)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

    # OpenAI (직접 사용 시)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')


# ============================================================
# 이메일 설정
# ============================================================
class EmailConfig:
    """이메일 관련 설정"""

    BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    PORT = int(os.environ.get('EMAIL_PORT', '587'))
    USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

    # 알림 발송용
    ALERT_FROM_EMAIL = os.environ.get('ALERT_FROM_EMAIL', 'sinhyeongman634@gmail.com')
    ALERT_RECIPIENT_LIST = os.environ.get('ALERT_RECIPIENT_LIST', '99gktjs2937@naver.com').split(',')


# ============================================================
# AWS S3 설정
# ============================================================
class S3Config:
    """AWS S3 관련 설정"""

    USE_S3 = os.environ.get('USE_S3', 'False').lower() == 'true'
    ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
    S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-2')
    S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', '')

    @classmethod
    def get_custom_domain(cls):
        if cls.S3_CUSTOM_DOMAIN:
            return cls.S3_CUSTOM_DOMAIN
        if cls.STORAGE_BUCKET_NAME:
            return f'{cls.STORAGE_BUCKET_NAME}.s3.{cls.S3_REGION_NAME}.amazonaws.com'
        return ''


# ============================================================
# 캐시 설정
# ============================================================
class CacheConfig:
    """캐시 관련 설정"""

    CACHE_TTL = int(os.environ.get('CACHE_TTL', '86400'))  # 24시간
    FORTUNE_CACHE_TTL = int(os.environ.get('FORTUNE_CACHE_TTL', '86400'))  # 24시간
    API_CACHE_TTL = int(os.environ.get('API_CACHE_TTL', '3600'))  # 1시간


# ============================================================
# 운세 계산 설정
# ============================================================
class FortuneConfig:
    """운세 계산 관련 설정"""

    # 점수 범위
    MIN_SCORE = 50
    MAX_SCORE = 100
    BASE_SCORE_MIN = 55
    BASE_SCORE_MAX = 90

    # LLM 설정
    LLM_MAX_RETRIES = 1
    LLM_RETRY_DELAY = 2  # 초
    LLM_TEMPERATURE = 0.85
    LLM_MAX_TOKENS = 2500


# ============================================================
# CORS 설정
# ============================================================
def get_cors_origins():
    """환경변수에서 CORS 허용 오리진 가져오기"""
    origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
    if origins:
        return [o.strip() for o in origins.split(',') if o.strip()]
    return [
        'http://localhost:5173',
        'http://localhost:5174',
        'http://127.0.0.1:5173',
        'https://fortunelife.vercel.app',
    ]
