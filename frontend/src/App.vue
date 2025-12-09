<template>
  <div id="app">
    <!-- Background Elements - Django base.html과 동일 -->
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: -1; overflow: hidden;">
      <div style="position: absolute; top: -10%; left: -10%; width: 50%; height: 50%; background: radial-gradient(circle, rgba(124, 58, 237, 0.2) 0%, transparent 70%); filter: blur(80px);"></div>
      <div style="position: absolute; bottom: -10%; right: -10%; width: 50%; height: 50%; background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%); filter: blur(80px);"></div>
    </div>

    <!-- Toast Container - Django base.html과 동일 -->
    <div id="toast-container" style="position: fixed; top: 20px; right: 20px; z-index: 10000;"></div>

    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useFortuneStore } from '@/stores/fortune'

const authStore = useAuthStore()
const fortuneStore = useFortuneStore()

onMounted(async () => {
  // 인증 상태 초기화는 main.js에서 라우터 설정 전에 수행됨
  // Django 세션의 운세 데이터와 동기화
  if (authStore.isAuthenticated) {
    await fortuneStore.checkTodayFortune()
  }
})
</script>

<style>
/* Django style.css를 import했으므로 추가 스타일 불필요 */

/* 모바일 좌우 여백 최적화 - 전역 스타일 */
@media (max-width: 768px) {
  /* 컨테이너 좌우 패딩 축소 */
  .container, .container-fluid {
    padding-left: 8px !important;
    padding-right: 8px !important;
  }

  /* row 좌우 마진/패딩 축소 */
  .row {
    margin-left: -4px !important;
    margin-right: -4px !important;
  }

  .row > [class*="col-"] {
    padding-left: 4px !important;
    padding-right: 4px !important;
  }

  /* glass-card 좌우 패딩 축소 (70% 수준) */
  .glass-card {
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
  }

  /* responsive-padding 클래스 (기존 3% -> 2%) */
  .responsive-padding {
    padding: 1.2rem 0.6rem !important;
  }

  /* px-1 클래스 모바일에서 더 축소 */
  .px-1 {
    padding-left: 0.15rem !important;
    padding-right: 0.15rem !important;
  }
}
</style>
