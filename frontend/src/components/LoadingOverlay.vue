<template>
  <div v-if="isVisible" id="global-loading-overlay" class="loading-overlay">
    <div class="spinner-border text-warning loading-spinner" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <h3 class="mt-4 fw-bold text-warning">
      <i class="fas fa-sparkles fa-spin"></i> 운세 생성 중...
    </h3>
    <p class="text-white-50 mt-2">잠시만 기다려주세요</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const isVisible = ref(false)

const show = () => {
  isVisible.value = true
}

const hide = () => {
  isVisible.value = false
}

// 전역 함수로 등록
if (typeof window !== 'undefined') {
  window.showLoadingOverlay = show
  window.hideLoadingOverlay = hide
}

// 10초 후 자동으로 숨기기 (안전장치)
let autoHideTimer = null

const startAutoHide = () => {
  if (autoHideTimer) clearTimeout(autoHideTimer)
  autoHideTimer = setTimeout(() => {
    hide()
  }, 10000)
}

onMounted(() => {
  // 페이지 로드 완료 시 숨기기
  window.addEventListener('load', hide)
  window.addEventListener('pageshow', hide)
})

onUnmounted(() => {
  window.removeEventListener('load', hide)
  window.removeEventListener('pageshow', hide)
  if (autoHideTimer) clearTimeout(autoHideTimer)
})

defineExpose({
  show,
  hide,
  startAutoHide
})
</script>

<style scoped>
.loading-overlay {
  display: flex;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  z-index: 9999;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  color: white;
  backdrop-filter: blur(5px);
}

.loading-spinner {
  width: 4rem;
  height: 4rem;
  border-width: 0.4rem;
}
</style>
