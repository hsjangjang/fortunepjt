<template>
  <div id="toast-container" class="toast-container-vue"></div>
</template>

<script setup>
import { onMounted } from 'vue'

// Toast 생성 함수를 전역으로 노출
const showToast = (message, type = 'info') => {
  const container = document.getElementById('toast-container')
  if (!container) return

  const toast = document.createElement('div')
  toast.className = `toast-message ${type}`

  let icon = 'fa-info-circle'
  if (type === 'success') icon = 'fa-check-circle'
  if (type === 'error') icon = 'fa-exclamation-circle'
  if (type === 'warning') icon = 'fa-exclamation-triangle'

  toast.innerHTML = `
    <div class="toast-content">
      <i class="fas ${icon}" style="color: var(--${type}-color, var(--info-color))"></i>
      <span>${message}</span>
    </div>
    <i class="fas fa-times toast-close" onclick="this.parentElement.remove()"></i>
  `

  container.appendChild(toast)

  // Trigger animation
  setTimeout(() => toast.classList.add('show'), 10)

  // Auto remove
  setTimeout(() => {
    toast.classList.remove('show')
    setTimeout(() => toast.remove(), 500)
  }, 3000)
}

// 전역 함수로 등록
if (typeof window !== 'undefined') {
  window.showToast = showToast
}

defineExpose({
  showToast
})
</script>

<style>
:root {
  --primary-color: #7c3aed;
  --secondary-color: #a78bfa;
  --success-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;
  --info-color: #3b82f6;
}

.toast-container-vue {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
}

.toast-message {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-left: 5px solid var(--primary-color);
  border-radius: 10px;
  padding: 15px 25px;
  margin-bottom: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 300px;
  transform: translateX(120%);
  transition: transform 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.toast-message.show {
  transform: translateX(0);
}

.toast-message.success {
  border-left-color: var(--success-color);
}

.toast-message.error {
  border-left-color: var(--danger-color);
}

.toast-message.warning {
  border-left-color: var(--warning-color);
}

.toast-message.info {
  border-left-color: var(--info-color);
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  color: #333;
}

.toast-close {
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s;
  color: #666;
}

.toast-close:hover {
  opacity: 1;
}
</style>
