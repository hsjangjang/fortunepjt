import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFortuneStore } from '@/stores/fortune'
import apiClient from '@/config/api'

// 동적 import 실패 시 페이지 새로고침 (배포 후 캐시 문제 해결)
const lazyLoad = (importFn) => {
  return () => importFn().catch(() => {
    // 새로 배포된 경우 청크 파일이 변경되어 로드 실패할 수 있음
    // 이 경우 페이지를 새로고침하여 최신 버전을 로드
    window.location.reload()
  })
}

// Lazy load components
const Home = lazyLoad(() => import('@/views/Home.vue'))

// Auth
const Login = lazyLoad(() => import('@/views/auth/Login.vue'))
const Register = lazyLoad(() => import('@/views/auth/Register.vue'))
const Profile = lazyLoad(() => import('@/views/auth/Profile.vue'))
const PasswordReset = lazyLoad(() => import('@/views/auth/PasswordReset.vue'))
const PasswordResetConfirm = lazyLoad(() => import('@/views/auth/PasswordResetConfirm.vue'))
const FindUsername = lazyLoad(() => import('@/views/auth/FindUsername.vue'))
const FindPassword = lazyLoad(() => import('@/views/auth/FindPassword.vue'))
const ChangePassword = lazyLoad(() => import('@/views/auth/ChangePassword.vue'))
const DeleteAccount = lazyLoad(() => import('@/views/auth/DeleteAccount.vue'))

// Fortune
const FortuneCalculate = lazyLoad(() => import('@/views/fortune/Calculate.vue'))
const FortuneLoading = lazyLoad(() => import('@/views/fortune/Loading.vue'))
const Fortune = lazyLoad(() => import('@/views/fortune/Fortune.vue'))
const FortuneDetail = lazyLoad(() => import('@/views/fortune/Detail.vue'))
const ItemCheck = lazyLoad(() => import('@/views/fortune/ItemCheck.vue'))

// Items
const ItemList = lazyLoad(() => import('@/views/items/List.vue'))
const ItemUpload = lazyLoad(() => import('@/views/items/Upload.vue'))
const ItemDetail = lazyLoad(() => import('@/views/items/Detail.vue'))

// Recommendations
const OOTDRecommendation = lazyLoad(() => import('@/views/recommendations/OOTD.vue'))
const MenuRecommendation = lazyLoad(() => import('@/views/recommendations/Menu.vue'))

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
      component: Fortune,
      meta: { title: '오늘의 운세', requiresFortune: true }
    },
    {
      path: '/fortune/weekly',
      name: 'fortune-weekly',
      component: Fortune,
      meta: { title: '이 주의 운세', requiresFortune: true }
    },
    {
      path: '/fortune/monthly',
      name: 'fortune-monthly',
      component: Fortune,
      meta: { title: '이 달의 운세', requiresFortune: true }
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

    // 회원 탈퇴
    {
      path: '/delete-account',
      name: 'delete-account',
      component: DeleteAccount,
      meta: { title: '회원 탈퇴', requiresAuth: true }
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
      component: lazyLoad(() => import('@/views/NotFound.vue')),
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
  // 운세 필요한 페이지: daily/weekly/monthly 3개 모두 있어야 통과
  if (to.meta.requiresFortune) {
    console.log('[Router Guard] 운세 필요한 페이지')

    let hasAllFortunes = false

    if (authStore.isAuthenticated) {
      // 로그인 사용자: API로 3개 모두 체크
      try {
        const [dailyRes, weeklyRes, monthlyRes] = await Promise.all([
          apiClient.get('/api/fortune/today/'),
          apiClient.get('/api/fortune/weekly/'),
          apiClient.get('/api/fortune/monthly/')
        ])

        const hasDaily = dailyRes.data.success && dailyRes.data.fortune
        const hasWeekly = weeklyRes.data.success && weeklyRes.data.fortune
        const hasMonthly = monthlyRes.data.success && monthlyRes.data.fortune

        console.log('[Router Guard] 로그인 사용자 - daily:', hasDaily, 'weekly:', hasWeekly, 'monthly:', hasMonthly)

        hasAllFortunes = hasDaily && hasWeekly && hasMonthly
      } catch (error) {
        console.error('[Router Guard] 운세 체크 에러:', error)
        hasAllFortunes = false
      }
    } else {
      // 비로그인 사용자도 API로 3개 모두 체크
      try {
        const [dailyRes, weeklyRes, monthlyRes] = await Promise.all([
          apiClient.get('/api/fortune/today/'),
          apiClient.get('/api/fortune/weekly/'),
          apiClient.get('/api/fortune/monthly/')
        ])

        const hasDaily = dailyRes.data.success && dailyRes.data.fortune
        const hasWeekly = weeklyRes.data.success && weeklyRes.data.fortune
        const hasMonthly = monthlyRes.data.success && monthlyRes.data.fortune

        console.log('[Router Guard] 비로그인 사용자 - daily:', hasDaily, 'weekly:', hasWeekly, 'monthly:', hasMonthly)

        hasAllFortunes = hasDaily && hasWeekly && hasMonthly
      } catch (error) {
        console.error('[Router Guard] 비로그인 운세 체크 에러:', error)
        hasAllFortunes = false
      }
    }

    console.log('[Router Guard] hasAllFortunes:', hasAllFortunes)

    // 운세가 하나라도 없으면 Loading 페이지로
    if (!hasAllFortunes) {
      if (authStore.isAuthenticated) {
        console.log('[Router Guard] 로그인 사용자 → 운세 없음 → 로딩 페이지로')
        next({ name: 'fortune-loading', query: { redirect: to.fullPath }, replace: true })
        return
      } else {
        // 비로그인 사용자: formData 있으면 로딩, 없으면 계산 페이지
        const formInfo = fortuneStore.formData || {}
        if (formInfo.birth_date && formInfo.gender) {
          console.log('[Router Guard] 비로그인 + formData 있음 → 로딩 페이지로')
          next({
            name: 'fortune-loading',
            query: {
              redirect: to.fullPath,
              birth_date: formInfo.birth_date,
              gender: formInfo.gender,
              birth_time: formInfo.birth_time || '',
              chinese_name: formInfo.chinese_name || '',
              mbti: formInfo.mbti || ''
            },
            replace: true
          })
        } else {
          console.log('[Router Guard] 비로그인 + formData 없음 → 계산 페이지로')
          next({ name: 'fortune-calculate', query: { redirect: to.fullPath }, replace: true })
        }
        return
      }
    }

    console.log('[Router Guard] 운세 모두 있음 → 통과')
  }

  console.log('[Router Guard] 통과')
  next()
})

export default router
