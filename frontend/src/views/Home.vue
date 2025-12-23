<template>
  <DefaultLayout>
    <!-- 스크롤 컨테이너 -->
    <div class="scroll-container">
      <!-- Hero Section - 고정되어 있다가 스크롤 시 위로 사라짐 -->
      <div class="hero-section" :style="{
        opacity: heroOpacity,
        transform: `scale(${heroScale}) translateY(${heroTranslate}px)`,
        visibility: heroOpacity <= 0 ? 'hidden' : 'visible'
      }">
        <!-- 은하수 반짝이 배경 -->
        <div class="galaxy-sparkles">
          <div v-for="n in 80" :key="'g'+n" class="galaxy-particle" :style="getGalaxyParticleStyle(n)"></div>
        </div>
        <!-- 반짝이는 별 배경 -->
        <div class="stars-container">
          <div v-for="n in 50" :key="n" class="star" :style="getStarStyle(n)"></div>
        </div>
        <div class="hero-content text-center">
          <h1 class="display-title fw-bold mb-4">
            행운을 PICK<span class="star-icon">✨</span><br>당신의 하루를 열어보아요
          </h1>
          <p class="lead mb-5 hero-description">
            사주와 별자리를 분석하여<br>
            당신에게 딱 맞는 <span class="text-white fw-bold">행운의 아이템, OOTD, 메뉴</span>를 추천해드립니다
          </p>
          <div class="d-flex justify-content-center gap-3">
            <router-link to="/fortune/calculate" class="btn btn-lg px-5 fortune-loading-link hero-btn">
              <i class="fas fa-calendar-check me-2"></i> 운세 보기
            </router-link>
          </div>
        </div>
        <!-- 스크롤 안내 화살표 -->
        <div class="scroll-indicator" @click="scrollToFeatures">
          <ChevronDown :size="32" class="bounce" />
        </div>
      </div>

      <!-- Spacer - Hero 높이만큼 공간 확보 -->
      <div class="hero-spacer"></div>

      <!-- Main Features - 스크롤하면 아래에서 올라옴 -->
      <div id="features" class="features-section">
        <div class="row g-4 features-row">
          <!-- 아이템 행운도 -->
          <div class="col-md-4 feature-item" :class="{ 'is-visible': featureVisible[0] }">
            <router-link to="/fortune/item-check" class="glass-card h-100 p-4 text-center position-relative overflow-hidden feature-card text-decoration-none">
              <div class="position-absolute top-0 start-50 translate-middle-x mt-n4" style="width: 100px; height: 100px; background: var(--primary); filter: blur(60px); opacity: 0.4;"></div>
              <div class="feature-content">
                <div class="mb-4 mt-3">
                  <img src="@/assets/images/item_check_icon.png" alt="" class="feature-icon" />
                </div>
                <h4 class="mb-3 text-white">아이템 행운도 분석</h4>
                <p class="text-muted mb-0">
                  내 아이템이 오늘의 행운과<br>
                  얼마나 맞는지 AI가 분석합니다
                </p>
              </div>
              <span class="btn btn-outline-light w-100 feature-btn">
                행운도 측정하기
              </span>
            </router-link>
          </div>

          <!-- OOTD 추천 -->
          <div class="col-md-4 feature-item" :class="{ 'is-visible': featureVisible[1] }">
            <router-link to="/recommendations/ootd" class="glass-card h-100 p-4 text-center position-relative overflow-hidden feature-card text-decoration-none">
              <div class="position-absolute top-0 start-50 translate-middle-x mt-n4" style="width: 100px; height: 100px; background: var(--success); filter: blur(60px); opacity: 0.3;"></div>
              <div class="feature-content">
                <div class="mb-4 mt-3">
                  <img src="@/assets/images/ootd-icon2.png" alt="" class="feature-icon" />
                </div>
                <h4 class="mb-3 text-white">OOTD 추천</h4>
                <p class="text-muted mb-0">
                  행운색과 날씨를 고려한<br>
                  완벽한 코디를 제안합니다
                </p>
              </div>
              <span class="btn btn-outline-light w-100 feature-btn">
                코디 추천받기
              </span>
            </router-link>
          </div>

          <!-- 메뉴 추천 -->
          <div class="col-md-4 feature-item" :class="{ 'is-visible': featureVisible[2] }">
            <router-link to="/recommendations/menu" class="glass-card h-100 p-4 text-center position-relative overflow-hidden feature-card text-decoration-none">
              <div class="position-absolute top-0 start-50 translate-middle-x mt-n4" style="width: 100px; height: 100px; background: var(--warning); filter: blur(60px); opacity: 0.3;"></div>
              <div class="feature-content">
                <div class="mb-4 mt-3 feature-emoji">🍽️</div>
                <h4 class="mb-3 text-white">오늘의 메뉴 추천</h4>
                <p class="text-muted mb-0">
                  오늘의 운세에 맞는<br>
                  행운의 메뉴를 추천합니다
                </p>
              </div>
              <span class="btn btn-outline-light w-100 feature-btn">
                메뉴 추천받기
              </span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { ChevronDown } from 'lucide-vue-next'
