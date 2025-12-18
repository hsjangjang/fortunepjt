<template>
  <div class="fortune-circle">
    <svg width="220" height="220">
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
        </linearGradient>
      </defs>
      <circle cx="110" cy="110" r="100" class="fortune-circle-bg"></circle>
      <circle cx="110" cy="110" r="100" class="fortune-circle-progress"
              :data-score="score || 0"></circle>
    </svg>
    <div class="fortune-score-text">
      <div class="score">{{ displayScore }}</div>
      <div class="label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  score: {
    type: Number,
    default: 0
  },
  label: {
    type: String,
    default: '점'
  },
  animate: {
    type: Boolean,
    default: true
  }
})

const displayScore = ref(0)

const animateScore = () => {
  if (!props.animate) {
    displayScore.value = props.score
    return
  }

  const target = props.score || 0
  const duration = 1500
  const startTime = Date.now()

  const tick = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easeOut = 1 - Math.pow(1 - progress, 3)
    displayScore.value = Math.round(target * easeOut)

    if (progress < 1) {
      requestAnimationFrame(tick)
    }
  }

  requestAnimationFrame(tick)

  // SVG 원형 프로그레스 애니메이션
  setTimeout(() => {
    const circle = document.querySelector('.fortune-circle-progress')
    if (circle) {
      const offset = 628 - (628 * target / 100)
      circle.style.strokeDashoffset = offset
    }
  }, 100)
}

watch(() => props.score, () => {
  animateScore()
})

onMounted(() => {
  animateScore()
})
</script>

<style scoped>
.fortune-circle {
  position: relative;
  width: 220px;
  height: 220px;
  margin: 0 auto;
}

.fortune-circle svg {
  transform: rotate(0deg) scaleY(1);
  transform-origin: center;
  filter: drop-shadow(0 0 10px rgba(124, 58, 237, 0.3));
}

.fortune-circle-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 15;
}

.fortune-circle-progress {
  fill: none;
  stroke: url(#gradient);
  stroke-width: 15;
  stroke-linecap: round;
  stroke-dasharray: 628;
  stroke-dashoffset: 628;
  transition: stroke-dashoffset 2s ease-out;
}

.fortune-score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.fortune-score-text .score {
  font-size: 4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(167, 139, 250, 0.5);
}

.fortune-score-text .label {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 300;
}
</style>
