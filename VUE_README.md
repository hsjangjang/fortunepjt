sour# Vue 프론트엔드 구현

Fortune Life 프로젝트의 Vue 3 기반 프론트엔드 구현입니다.

## 🆕 최신 업데이트 (2025-01-26)

- ✨ **Toast Notification 시스템** - 우아한 팝업 알림
- 🎨 **개선된 UI/UX** - Django 템플릿과 동일한 디자인 적용
- 🔄 **Loading Overlay** - 운세 계산 중 로딩 화면

## 📋 구현된 기능

### ✅ 완료된 작업

1. **Vue 3 프로젝트 구조 설정**
   - Vite 기반 개발 환경
   - Vue Router 4 (SPA 라우팅)
   - Pinia (상태 관리)
   - Axios (HTTP 클라이언트)

2. **Django REST API 엔드포인트**
   - `/fortune/api/calculate/` - 운세 계산
   - `/fortune/api/today/` - 오늘의 운세 조회
   - `/fortune/api/reset/` - 운세 초기화
   - `/fortune/api/item-check/` - 아이템 행운도 측정

3. **Vue 컴포넌트**
   - `FortuneCalculate.vue` - 운세 계산 페이지
   - `TodayFortune.vue` - 오늘의 운세 표시
   - `ItemCheck.vue` - 아이템 행운도 측정

4. **통합 설정**
   - CORS 설정 완료
   - 세션 기반 인증
   - Django + Vue 통합 템플릿

## 🚀 시작하기

### 1. 개발 환경 실행

#### 터미널 1: Django 서버 실행
```bash
cd c:\Users\SSAFY\Desktop\pjt
python manage.py runserver
```

#### 터미널 2: Vue 개발 서버 실행
```bash
cd c:\Users\SSAFY\Desktop\pjt
npm run dev
```

### 2. 접속

- **Vue 앱 (개발 모드)**: http://localhost:8000/vue/
- **Django 템플릿 (기존)**: http://localhost:8000/fortune/calculate/
- **Vite 개발 서버**: http://localhost:5173/ (직접 접속 가능)

## 📁 프로젝트 구조

```
pjt/
├── frontend/                # Vue 프론트엔드
│   ├── src/
│   │   ├── api/            # API 클라이언트
│   │   │   └── fortune.js  # Fortune API
│   │   ├── assets/         # 정적 파일
│   │   │   └── main.css    # 전역 스타일
│   │   ├── components/     # 재사용 컴포넌트
│   │   ├── router/         # Vue Router 설정
│   │   │   └── index.js
│   │   ├── stores/         # Pinia 스토어
│   │   │   └── fortune.js  # Fortune 상태 관리
│   │   ├── views/          # 페이지 컴포넌트
│   │   │   ├── FortuneCalculate.vue
│   │   │   ├── TodayFortune.vue
│   │   │   └── ItemCheck.vue
│   │   ├── App.vue         # 루트 컴포넌트
│   │   └── main.js         # 앱 진입점
│   ├── index.html          # HTML 템플릿
│   └── .env                # 환경 변수
├── fortune/
│   ├── api_views.py        # REST API 뷰
│   ├── serializers.py      # DRF 시리얼라이저
│   └── urls.py             # API URL 설정
├── templates/
│   └── vue_app.html        # Vue 앱 서빙 템플릿
├── vite.config.js          # Vite 설정
└── package.json            # NPM 패키지
```

## 🔧 주요 기술 스택

### Frontend
- **Vue 3** - Composition API 사용
- **Vue Router 4** - SPA 라우팅
- **Pinia** - 상태 관리
- **Axios** - HTTP 클라이언트
- **Vite** - 빌드 도구
- **Bootstrap 5** - UI 프레임워크

### Backend
- **Django REST Framework** - REST API
- **CORS Headers** - CORS 처리
- **Session Authentication** - 세션 기반 인증

## 📝 API 사용 예시