import Lenis from 'lenis'

// Hero 애니메이션 값
const heroOpacity = ref(1)
const heroScale = ref(1)
const heroTranslate = ref(0)

// Feature 카드 visible 상태
const featureVisible = reactive([false, false, false])

// 별 스타일 생성 함수 - 화면 전체에 골고루 분산
const getStarStyle = (index) => {
  // 황금각을 이용해 균일하게 분산
  const goldenAngle = 137.508
  const angle = index * goldenAngle
  const radius = Math.sqrt(index / 50) * 50

  // 극좌표를 직교좌표로 변환하여 화면 전체에 분산
  const left = 50 + radius * Math.cos(angle * Math.PI / 180) * 0.9
  const top = 50 + radius * Math.sin(angle * Math.PI / 180) * 0.9

  // 크기와 애니메이션 타이밍 다양화
  const size = 1.5 + (index % 3)
  const delay = (index * 0.15) % 5
  const duration = 2 + (index % 4)

  return {
    left: `${Math.max(2, Math.min(98, left))}%`,
    top: `${Math.max(2, Math.min(98, top))}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

// 은하수 반짝이 스타일 - 대각선 띠 형태로 분포
const getGalaxyParticleStyle = (index) => {
  // 대각선 띠를 따라 분포 (좌상단 -> 우하단)
  const progress = index / 80
  const baseLeft = 10 + progress * 80
  const baseTop = 10 + progress * 80

  // 띠 주변으로 랜덤하게 흩뿌림
  const spread = 15
  const offsetX = (Math.sin(index * 2.5) * spread)
  const offsetY = (Math.cos(index * 3.7) * spread)

  const left = baseLeft + offsetX
  const top = baseTop + offsetY

  const size = 0.5 + (index % 3) * 0.5
  const delay = (index * 0.08) % 4
  const duration = 1.5 + (index % 3)

  return {
    left: `${Math.max(0, Math.min(100, left))}%`,
    top: `${Math.max(0, Math.min(100, top))}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

// Lenis 인스턴스
let lenis = null

// iOS Safari용 RAF ID
let iosRafId = null

// iOS Safari 감지
const isIOSSafari = () => {
  const ua = navigator.userAgent
  const isIOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  const isSafari = /Safari/.test(ua) && !/Chrome|CriOS|FxiOS/.test(ua)
  return isIOS && isSafari
}

// 스크롤 시 애니메이션 처리
const handleScroll = (scrollY) => {
  const windowHeight = window.innerHeight

  // === Hero 섹션 애니메이션 ===
  const heroEnd = windowHeight * 0.6
  const progress = Math.min(scrollY / heroEnd, 1)
  heroOpacity.value = 1 - progress
  heroScale.value = 1 - (progress * 0.1)
  heroTranslate.value = -scrollY * 0.3

  // === Feature 카드 애니메이션 ===
  // 모바일 여부 확인 (768px 이하)
  const isMobile = window.innerWidth <= 768

  // 모바일에서는 카드가 세로로 배치되므로 트리거 간격을 더 넓게
  const triggers = isMobile
    ? [
        windowHeight * 0.1,
        windowHeight * 0.35,
        windowHeight * 0.6
      ]
    : [
        windowHeight * 0.15,
        windowHeight * 0.25,
        windowHeight * 0.35
      ]

  for (let i = 0; i < 3; i++) {
    if (scrollY >= triggers[i]) {
      featureVisible[i] = true
    } else {
      featureVisible[i] = false
    }
  }
}

// 화살표 클릭 시 스크롤
const scrollToFeatures = () => {
  if (lenis) {
    lenis.scrollTo('#features', {
      offset: -100,
      duration: 1.5
    })
  } else {
    // iOS Safari용 네이티브 스크롤
    const el = document.getElementById('features')
    if (el) {
      const top = el.getBoundingClientRect().top + window.scrollY - 100
      window.scrollTo({ top, behavior: 'smooth' })
    }
  }
}

// RAF 루프 (Lenis용)
const raf = (time) => {
  lenis?.raf(time)
  requestAnimationFrame(raf)
}

// iOS Safari용 RAF 폴링 루프 (스크롤 이벤트 쓰로틀링 우회)
const iosRafLoop = () => {
  handleScroll(window.scrollY)
  iosRafId = requestAnimationFrame(iosRafLoop)
}

onMounted(() => {
  // iOS Safari 여부 확인
  const useNativeScroll = isIOSSafari()
  const isMobile = window.innerWidth <= 768

  if (useNativeScroll) {
    // iOS Safari: RAF 폴링으로 매 프레임 스크롤 위치 체크 (쓰로틀링 우회)
    iosRafId = requestAnimationFrame(iosRafLoop)
  } else {
    // 다른 브라우저: Lenis 사용
    lenis = new Lenis({
      duration: isMobile ? 2.0 : 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      smoothWheel: true
    })

    // 스크롤 이벤트 연결
    lenis.on('scroll', ({ scroll }) => {
      handleScroll(scroll)
    })

    // RAF 시작
    requestAnimationFrame(raf)
  }

  // 초기 상태 설정
  handleScroll(window.scrollY)
})

onUnmounted(() => {
  if (lenis) {
    lenis.destroy()
    lenis = null
  }
  if (iosRafId) {
    cancelAnimationFrame(iosRafId)
    iosRafId = null
  }
})
</script>

<style scoped>
.scroll-container {
  position: relative;
  background: linear-gradient(180deg, #000005 0%, #020617 30%, #0a0a1a 100%);
  min-height: 100vh;
  margin-left: calc(-50vw + 50%);
  margin-right: calc(-50vw + 50%);
  width: 100vw;
}

/* 은하수 반짝이 */
.galaxy-sparkles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.galaxy-particle {
  position: absolute;
  background: white;
  border-radius: 50%;
  opacity: 0;
  animation: sparkle ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% {
    opacity: 0;
    transform: scale(0);
  }
  50% {
    opacity: 0.7;
    transform: scale(1);
    box-shadow: 0 0 4px 1px rgba(200, 180, 255, 0.5);
  }
}

/* 반짝이는 별 배경 */
.stars-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.star {
  position: absolute;
  background: radial-gradient(circle, #ffffff 0%, rgba(255, 255, 255, 0.8) 50%, transparent 100%);
  border-radius: 50%;
  opacity: 0;
  animation: twinkle ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% {
    opacity: 0;
    transform: scale(0.3);
    filter: blur(0px);
  }
  50% {
    opacity: 0.9;
    transform: scale(1);
    filter: blur(0.5px);
    box-shadow: 0 0 8px 2px rgba(255, 255, 255, 0.4);
  }
}

/* Hero Section - 화면 전체 정중앙 */
.hero-section {
  position: fixed;
  top: 76px;
  left: 0;
  right: 0;
  height: calc(100vh - 76px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 1rem;
  z-index: 1;
  will-change: transform, opacity;
}

.hero-content {
  max-width: 800px;
}

/* Hero 설명 문구 색상 */
.hero-description {
  color: #c1c1c1;
}

/* Hero 버튼 - 비활성 상태는 outline-light 스타일 */
.hero-btn {
  display: inline-block;
  color: #fff;
  background-color: transparent;
  border: 1px solid #fff;
}

.hero-btn:hover,
.hero-btn:focus,
.hero-btn:active {
  color: #fff;
  background-color: var(--primary);
  border-color: var(--primary);
}

/* Hero 높이만큼 공간 확보 (카드가 보이도록 줄임) */
.hero-spacer {
  height: 55vh;
}

/* 스크롤 안내 화살표 */
.scroll-indicator {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: color 0.3s;
}

.scroll-indicator:hover {
  color: rgba(255, 255, 255, 0.8);
}

.bounce {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

/* Features Section - 화면 정중앙 배치 */
.features-section {
  position: relative;
  z-index: 2;
  min-height: calc(100vh - 76px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 1rem;
  background: transparent;
}

.features-row {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* Feature Item - 슈우웅 부드러운 애니메이션 */
.feature-item {
  opacity: 0;
  transform: translateY(100px) translateZ(0);
  transition:
    opacity 1s cubic-bezier(0.16, 1, 0.3, 1),
    transform 1s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: transform, opacity;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

/* 첫 번째 카드 */
.feature-item:nth-child(1) {
  transition-delay: 0s;
}

/* 두 번째 카드 */
.feature-item:nth-child(2) {
  transition-delay: 0.1s;
}

/* 세 번째 카드 */
.feature-item:nth-child(3) {
  transition-delay: 0.2s;
}

.feature-item.is-visible {
  opacity: 1;
  transform: translateY(0) translateZ(0);
}

/* 피처 아이콘 */
.feature-icon {
  width: 72px;
  height: 72px;
  object-fit: contain;
}

/* 별 아이콘 */
.star-icon {
  text-shadow: 0 0 10px rgba(251, 191, 36, 0.8), 0 0 20px rgba(251, 191, 36, 0.5);
}

/* 메인 피처 카드 */
.feature-card {
  display: flex;
  flex-direction: column;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.feature-card:hover {
  transform: translateY(-12px);
  box-shadow: 0 25px 50px rgba(124, 58, 237, 0.25);
}

.feature-content {
  flex-shrink: 0;
  margin-bottom: 1.5rem;
}

.feature-btn {
  margin-top: auto;
}

/* 이모지 아이콘 */
.feature-emoji {
  font-size: 3.5rem;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 모바일 대응 */
@media (max-width: 768px) {
  .hero-section {
    top: 60px;
    height: calc(100vh - 60px);
  }

  .hero-spacer {
    height: 50vh;
  }

  .features-section {
    min-height: calc(100vh - 60px);
    padding: 2rem 1rem;
  }

  .scroll-indicator {
    bottom: 30px;
  }

  .feature-item {
    transform: translateY(60px) translateZ(0);
  }
}
</style>

<style>
/* Lenis 기본 스타일 */
html.lenis, html.lenis body {
  height: auto;
}

.lenis.lenis-smooth {
  scroll-behavior: auto !important;
}

.lenis.lenis-smooth [data-lenis-prevent] {
  overscroll-behavior: contain;
}

.lenis.lenis-stopped {
  overflow: hidden;
}

.lenis.lenis-scrolling iframe {
  pointer-events: none;
}
</style>
