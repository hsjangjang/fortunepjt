import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFortuneStore } from '@/stores/fortune'

// Lazy load components
const Home = () => import('@/views/Home.vue')

// Auth
const Login = () => import('@/views/auth/Login.vue')
const Register = () => import('@/views/auth/Register.vue')
const Profile = () => import('@/views/auth/Profile.vue')
const PasswordReset = () => import('@/views/auth/PasswordReset.vue')
const PasswordResetConfirm = () => import('@/views/auth/PasswordResetConfirm.vue')
const FindUsername = () => import('@/views/auth/FindUsername.vue')
const FindPassword = () => import('@/views/auth/FindPassword.vue')
const ChangePassword = () => import('@/views/auth/ChangePassword.vue')

// Fortune
const FortuneCalculate = () => import('@/views/fortune/Calculate.vue')
const FortuneLoading = () => import('@/views/fortune/Loading.vue')
const TodayFortune = () => import('@/views/fortune/Today.vue')
const FortuneDetail = () => import('@/views/fortune/Detail.vue')
const ItemCheck = () => import('@/views/fortune/ItemCheck.vue')

// Items
const ItemList = () => import('@/views/items/List.vue')
const ItemUpload = () => import('@/views/items/Upload.vue')
const ItemDetail = () => import('@/views/items/Detail.vue')

// Recommendations
const OOTDRecommendation = () => import('@/views/recommendations/OOTD.vue')
const MenuRecommendation = () => import('@/views/recommendations/Menu.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { title: 'Fortune Life - AI 기반 운세 서비스' }
    },

    // 인증 관련
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { title: '로그인', requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
      meta: { title: '회원가입', requiresGuest: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile,
      meta: { title: '내 프로필', requiresAuth: true }
    },

    // 운세 관련
    {
      path: '/fortune/calculate',
      name: 'fortune-calculate',
      component: FortuneCalculate,
      meta: { title: '운세 계산' }
    },
    {
      path: '/fortune/loading',
      name: 'fortune-loading',
      component: FortuneLoading,
      meta: { title: '운세 생성 중...' }
    },
    {
      path: '/fortune/today',
      name: 'fortune-today',
      component: TodayFortune,
      meta: { title: '오늘의 운세', requiresFortune: true }
    },
    {
      path: '/fortune/detail',
      name: 'fortune-detail',
      component: FortuneDetail,
      meta: { title: '상세 운세', requiresAuth: true, requiresFortune: true }
    },
    {
      path: '/fortune/item-check',
      name: 'item-check',
      component: ItemCheck,
      meta: { title: '행운템 분석', requiresAuth: true, requiresFortune: true }
    },

    // 아이템 관련
    {
      path: '/items',
      name: 'item-list',
      component: ItemList,
      meta: { title: '내 아이템', requiresAuth: true }
    },
    {
      path: '/items/upload',
      name: 'item-upload',
      component: ItemUpload,
      meta: { title: '아이템 등록', requiresAuth: true }
    },
    {
      path: '/items/:id',
      name: 'item-detail',
      component: ItemDetail,
      meta: { title: '아이템 상세', requiresAuth: true }
    },

    // 추천 시스템
    {
      path: '/recommendations/ootd',
      name: 'ootd',
      component: OOTDRecommendation,
      meta: { title: 'OOTD 추천', requiresAuth: true, requiresFortune: true }
    },
    {
      path: '/recommendations/menu',
      name: 'menu',
      component: MenuRecommendation,
      meta: { title: '메뉴 추천', requiresAuth: true, requiresFortune: true }
    },

    // 아이디 찾기
    {
      path: '/find-username',
      name: 'find-username',
      component: FindUsername,
      meta: { title: '아이디 찾기', requiresGuest: true }
    },

    // 비밀번호 찾기
    {
      path: '/find-password',
      name: 'find-password',
      component: FindPassword,
      meta: { title: '비밀번호 찾기', requiresGuest: true }
    },

    // 비밀번호 변경
    {
      path: '/change-password',
      name: 'change-password',
      component: ChangePassword,
      meta: { title: '비밀번호 변경', requiresAuth: true }
    },

    // 비밀번호 재설정
    {
      path: '/password-reset',
      name: 'password-reset',
      component: PasswordReset,
      meta: { title: '비밀번호 재설정' }
    },
    {
      path: '/password-reset-confirm/:uid/:token',
      name: 'password-reset-confirm',
      component: PasswordResetConfirm,
      meta: { title: '새 비밀번호 설정' }
    },

    // 404
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFound.vue'),
      meta: { title: '페이지를 찾을 수 없습니다' }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation Guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const fortuneStore = useFortuneStore()

  console.log('[Router Guard] 네비게이션:', from.path, '→', to.path)
  console.log('[Router Guard] 인증 상태:', authStore.isAuthenticated)
  console.log('[Router Guard] 운세 데이터:', fortuneStore.fortuneData)
  console.log('[Router Guard] 운세 날짜:', fortuneStore.fortuneDate)
  console.log('[Router Guard] hasTodayFortune:', fortuneStore.hasTodayFortune)

  // 페이지 타이틀 설정
  document.title = to.meta.title || 'Fortune Life'

  // 인증 필요한 페이지
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('[Router Guard] 인증 필요 → 로그인 페이지로')
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // 로그인한 사용자가 로그인/회원가입 페이지 접근 시
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    console.log('[Router Guard] 이미 로그인됨 → 홈으로')
    next({ name: 'home' })
    return
  }

  // ===== Django 운세 체크 로직 =====
  // Django: fortune_data가 필요한 페이지에서 세션 확인 후 리다이렉트
  if (to.meta.requiresFortune) {
    console.log('[Router Guard] 운세 필요한 페이지')

    // 운세 데이터 확인 (API 호출) - 로그인/비로그인 모두 체크
    const hasFortune = await fortuneStore.checkTodayFortune()

    console.log('[Router Guard] 운세 체크 완료')
    console.log('[Router Guard] hasFortune:', hasFortune)

    // 오늘의 운세가 없으면
    if (!hasFortune) {
      // 로그인 사용자: 로딩 페이지로 (원래 가려던 페이지 정보 전달)
      if (authStore.isAuthenticated) {
        console.log('[Router Guard] 로그인 사용자 → 운세 없음 → 로딩 페이지로')
        next({ name: 'fortune-loading', query: { redirect: to.fullPath }, replace: true })
        return
      } else {
        // 비로그인 사용자: 계산 페이지로 (원래 가려던 페이지 정보 전달)
        console.log('[Router Guard] 비로그인 사용자 → 운세 없음 → 계산 페이지로')
        next({ name: 'fortune-calculate', query: { redirect: to.fullPath }, replace: true })
        return
      }
    }

    console.log('[Router Guard] 운세 있음 → 통과')
  }

  console.log('[Router Guard] 통과')
  next()
})

export default router
