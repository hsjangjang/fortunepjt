# 🔮 Fortune Life - 운세 기반 일상 추천 서비스

운세, 사주, 별자리를 기반으로 개인 맞춤형 일상(OOTD, 메뉴, 아이템)을 추천하는 AI 기반 웹 서비스입니다.

## 🎯 핵심 기능

- 🎨 **AI 운세 계산**: Google Gemini 기반 사주, 별자리, MBTI 종합 분석
- 👔 **OOTD 추천**: 날씨와 운세를 고려한 맞춤형 코디 제안
- 🍽️ **메뉴 추천**: 운세에 맞는 음식 추천
- 📸 **아이템 색상 분석**: AI 이미지 분석으로 행운색 매칭도 계산
- 🎭 **비회원 지원**: 세션 기반으로 회원가입 없이도 이용 가능

## 🚀 빠른 시작

### 1. 저장소 클론 및 의존성 설치

```bash
# 저장소 클론
git clone https://github.com/yurim56/pjt.git
cd pjt

# Python 가상환경
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Node.js 의존성
npm install
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성 (프로젝트 루트)
cp .env.example .env

# 필수 API 키 설정
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_weather_api_key
SECRET_KEY=your_django_secret_key
```

### 3. 데이터베이스 초기화

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. 개발 서버 실행

#### Django 템플릿 버전 (기존)
```bash
python manage.py runserver
# http://localhost:8000
```

#### Vue SPA 버전 (신규)
```bash
# 터미널 1: Django API 서버
python manage.py runserver

# 터미널 2: Vue 개발 서버
npm run dev

# 접속: http://localhost:8000/vue/
```

## 🏗️ 프로젝트 구조

```
pjt/
├── config/              # Django 설정
├── users/               # 사용자 관리
├── fortune/             # 운세 계산 핵심 로직
│   ├── services.py      # AI 운세 생성
│   ├── api_views.py     # REST API
│   └── views.py         # 템플릿 뷰
├── recommendations/     # OOTD, 메뉴 추천
├── items/               # 아이템 색상 분석
├── templates/           # Django 템플릿
│   └── vue_app.html     # Vue 앱 서빙
├── frontend/            # Vue 3 프론트엔드
│   ├── src/
│   │   ├── components/  # ToastNotification, LoadingOverlay
│   │   ├── views/       # FortuneCalculate, TodayFortune, ItemCheck
│   │   ├── stores/      # Pinia 상태 관리
│   │   └── api/         # API 클라이언트
│   └── index.html
├── vite.config.js       # Vite 설정
└── package.json         # NPM 패키지
```

## 💻 기술 스택

### Backend
- **Django 5.2** + Django REST Framework
- **Google Gemini** - AI 운세 텍스트 생성
- **OpenCV** - 이미지 색상 분석
- **Redis/Session** - 운세 캐싱

### Frontend
- **Vue 3** (Composition API)
- **Vite** - 빌드 도구
- **Pinia** - 상태 관리
- **Vue Router** - SPA 라우팅
- **Axios** - HTTP 클라이언트
- **Bootstrap 5** - UI 프레임워크

### 주요 라이브러리
```bash
# Python
django==5.2.6
djangorestframework==3.16.1
google-generativeai  # Gemini
opencv-python        # 이미지 분석
Pillow               # 이미지 처리

# JavaScript
vue@3.5.25
vite@7.2.4
pinia@3.0.4
axios@1.13.2
```

## 🎨 프론트엔드 버전 비교

| 기능 | Django 템플릿 | Vue SPA |
|------|--------------|---------|
| 페이지 전환 | 전체 새로고침 | 부드러운 전환 ✨ |
| 초기 로딩 | 빠름 | 약간 느림 |
| UX | 기본 | 현대적 🎯 |
| 알림 | Alert | Toast Popup 🔔 |
| 상태 관리 | Session | Pinia |
| SEO | 우수 | 추가 설정 필요 |

**추천**: 둘 다 사용 가능! 필요에 따라 선택하세요.
- 빠른 개발/SEO 중요 → Django 템플릿
- 현대적 UX/SPA 경험 → Vue 버전

