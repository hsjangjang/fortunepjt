<template>
  <!-- Navigation - Django base.html과 동일 -->
  <nav ref="navbarRef" class="navbar navbar-expand-lg navbar-dark fixed-top" @mouseleave="handleNavbarMouseLeave" @mouseenter="handleNavbarMouseEnter">
    <div class="container">
      <router-link class="navbar-brand" to="/">
        <MoonStar class="text-warning me-2" :size="24" />
        <span class="text-gradient fw-bold">Fortune Life</span>
      </router-link>
      <button class="navbar-toggler border-0" type="button" @click="toggleMobileMenu">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div ref="collapseRef" class="collapse navbar-collapse" :class="{ show: mobileMenuOpen, closing: mobileMenuClosing }" @mouseleave="handleCollapseMouseLeave" @mouseenter="handleNavbarMouseEnter">
        <ul class="navbar-nav ms-auto align-items-center">
          <template v-if="authStore.isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/fortune/today">
                <Sparkles class="me-1" :size="18" /> 오늘의 운세
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/fortune/item-check">
                <Diamond class="me-1" :size="18" /> 행운템 분석
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/recommendations/ootd">
                <Shirt class="me-1" :size="18" /> OOTD
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/recommendations/menu">
                <UtensilsCrossed class="me-1" :size="18" /> 메뉴
              </router-link>
            </li>
            <li class="nav-item dropdown ms-lg-3">
              <a class="nav-link dropdown-toggle btn btn-outline-light px-3 py-2 rounded-pill" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown" @click.prevent="toggleUserDropdown">
                <UserCircle class="me-1" :size="18" /> {{ userFullName }}님
              </a>
              <ul class="dropdown-menu dropdown-menu-end glass-card border-0 mt-2" :class="{ show: userDropdownOpen }">
                <li><router-link class="dropdown-item text-white" to="/profile"><IdCard class="me-2" :size="16" /> 프로필</router-link></li>
                <li><router-link class="dropdown-item text-white" to="/items/upload"><PlusCircle class="me-2" :size="16" /> 아이템 등록</router-link></li>
                <li><hr class="dropdown-divider bg-light opacity-25"></li>
                <li><a class="dropdown-item text-danger" href="#" @click.prevent="handleLogout"><LogOut class="me-2" :size="16" /> 로그아웃</a></li>
              </ul>
            </li>
          </template>

          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link px-3" to="/login">로그인</router-link>
            </li>
            <li class="nav-item ms-lg-3">
              <router-link class="nav-link btn btn-primary text-white px-4" to="/register">
                회원가입
              </router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import {
  MoonStar, Sparkles, Diamond, Shirt, UtensilsCrossed,
  UserCircle, IdCard, PlusCircle, LogOut
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const { showToast } = useToast()

// 사용자 전체 이름 (성 + 이름)
const userFullName = computed(() => {
  const user = authStore.user
  if (!user) return authStore.username

  const lastName = user.last_name || ''
  const firstName = user.first_name || ''
  const fullName = (lastName + firstName).trim()

  return fullName || authStore.username
})

const mobileMenuOpen = ref(false)
const mobileMenuClosing = ref(false)
const userDropdownOpen = ref(false)
const navbarRef = ref(null)
const collapseRef = ref(null)
let closeTimeout = null
let isClosing = false

// 메뉴 열기
const openMenu = () => {
  if (!mobileMenuOpen.value && !isClosing) {
    mobileMenuClosing.value = false
    mobileMenuOpen.value = true
  }
  cancelClose()
}

// 메뉴 닫기 (애니메이션 포함)
const closeMenu = () => {
  if (mobileMenuOpen.value && !isClosing) {
    isClosing = true
    mobileMenuClosing.value = true
    setTimeout(() => {
      mobileMenuOpen.value = false
      mobileMenuClosing.value = false
      isClosing = false
    }, 400)
  }
}

// 닫기 예약 (딜레이 후 닫힘) - 즉시 닫기
const scheduleClose = () => {
  if (closeTimeout) {
    clearTimeout(closeTimeout)
  }
  // 마우스가 바깥으로 나가면 즉시 닫기 (딜레이 없음)
  closeMenu()
}

// 닫기 취소
const cancelClose = () => {
  if (closeTimeout) {
    clearTimeout(closeTimeout)
    closeTimeout = null
  }
}

// 마우스가 navbar 또는 collapse 영역 내에 있는지 확인
const isInsideNavbar = (element) => {
  if (!element) return false
  const navbar = navbarRef.value
  const collapse = collapseRef.value
  return (navbar && navbar.contains(element)) || (collapse && collapse.contains(element))
}

const toggleMobileMenu = () => {
  if (mobileMenuOpen.value) {
    closeMenu()
  } else {
    openMenu()
  }
}

const toggleUserDropdown = () => {
  userDropdownOpen.value = !userDropdownOpen.value
}

// navbar에서 마우스 떠날 때
const handleNavbarMouseLeave = (e) => {
  // 마우스가 collapse로 이동한 경우 닫지 않음
  if (!isInsideNavbar(e.relatedTarget)) {
    scheduleClose()
  }
}

// collapse에서 마우스 떠날 때
const handleCollapseMouseLeave = (e) => {
  // 마우스가 navbar로 이동한 경우 닫지 않음
  if (!isInsideNavbar(e.relatedTarget)) {
    scheduleClose()
  }
}

// navbar 또는 collapse에 마우스 들어오면 닫기 취소
const handleNavbarMouseEnter = () => {
  cancelClose()
}

// 컴포넌트 언마운트 시 타이머 정리
onUnmounted(() => {
  if (closeTimeout) {
    clearTimeout(closeTimeout)
  }
})

const handleLogout = async () => {
  // UI 상태 초기화
  userDropdownOpen.value = false
  mobileMenuOpen.value = false

  // 로그아웃 API 호출 먼저 (인증 상태 변경)
  await authStore.logout()

  // 홈으로 이동 (라우터 가드가 인증 필요 페이지 접근 차단)
  await router.push('/')

  // Django: messages.success(request, '로그아웃되었습니다.')
  showToast('로그아웃되었습니다.', 'success')
}
</script>

<style scoped>
/* 네비게이션 부드러운 애니메이션 */
.navbar-collapse {
  transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease-in-out;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
}

.navbar-collapse.show {
  max-height: 500px;
  opacity: 1;
}

.navbar-collapse.closing {
  max-height: 0;
  opacity: 0;
}

/* 모바일에서 네비게이션 항목 애니메이션 */
@media (max-width: 991.98px) {
  .navbar-collapse.show .nav-item {
    animation: slideInDown 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  }

  .navbar-collapse.closing .nav-item {
    animation: slideOutUp 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  }
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideOutUp {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

/* 데스크톱에서는 기본 동작 유지 */
@media (min-width: 992px) {
  .navbar-collapse {
    max-height: none !important;
    opacity: 1 !important;
    overflow: visible !important;
  }
}
</style>