### 운세 계산
```javascript
import { fortuneAPI } from '@/api/fortune'

const formData = {
  birth_date: '1990-01-01',
  gender: 'M',
  mbti: 'INTJ'
}

const response = await fortuneAPI.calculate(formData)
```

### 오늘의 운세 조회
```javascript
const response = await fortuneAPI.getToday()
```

### 운세 초기화
```javascript
await fortuneAPI.reset()
```

## 🎨 컴포넌트 설명

### FortuneCalculate.vue
- 사용자 입력 폼 (생년월일, 성별, MBTI)
- 운세 계산 요청
- 유효성 검증 (날짜 범위 체크)
- 로딩 상태 관리

### TodayFortune.vue
- 종합 운세 표시
- 4가지 운세 점수 (금전운, 애정운, 학업운, 직장운)
- 행운색 및 행운 아이템 표시
- 프로그레스 바로 시각화

### ItemCheck.vue
- 오늘의 행운색 표시
- 사용자 아이템 목록
- 아이템별 행운도 계산
- 색상 매칭 알고리즘

## 🔄 상태 관리 (Pinia)

```javascript
// Fortune Store 사용 예시
import { useFortuneStore } from '@/stores/fortune'

const fortuneStore = useFortuneStore()

// 운세 계산
await fortuneStore.calculateFortune(formData)

// 상태 접근
fortuneStore.fortuneData      // 운세 데이터
fortuneStore.loading          // 로딩 상태
fortuneStore.error            // 에러 메시지
fortuneStore.hasFortune       // 운세 존재 여부

// Getters
fortuneStore.fortuneScores    // 운세 점수들
fortuneStore.fortuneTexts     // 운세 텍스트들
fortuneStore.luckyColors      // 행운색 목록
```

## 🏗️ 프로덕션 빌드

```bash
# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

빌드된 파일은 `static/dist/` 디렉토리에 생성됩니다.

## 🌐 Django와 Vue 통합

개발 모드에서는 Vite 개발 서버를 사용하고, 프로덕션에서는 빌드된 정적 파일을 사용합니다.

### 개발 모드
```html
<!-- templates/vue_app.html -->
<script type="module" src="http://localhost:5173/@vite/client"></script>
<script type="module" src="http://localhost:5173/src/main.js"></script>
```

### 프로덕션 모드
```html
<link rel="stylesheet" href="/static/dist/assets/index.css">
<script type="module" src="/static/dist/assets/index.js"></script>
```

## 🔐 세션 인증

Vue 앱은 Django의 세션 인증을 사용합니다:
- `withCredentials: true` 설정으로 쿠키 자동 전송
- CSRF 토큰 자동 추가
- Django 세션과 Vue 상태 동기화

## 📊 비교: Django 템플릿 vs Vue

| 기능 | Django 템플릿 | Vue SPA |
|------|---------------|---------|
| **페이지 전환** | 전체 새로고침 | 부드러운 전환 |
| **로딩 속도** | 초기 빠름 | 초기 느림, 이후 빠름 |
| **사용자 경험** | 기본 | 현대적 |
| **개발 복잡도** | 낮음 | 높음 |
| **SEO** | 우수 | 추가 설정 필요 |
| **유지보수** | 쉬움 | 중간 |

## 🚧 향후 개선사항

1. **SSR (Server-Side Rendering)** - SEO 개선
2. **PWA (Progressive Web App)** - 오프라인 지원
3. **컴포넌트 재사용성 강화** - 공통 컴포넌트 분리
4. **테스트 코드 작성** - Vitest 사용
5. **타입스크립트 적용** - 타입 안정성

## 🆘 문제 해결

### CORS 오류
```bash
# .env 파일에 올바른 URL 설정
VITE_API_BASE_URL=http://localhost:8000
```

### 세션 쿠키 전송 안됨
```javascript
// axios 설정 확인
withCredentials: true
```

### Vite 개발 서버 오류
```bash
# 포트 충돌 시 다른 포트 사용
npm run dev -- --port 5174
```

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해주세요.
