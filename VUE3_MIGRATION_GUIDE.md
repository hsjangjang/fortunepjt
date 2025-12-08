# Vue3 프론트엔드 전환 가이드

Django 템플릿 기반에서 Vue3 SPA로 완전 전환하는 가이드입니다.

---

## 📋 목차

1. [프로젝트 구조](#프로젝트-구조)
2. [설치 및 실행](#설치-및-실행)
3. [아키텍처 개요](#아키텍처-개요)
4. [개발 워크플로우](#개발-워크플로우)
5. [주요 기능 구현](#주요-기능-구현)
6. [배포](#배포)

---

## 프로젝트 구조

```
pjt/
├── backend (Django)
│   ├── config/              # Django 설정
│   ├── users/               # 사용자 인증 API
│   ├── fortune/             # 운세 API
│   ├── recommendations/     # 추천 API
│   ├── items/               # 아이템 API
│   └── manage.py
│
├── frontend/ (Vue3)
│   ├── src/
│   │   ├── api/             # API 호출 함수
│   │   ├── assets/          # 이미지, 폰트 등
│   │   ├── components/      # 재사용 가능한 컴포넌트
│   │   ├── composables/     # Vue Composition API 훅
│   │   ├── config/          # 설정 파일
│   │   ├── layouts/         # 레이아웃 컴포넌트
│   │   ├── router/          # Vue Router 설정
│   │   ├── stores/          # Pinia 상태 관리
│   │   ├── utils/           # 유틸리티 함수
│   │   ├── views/           # 페이지 컴포넌트
│   │   │   ├── auth/        # 인증 관련
│   │   │   ├── fortune/     # 운세 관련
│   │   │   └── recommendations/ # 추천 시스템
│   │   ├── App.vue
│   │   └── main.js
│   ├── .env                 # 환경 변수
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── VUE3_MIGRATION_GUIDE.md  # 이 문서
```

---

## 설치 및 실행

### 1. Frontend 설치

```bash
# frontend 디렉토리로 이동
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행 (http://localhost:5173)
npm run dev

# 프로덕션 빌드
npm run build
```

### 2. Backend 실행

```bash
# 프로젝트 루트에서
python manage.py runserver
```

### 3. 동시 실행

**개발 환경에서는 두 서버를 모두 실행:**
- Vue 개발 서버: `http://localhost:5173` (프론트엔드)
- Django 서버: `http://localhost:8000` (백엔드 API)

Vite 프록시 설정으로 `/api`로 시작하는 요청은 자동으로 Django 서버로 전달됩니다.

---

## 아키텍처 개요

### Frontend (Vue3 SPA)

- **Framework**: Vue 3.5 (Composition API)
- **Build Tool**: Vite 7
- **Router**: Vue Router 4
- **State Management**: Pinia 3
- **HTTP Client**: Axios

### Backend (Django REST API)

- **Framework**: Django 5.2
- **REST API**: Django REST Framework
- **Authentication**: Session 기반 (쿠키) + JWT 옵션

### 통신 방식

```
Vue3 App (5173) → Vite Proxy → Django API (8000)
                     ↓
              CSRF Token + Session Cookie
                     ↓
                  JSON Response
```

---

## 개발 워크플로우

### 1. API 우선 개발

1. **Django에서 API 엔드포인트 작성**
   ```python
   # users/api_views.py
   class LoginAPIView(APIView):
       def post(self, request):
           # 로그인 로직
           return Response({'success': True, 'user': user_data})
   ```

2. **Vue에서 API 호출 함수 작성**
   ```javascript
   // src/api/auth.js
   export async function login(username, password) {
       const response = await apiClient.post('/api/auth/login/', {
           username, password
       })
       return response.data
   }
   ```

3. **Pinia Store에서 상태 관리**
   ```javascript
   // src/stores/auth.js
   async function login(username, password) {
       const data = await authAPI.login(username, password)
       user.value = data.user
       isAuthenticated.value = true
   }
   ```

4. **Vue 컴포넌트에서 사용**
   ```vue
   <script setup>
   import { useAuthStore } from '@/stores/auth'
   const authStore = useAuthStore()

   const handleLogin = async () => {
       await authStore.login(username.value, password.value)
       router.push('/')
   }
   </script>
   ```

### 2. 컴포넌트 구조

#### 재사용 가능한 컴포넌트 (components/)

```vue
<!-- components/Button.vue -->
<template>
  <button :class="buttonClass" @click="handleClick">
    <slot></slot>
  </button>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'primary' }
})
</script>
```

#### 페이지 컴포넌트 (views/)

```vue
<!-- views/auth/Login.vue -->
<template>
  <div class="login-page">
    <h1>로그인</h1>
    <LoginForm @submit="handleLogin" />
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async (credentials) => {
  await authStore.login(credentials.username, credentials.password)
  router.push('/')
}
</script>
```

---

## 주요 기능 구현

### 1. 인증 시스템

#### 로그인
```vue
<!-- views/auth/Login.vue -->
<template>
  <div class="auth-page">
    <form @submit.prevent="handleSubmit">
      <input v-model="username" placeholder="아이디" />
      <input v-model="password" type="password" placeholder="비밀번호" />
      <button type="submit" :disabled="loading">로그인</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  const result = await authStore.login(username.value, password.value)
  loading.value = false

  if (result.success) {
    router.push('/')
  } else {
    alert(result.error)
  }
}
</script>
```

#### 인증 가드 (Router)
```javascript
// router/index.js
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})
```

### 2. 운세 계산

```vue
<!-- views/fortune/Calculate.vue -->
<template>
  <div class="fortune-calculate">
    <h1>운세 계산</h1>
    <form @submit.prevent="calculate">
      <input v-model="birthDate" type="date" required />
      <select v-model="gender" required>
        <option value="M">남자</option>
        <option value="F">여자</option>
      </select>
      <button type="submit">운세 보기</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useFortuneStore } from '@/stores/fortune'
import { useRouter } from 'vue-router'

const fortuneStore = useFortuneStore()
const router = useRouter()

const birthDate = ref('')
const gender = ref('M')

const calculate = async () => {
  await fortuneStore.calculateFortune({
    birth_date: birthDate.value,
    gender: gender.value
  })
  router.push({ name: 'fortune-today' })
}
</script>
```

### 3. OOTD 추천

```vue
<!-- views/recommendations/OOTD.vue -->
<template>
  <div class="ootd-page">
    <h1>OOTD 추천</h1>

    <div v-if="loading">로딩 중...</div>

    <div v-else-if="ootdData" class="recommendations">
      <div class="weather-card">
        <h2>{{ weatherData.city }}</h2>
        <p>{{ weatherData.temp }}°C</p>
      </div>

      <div class="outfit-recommendations">
        <div class="outfit-item">
          <h3>상의</h3>
          <p>{{ ootdData.outfit.top }}</p>
        </div>
        <div class="outfit-item">
          <h3>하의</h3>
          <p>{{ ootdData.outfit.bottom }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRecommendationsStore } from '@/stores/recommendations'

const recommendationsStore = useRecommendationsStore()
const loading = ref(true)
const ootdData = ref(null)
const weatherData = ref(null)

onMounted(async () => {
  const result = await recommendationsStore.getOOTD()
  if (result.success) {
    ootdData.value = result.data.outfit
    weatherData.value = result.data.weather
  }
  loading.value = false
})
</script>
```

---

## 환경 변수 설정

### Frontend (.env)

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000

# App Settings
VITE_APP_TITLE=Fortune Life
```

### Backend (.env)

```env
# CORS 설정
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 배포

### 1. 프로덕션 빌드

```bash
cd frontend
npm run build
```

빌드 결과물은 `frontend/dist/` 디렉토리에 생성됩니다.

### 2. Django Static 파일로 서빙

**옵션 1: Django에서 직접 서빙**

```python
# config/settings.py
STATICFILES_DIRS = [
    BASE_DIR / 'frontend' / 'dist',
]
```

**옵션 2: Nginx로 분리**

```nginx
server {
    listen 80;

    # Vue 앱 (SPA)
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Django API
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

### 3. AWS 배포

Elastic Beanstalk에 배포 시:

```bash
# Vue 빌드
cd frontend && npm run build

# Django collectstatic
python manage.py collectstatic --noinput

# 배포
eb deploy
```

---

## 기존 Django 템플릿과 병행 운영

### Phase 1: 점진적 마이그레이션

1. **Vue 라우트**: `/` (새 Vue 앱)
2. **Django 템플릿**: `/legacy/` (기존 템플릿)

```python
# config/urls.py
urlpatterns = [
    path('api/', include('api_urls')),  # API
    path('legacy/', include('legacy_urls')),  # 기존 템플릿
    re_path(r'^.*$', vue_app),  # Vue SPA (모든 경로)
]
```

### Phase 2: 완전 전환

- Django는 API만 제공
- 모든 프론트엔드는 Vue로 처리

---

## 트러블슈팅

### CORS 에러

```python
# config/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]
```

### CSRF 토큰 문제

```javascript
// src/config/api.js
const csrfToken = getCookie('csrftoken')
if (csrfToken) {
  config.headers['X-CSRFToken'] = csrfToken
}
```

### 세션 인증 문제

```javascript
// axios 설정
withCredentials: true  // 쿠키 전송 활성화
```

---

## 다음 단계

1. ✅ 프로젝트 초기 설정 완료
2. ✅ 라우터 및 상태 관리 설정
3. 🔄 컴포넌트 개발
   - [ ] 레이아웃 컴포넌트
   - [ ] 인증 페이지
   - [ ] 운세 페이지
   - [ ] 추천 페이지
4. [ ] API 통합 테스트
5. [ ] 스타일링 (TailwindCSS 또는 기존 CSS)
6. [ ] 프로덕션 배포

---

## 참고 자료

- [Vue 3 공식 문서](https://vuejs.org/)
- [Vue Router 문서](https://router.vuejs.org/)
- [Pinia 문서](https://pinia.vuejs.org/)
- [Vite 문서](https://vitejs.dev/)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

**작성일**: 2025-11-30
**버전**: 1.0.0
