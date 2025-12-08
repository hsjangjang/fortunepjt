# Fortune Life - Vue3 Frontend

AI 기반 운세 서비스의 Vue3 SPA 프론트엔드입니다.

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

개발 서버가 `http://localhost:5173`에서 실행됩니다.

### 3. Django 백엔드 실행 (별도 터미널)

```bash
cd ..
python manage.py runserver
```

Django 서버가 `http://localhost:8000`에서 실행됩니다.

## 📦 빌드

### 프로덕션 빌드

```bash
npm run build
```

빌드 결과물은 `dist/` 디렉토리에 생성됩니다.

### 빌드 미리보기

```bash
npm run preview
```

## 🏗️ 프로젝트 구조

```
frontend/
├── public/              # 정적 파일
├── src/
│   ├── api/            # API 호출 함수
│   ├── assets/         # 이미지, 폰트 등
│   ├── components/     # 재사용 가능한 컴포넌트
│   │   ├── Navbar.vue
│   │   └── Footer.vue
│   ├── composables/    # Vue Composition API 훅
│   ├── config/         # 설정 파일
│   │   └── api.js      # Axios 설정
│   ├── layouts/        # 레이아웃 컴포넌트
│   │   └── DefaultLayout.vue
│   ├── router/         # Vue Router 설정
│   │   └── index.js
│   ├── stores/         # Pinia 상태 관리
│   │   ├── auth.js
│   │   ├── fortune.js
│   │   └── recommendations.js
│   ├── utils/          # 유틸리티 함수
│   │   └── auth.js
│   ├── views/          # 페이지 컴포넌트
│   │   ├── Home.vue
│   │   ├── NotFound.vue
│   │   ├── auth/
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   └── Profile.vue
│   │   ├── fortune/
│   │   │   ├── Calculate.vue (TODO)
│   │   │   ├── Today.vue (TODO)
│   │   │   ├── Detail.vue (TODO)
│   │   │   └── ItemCheck.vue (TODO)
│   │   └── recommendations/
│   │       ├── OOTD.vue (TODO)
│   │       └── Menu.vue (TODO)
│   ├── App.vue
│   └── main.js
├── .env                # 환경 변수
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 🔧 기술 스택

- **Vue 3.5** - Progressive JavaScript Framework
- **Vite 7** - 빠른 빌드 도구
- **Vue Router 4** - 공식 라우팅 라이브러리
- **Pinia 3** - 공식 상태 관리 라이브러리
- **Axios 1.13** - HTTP 클라이언트

## 📝 개발 가이드

### API 호출

```javascript
// src/api/example.js
import apiClient from '@/config/api'

export async function fetchData() {
  const response = await apiClient.get('/api/endpoint/')
  return response.data
}
```

### 새로운 페이지 추가

1. `src/views/` 에 컴포넌트 생성
2. `src/router/index.js` 에 라우트 추가
3. 필요시 Pinia store 업데이트

### 상태 관리 (Pinia)

```vue
<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 상태 접근
console.log(authStore.user)

// 액션 호출
await authStore.login(username, password)
</script>
```

### 환경 변수

`.env` 파일에서 환경 변수를 설정합니다:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Fortune Life
```

컴포넌트에서 사용:

```javascript
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

## 🎨 스타일 가이드

### 색상 팔레트

- Primary: `#667eea`
- Secondary: `#764ba2`
- Success: `#10b981`
- Danger: `#ef4444`
- Warning: `#f59e0b`

### CSS 사용

컴포넌트별 scoped 스타일 사용:

```vue
<style scoped>
.my-component {
  color: #667eea;
}
</style>
```

## 🔐 인증

- Session 기반 인증 (Cookie)
- CSRF 토큰 자동 처리
- Axios 인터셉터로 토큰 관리
- Router 가드로 접근 제어

## 🐛 문제 해결

### CORS 에러

Django `settings.py`에서 CORS 설정 확인:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]
```

### API 404 에러

- Django 서버가 실행 중인지 확인
- API 엔드포인트 경로 확인 (`/api/...`)
- Vite 프록시 설정 확인 (`vite.config.js`)

### 로그인 상태 유지 안됨

- `withCredentials: true` 설정 확인
- CSRF 토큰 전송 확인
- Django SESSION_COOKIE_SAMESITE 설정 확인

## 📚 추가 문서

- [VUE3_MIGRATION_GUIDE.md](../VUE3_MIGRATION_GUIDE.md) - Vue3 전환 가이드
- [VUE3_IMPLEMENTATION_STATUS.md](../VUE3_IMPLEMENTATION_STATUS.md) - 구현 현황

## 🤝 기여

개발 시 다음 컨벤션을 따라주세요:

- **컴포넌트**: PascalCase (예: `MyComponent.vue`)
- **파일명**: camelCase 또는 kebab-case
- **변수/함수**: camelCase
- **상수**: UPPER_SNAKE_CASE

## 📄 라이선스

© 2025 Fortune Life. All rights reserved.