## 📡 API 엔드포인트

### 인증
```bash
POST   /users/login/         # 로그인
POST   /users/register/      # 회원가입
GET    /users/logout/        # 로그아웃
```

### 운세 (템플릿)
```bash
GET    /fortune/today/       # 오늘의 운세 페이지
GET    /fortune/calculate/   # 운세 계산 페이지
GET    /fortune/item-check/  # 아이템 행운도 측정
POST   /fortune/reset/       # 운세 초기화
```

### 운세 (API - Vue용)
```bash
POST   /fortune/api/calculate/     # 운세 계산
GET    /fortune/api/today/         # 오늘의 운세 조회
POST   /fortune/api/reset/         # 운세 초기화
GET    /fortune/api/item-check/    # 아이템 행운도
```

### 추천
```bash
GET    /recommendations/ootd/   # OOTD 추천
GET    /recommendations/menu/   # 메뉴 추천
```

### 아이템
```bash
GET    /items/               # 내 아이템 목록
POST   /items/upload/        # 이미지 업로드
```

## 🔑 필수 API 키

### 1. Google Gemini API (필수)
```bash
# https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_key_here
```

### 2. OpenWeatherMap API (OOTD용)
```bash
# https://openweathermap.org/api
WEATHER_API_KEY=your_key_here
```

## 🆕 Vue 프론트엔드 특징

### 새로운 컴포넌트
- ✨ **ToastNotification** - 우아한 팝업 알림
- 🔄 **LoadingOverlay** - 운세 생성 중 로딩 화면
- 🎨 **개선된 디자인** - Gradient 배경, 반투명 네비

### 상태 관리 (Pinia)
```javascript
import { useFortuneStore } from '@/stores/fortune'

const fortuneStore = useFortuneStore()

// 운세 계산
await fortuneStore.calculateFortune(formData)

// 상태 접근
fortuneStore.fortuneData      // 운세 데이터
fortuneStore.loading          // 로딩 상태
fortuneStore.hasFortune       // 운세 존재 여부
```

### API 사용 예시
```javascript
import { fortuneAPI } from '@/api/fortune'

// 운세 계산
const response = await fortuneAPI.calculate({
  birth_date: '1990-01-01',
  gender: 'M',
  mbti: 'INTJ'
})
```

## 📦 배포

### 개발 환경
```bash
# Django
python manage.py runserver

# Vue
npm run dev
```

### 프로덕션 빌드
```bash
# Vue 빌드
npm run build

# 빌드 파일은 static/dist/에 생성됨
# Django가 자동으로 서빙
```

## 🐛 문제 해결

### CORS 오류
```bash
# .env 파일 확인
VITE_API_BASE_URL=http://localhost:8000
```

### Vue 개발 서버 포트 충돌
```bash
npm run dev -- --port 5174
```

### __pycache__ / node_modules 문제
```bash
# 이미 .gitignore에 포함되어 있음
# Git에서 자동으로 제외됨
```

## 🗓️ 개발 현황

### ✅ 완료
- [x] Django 프로젝트 기본 구조
- [x] 운세 계산 핵심 로직
- [x] Google Gemini AI 통합
- [x] 이미지 색상 분석
- [x] OOTD, 메뉴 추천 시스템
- [x] Django 템플릿 UI
- [x] Vue 3 SPA 구현
- [x] Toast 알림 시스템
- [x] REST API 구축

### 🚧 진행 중
- [ ] 사용자 피드백 수집
- [ ] ML 기반 추천 알고리즘
- [ ] 프로덕션 배포

## 📚 문서

- [VUE_README.md](VUE_README.md) - Vue 상세 가이드 (참고용)
- API 문서: http://localhost:8000/api/ (개발 서버 실행 시)

## 🤝 기여

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📧 팀

- **프로젝트 저장소**: https://github.com/yurim56/pjt
- **이슈 트래커**: https://github.com/yurim56/pjt/issues

## 📝 라이선스

MIT License

---

**Made with ❤️ by SSAFY Team**
