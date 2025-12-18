<template>
  <div class="lucky-colors-section">
    <h4 class="text-white text-center mb-2">
      <i class="fas fa-palette text-primary me-2" style="color: #a78bfa !important;"></i>
      {{ title }}
    </h4>
    <p v-if="subtitle" class="text-center text-white opacity-75 mb-5">{{ subtitle }}</p>

    <div v-if="colors && colors.length > 0" class="d-flex justify-content-center align-items-center gap-3 gap-md-5">
      <div v-for="color in colors" :key="color" class="text-center">
        <div class="lucky-color-circle" :style="`background: ${getColorBackground(color)};`"></div>
        <p class="mt-3 mb-0 fw-bold text-white responsive-text-shadow">{{ color }}</p>
      </div>
    </div>
    <div v-else class="d-flex justify-content-center align-items-center gap-3 gap-md-5">
      <div v-for="fallback in fallbackColors" :key="fallback.name" class="text-center">
        <div class="lucky-color-circle" :style="`background: ${fallback.hex};`"></div>
        <p class="mt-3 mb-0 fw-bold text-white responsive-text-shadow">{{ fallback.name }}</p>
      </div>
    </div>

    <p v-if="footerText" class="text-center text-white opacity-75 mt-4 mb-0">
      {{ footerText }}
    </p>
  </div>
</template>

<script setup>
import { getColorBackground } from '@/utils/colors'

defineProps({
  title: {
    type: String,
    default: '오늘의 행운색'
  },
  subtitle: {
    type: String,
    default: ''
  },
  colors: {
    type: Array,
    default: () => []
  },
  footerText: {
    type: String,
    default: ''
  },
  fallbackColors: {
    type: Array,
    default: () => [
      { name: '하늘색', hex: '#87CEEB' },
      { name: '연두색', hex: '#90EE90' },
      { name: '보라색', hex: '#800080' }
    ]
  }
})
</script>

<style scoped>
.lucky-color-circle {
  width: min(100px, 20vw);
  height: min(100px, 20vw);
  min-width: 40px;
  min-height: 40px;
  border-radius: 50%;
  margin: 0 auto;
  box-shadow: 0 8px 20px rgba(0,0,0,0.3), inset 0 -5px 10px rgba(0,0,0,0.2), inset 0 5px 10px rgba(255,255,255,0.2);
  border: 3px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.responsive-text-shadow {
  font-size: 1.1rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

@media (max-width: 768px) {
  .lucky-color-circle {
    width: 60px;
    height: 60px;
    border-width: 2px;
  }

  .responsive-text-shadow {
    font-size: 0.9rem;
  }
}
</style>
