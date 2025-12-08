# AWS Django 프로젝트 배포 가이드

이 가이드는 Django 프로젝트를 AWS에 배포하는 전체 과정을 단계별로 설명합니다.

---

## 목차
1. [배포 준비](#1-배포-준비)
2. [AWS 계정 설정](#2-aws-계정-설정)
3. [배포 방법 선택](#3-배포-방법-선택)
4. [방법 1: AWS Elastic Beanstalk (추천 - 쉬운 방법)](#4-방법-1-aws-elastic-beanstalk-추천)
5. [방법 2: AWS EC2 (완전한 제어)](#5-방법-2-aws-ec2-완전한-제어)
6. [데이터베이스 설정 (RDS)](#6-데이터베이스-설정-rds)
7. [정적 파일 및 미디어 파일 (S3)](#7-정적-파일-및-미디어-파일-s3)
8. [도메인 연결](#8-도메인-연결)
9. [HTTPS 설정](#9-https-설정)
10. [문제 해결](#10-문제-해결)

---

## 1. 배포 준비

### 1.1 프로젝트 점검

현재 프로젝트에서 확인해야 할 사항:

```bash
# 필요한 패키지 목록 확인
pip freeze > requirements.txt

# Git 저장소 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Initial commit for deployment"
```

### 1.2 환경 변수 파일 준비

프로젝트 루트에 `.env.example` 파일 생성:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (AWS RDS)
DB_NAME=fortune_db
DB_USER=admin
DB_PASSWORD=your-password
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=5432

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=ap-northeast-2

# API Keys
OPENAI_API_KEY=your-openai-key
WEATHER_API_KEY=your-weather-key
GOOGLE_API_KEY=your-google-key
```

### 1.3 배포용 설정 파일 수정

`config/settings.py`에 배포 설정 추가:

```python
import os
from pathlib import Path

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database
if os.getenv('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    # 개발 환경에서는 SQLite 사용
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# AWS S3 설정 (선택사항)
if os.getenv('AWS_STORAGE_BUCKET_NAME'):
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'ap-northeast-2')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    # S3로 정적 파일 서빙
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

---

## 2. AWS 계정 설정

### 2.1 AWS 계정 생성

1. [AWS 콘솔](https://aws.amazon.com/ko/) 접속
2. "AWS 계정 생성" 클릭
3. 이메일, 비밀번호, 계정 이름 입력
4. 연락처 정보 입력
5. 결제 정보 입력 (신용카드 필요, 프리티어는 대부분 무료)
6. 신원 확인 (전화 인증)
7. 지원 플랜 선택 (기본 무료 플랜 선택)

### 2.2 IAM 사용자 생성 (보안 강화)

루트 계정 대신 IAM 사용자를 만들어 사용하는 것이 안전합니다.

1. AWS 콘솔 로그인
2. IAM 서비스 검색
3. "사용자" → "사용자 추가"
4. 사용자 이름 입력 (예: `django-deployer`)
5. 액세스 유형: "프로그래밍 방식 액세스" + "AWS Management Console 액세스" 모두 선택
6. 권한 설정:
   - "기존 정책 직접 연결" 선택
   - `AdministratorAccess` 선택 (또는 필요한 권한만 선택)
7. 액세스 키 ID와 비밀 액세스 키를 안전하게 저장

---

## 3. 배포 방법 선택

### 비교표

| 방법 | 난이도 | 비용 | 자동화 | 확장성 | 추천 대상 |
|------|--------|------|--------|--------|-----------|
| **Elastic Beanstalk** | 쉬움 | 중간 | 높음 | 높음 | 초보자, 빠른 배포 |
| **EC2** | 어려움 | 낮음 | 낮음 | 중간 | 완전한 제어 필요 |
| **ECS/Fargate** | 중간 | 높음 | 높음 | 매우 높음 | Docker 경험자 |
| **Lambda** | 어려움 | 매우 낮음 | 높음 | 자동 | 서버리스 선호 |

**초보자 추천: Elastic Beanstalk**

---

## 4. 방법 1: AWS Elastic Beanstalk (추천)

Elastic Beanstalk는 애플리케이션을 업로드하기만 하면 자동으로 배포, 확장, 로드 밸런싱을 처리합니다.

### 4.1 EB CLI 설치

```bash
# Windows
pip install awsebcli

# macOS/Linux
pip install awsebcli
```

### 4.2 EB 초기화

프로젝트 루트 디렉토리에서:

```bash
# EB 초기화
eb init

# 선택 사항:
# - 리전: ap-northeast-2 (서울)
# - 애플리케이션 이름: fortune-life
# - Python 버전: Python 3.12
# - SSH: yes (키 페어 생성)
```

### 4.3 배포 설정 파일 생성

프로젝트 루트에 `.ebextensions` 폴더 생성 후 설정 파일 추가:

**`.ebextensions/01_packages.config`**:
```yaml
packages:
  yum:
    git: []
    postgresql-devel: []
    libjpeg-turbo-devel: []
```

**`.ebextensions/02_python.config`**:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: config.wsgi:application
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: config.settings
```

**`.ebextensions/03_django.config`**:
```yaml
container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate --noinput"
    leader_only: true
  02_collectstatic:
    command: "source /var/app/venv/*/bin/activate && python manage.py collectstatic --noinput"
    leader_only: true
  03_create_superuser:
    command: "source /var/app/venv/*/bin/activate && python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')\""
    leader_only: true
```

### 4.4 환경 생성 및 배포

```bash
# 환경 생성 (최초 1회)
eb create fortune-life-env

# 환경 변수 설정
eb setenv SECRET_KEY="your-secret-key" \
         DEBUG=False \
         ALLOWED_HOSTS=".elasticbeanstalk.com" \
         OPENAI_API_KEY="your-key" \
         WEATHER_API_KEY="your-key"

# 배포
eb deploy

# 상태 확인
eb status

# 로그 확인
eb logs

# 웹사이트 열기
eb open
```

### 4.5 데이터베이스 연결 (RDS)

1. EB 콘솔에서 환경 선택
2. "구성" → "데이터베이스" → "편집"
3. PostgreSQL 선택
4. 인스턴스 클래스: db.t3.micro (프리티어)
5. 스토리지: 20GB
6. 사용자 이름/비밀번호 설정
7. 적용

EB가 자동으로 환경 변수 설정:
- `RDS_HOSTNAME`
- `RDS_PORT`
- `RDS_DB_NAME`
- `RDS_USERNAME`
- `RDS_PASSWORD`

`settings.py` 수정:
```python
if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
```

### 4.6 업데이트 배포

코드 수정 후:

```bash
git add .
git commit -m "Update message"
eb deploy
```

---

## 5. 방법 2: AWS EC2 (완전한 제어)

직접 서버를 설정하고 관리하는 방법입니다.

### 5.1 EC2 인스턴스 생성

1. AWS 콘솔 → EC2 → "인스턴스 시작"
2. 이름: `fortune-life-server`
3. AMI 선택: Ubuntu Server 22.04 LTS (프리티어)
4. 인스턴스 유형: t2.micro (프리티어)
5. 키 페어 생성 (`.pem` 파일 다운로드)
6. 네트워크 설정:
   - VPC: 기본값
   - 퍼블릭 IP 자동 할당: 활성화
   - 보안 그룹 규칙:
     - SSH (22) - 내 IP
     - HTTP (80) - 0.0.0.0/0
     - HTTPS (443) - 0.0.0.0/0
7. 스토리지: 30GB (프리티어 최대)
8. "인스턴스 시작"

### 5.2 SSH 접속

```bash
# Windows (PowerShell)
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip

# 권한 오류 시 (Windows)
icacls "your-key.pem" /inheritance:r
icacls "your-key.pem" /grant:r "%username%:R"
```

### 5.3 서버 초기 설정

```bash
# 패키지 업데이트
sudo apt update
sudo apt upgrade -y

# Python 및 필수 패키지 설치
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib git -y

# PostgreSQL 설정
sudo -u postgres psql
```

PostgreSQL에서:
```sql
CREATE DATABASE fortune_db;
CREATE USER fortune_user WITH PASSWORD 'your-password';
ALTER ROLE fortune_user SET client_encoding TO 'utf8';
ALTER ROLE fortune_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE fortune_user SET timezone TO 'Asia/Seoul';
GRANT ALL PRIVILEGES ON DATABASE fortune_db TO fortune_user;
\q
```

### 5.4 프로젝트 배포

```bash
# 프로젝트 디렉토리 생성
cd /home/ubuntu
mkdir apps
cd apps

# Git 클론 (GitHub에 푸시했다면)
git clone https://github.com/your-username/your-repo.git
cd your-repo

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# 환경 변수 설정
nano .env
# 위 .env.example 내용 복사 후 실제 값 입력

# Django 설정
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 5.5 Gunicorn 설정

Gunicorn 서비스 파일 생성:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

내용:
```ini
[Unit]
Description=gunicorn daemon for Fortune Life
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/apps/your-repo
Environment="PATH=/home/ubuntu/apps/your-repo/venv/bin"
EnvironmentFile=/home/ubuntu/apps/your-repo/.env
ExecStart=/home/ubuntu/apps/your-repo/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/ubuntu/apps/your-repo/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

서비스 시작:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

### 5.6 Nginx 설정

Nginx 설정 파일 생성:

```bash
sudo nano /etc/nginx/sites-available/fortune-life
```

내용:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/ubuntu/apps/your-repo/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/apps/your-repo/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/apps/your-repo/gunicorn.sock;
    }
}
```

설정 활성화:
```bash
sudo ln -s /etc/nginx/sites-available/fortune-life /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 5.7 방화벽 설정

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## 6. 데이터베이스 설정 (RDS)

EC2와 별도로 RDS를 사용하면 더 안정적입니다.

### 6.1 RDS 인스턴스 생성

1. AWS 콘솔 → RDS → "데이터베이스 생성"
2. 엔진: PostgreSQL
3. 템플릿: 프리 티어
4. DB 인스턴스 식별자: `fortune-db`
5. 마스터 사용자 이름: `admin`
6. 마스터 암호: 안전한 비밀번호
7. 인스턴스 구성: db.t3.micro
8. 스토리지: 20GB
9. 퍼블릭 액세스: 예 (보안 그룹으로 제어)
10. VPC 보안 그룹: 새로 생성
11. 데이터베이스 이름: `fortune_db`

### 6.2 보안 그룹 설정

1. RDS 보안 그룹 선택
2. 인바운드 규칙 편집
3. PostgreSQL (5432) 추가
4. 소스: EC2 인스턴스의 보안 그룹

### 6.3 Django 연결 설정

`.env` 파일에 RDS 정보 추가:
```env
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=5432
DB_NAME=fortune_db
DB_USER=admin
DB_PASSWORD=your-password
```

---

## 7. 정적 파일 및 미디어 파일 (S3)

### 7.1 S3 버킷 생성

1. AWS 콘솔 → S3 → "버킷 만들기"
2. 버킷 이름: `fortune-life-static` (고유해야 함)
3. 리전: ap-northeast-2 (서울)
4. 퍼블릭 액세스 차단 해제 (정적 파일용)
5. 생성

### 7.2 버킷 정책 설정

버킷 선택 → 권한 → 버킷 정책 편집:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::fortune-life-static/*"
        }
    ]
}
```

### 7.3 IAM 사용자 생성 (S3 액세스용)

1. IAM → 사용자 → 사용자 추가
2. 사용자 이름: `s3-upload-user`
3. 액세스 유형: 프로그래밍 방식 액세스
4. 권한: `AmazonS3FullAccess`
5. 액세스 키 저장

### 7.4 Django S3 설정

패키지 설치:
```bash
pip install django-storages boto3
```

`settings.py`:
```python
INSTALLED_APPS += ['storages']

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'ap-northeast-2'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Static files
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

# Media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

정적 파일 업로드:
```bash
python manage.py collectstatic
```

---

## 8. 도메인 연결

### 8.1 Route 53 설정 (AWS 도메인 서비스)

1. Route 53 → 호스팅 영역 생성
2. 도메인 이름 입력
3. 레코드 생성:
   - 유형: A
   - 이름: @ (또는 비워두기)
   - 값: EC2 퍼블릭 IP 또는 EB 환경 URL
4. www 레코드도 추가 (CNAME)

### 8.2 외부 도메인 사용 시

가비아, 후이즈 등에서 구매한 도메인:

1. 도메인 관리 → DNS 설정
2. A 레코드 추가:
   - 호스트: @
   - 값: EC2 IP
3. CNAME 레코드:
   - 호스트: www
   - 값: 도메인 이름

---

## 9. HTTPS 설정

### 9.1 Let's Encrypt (무료 SSL)

EC2에서:

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx -y

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 이메일 입력 및 약관 동의
# Nginx 자동 설정 선택

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

### 9.2 Elastic Beanstalk HTTPS

1. AWS Certificate Manager (ACM)에서 인증서 요청
2. 도메인 검증 (이메일 또는 DNS)
3. EB 환경 → 구성 → 로드 밸런서
4. 리스너 추가: HTTPS (443)
5. SSL 인증서 선택

---

## 10. 문제 해결

### 10.1 정적 파일이 안 보일 때

```bash
# 정적 파일 다시 수집
python manage.py collectstatic --clear --noinput

# Nginx 권한 확인
sudo chown -R www-data:www-data /home/ubuntu/apps/your-repo/staticfiles

# S3 사용 시 버킷 정책 확인
```

### 10.2 502 Bad Gateway

```bash
# Gunicorn 상태 확인
sudo systemctl status gunicorn
sudo journalctl -u gunicorn

# 소켓 파일 권한 확인
ls -l /home/ubuntu/apps/your-repo/gunicorn.sock

# Nginx 오류 로그
sudo tail -f /var/log/nginx/error.log
```

### 10.3 데이터베이스 연결 오류

```bash
# PostgreSQL 상태 확인
sudo systemctl status postgresql

# 연결 테스트
psql -h your-db-host -U your-user -d your-db

# RDS 보안 그룹 확인
# 5432 포트가 EC2에서 접근 가능한지 확인
```

### 10.4 환경 변수가 안 읽힐 때

```bash
# .env 파일 위치 확인
ls -la /home/ubuntu/apps/your-repo/.env

# Gunicorn 서비스에서 환경 변수 로드 확인
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

---

## 추가 팁

### 비용 절감

- **프리티어 활용**:
  - EC2 t2.micro (월 750시간)
  - RDS db.t3.micro (월 750시간)
  - S3 5GB 스토리지
  - CloudFront 50GB 전송

- **자동 종료 설정**: 개발 환경은 사용하지 않을 때 중지

- **모니터링**: CloudWatch로 비용 추적

### 성능 최적화

- **CDN 사용**: CloudFront로 정적 파일 캐싱
- **캐싱**: Redis/Memcached 추가
- **Auto Scaling**: 트래픽에 따라 자동 확장

### 백업

```bash
# 데이터베이스 백업
pg_dump -h your-db-host -U your-user your-db > backup.sql

# RDS 자동 백업 설정
# AWS 콘솔 → RDS → 백업 보존 기간 설정
```

### CI/CD (자동 배포)

GitHub Actions 예시:

`.github/workflows/deploy.yml`:
```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Deploy to EB
      uses: einaregilsson/beanstalk-deploy@v21
      with:
        aws_access_key: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws_secret_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        application_name: fortune-life
        environment_name: fortune-life-env
        region: ap-northeast-2
        version_label: ${{ github.sha }}
```

---

## 참고 자료

- [AWS 공식 문서](https://docs.aws.amazon.com/)
- [Django 배포 체크리스트](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Elastic Beanstalk Python 가이드](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html)

---

## 다음 단계

1. 모니터링 설정 (CloudWatch, Sentry)
2. 로깅 시스템 구축
3. 백업 자동화
4. CI/CD 파이프라인 구축
5. 성능 테스트 및 최적화

배포 성공을 기원합니다! 🚀
