<template>
  <div class="tab-pane fade" :class="{ 'show active': isActive }" :id="tabId">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="text-white">
        <i :class="iconClass" :style="{ color: iconColor }"></i>
        {{ title }}
      </h4>
      <span class="text-white opacity-50 small">{{ score }} / 100</span>
    </div>
    <div class="sub-score-bar">
      <span class="score-text">{{ score }}%</span>
      <div class="sub-score-fill" :style="barStyle" :data-target="score"></div>
    </div>
    <p class="fortune-text" v-html="formattedText"></p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tabId: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  iconColor: {
    type: String,
    default: '#a78bfa'
  },
  score: {
    type: Number,
    default: 70
  },
  text: {
    type: String,
    default: ''
  },
  gradientColors: {
    type: Array,
    default: () => ['#7c3aed', '#a78bfa']
  },
  colorClass: {
    type: String,
    default: 'color-purple'
  },
  isActive: {
    type: Boolean,
    default: false
  },
  periodType: {
    type: String,
    default: 'daily'
  }
})

const iconClass = computed(() => `fas ${props.icon} me-2`)

const barStyle = computed(() => ({
  width: `${props.score}%`,
  background: `linear-gradient(90deg, ${props.gradientColors[0]}, ${props.gradientColors[1]})`
}))

// 운세 텍스트 포맷팅 (주간/월간용 리스트 처리 포함)
const formattedText = computed(() => {
  if (!props.text) return ''

  // 주간/월간 운세: 요일/주차별 구분이 있는 경우
  if (props.periodType !== 'daily' && props.text.includes('\n')) {
    const lines = props.text.split('\n').filter(line => line.trim())
    const today = new Date()
    const currentDay = today.getDay()
    const dayNames = ['일', '월', '화', '수', '목', '금', '토']

    const items = lines.map((line, index) => {
      const isToday = props.periodType === 'weekly' && index === (currentDay === 0 ? 6 : currentDay - 1)
      return `<li${isToday ? ' class="today-highlight"' : ''}>${isToday ? '<strong>' : ''}${line}${isToday ? '</strong>' : ''}</li>`
    }).join('')

    return `<ul class="fortune-list ${props.colorClass}">${items}</ul>`
  }

  return props.text
})
</script>

<style scoped>
.sub-score-bar {
  position: relative;
  height: 25px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  overflow: hidden;
  margin: 15px 0;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
}

.sub-score-fill {
  height: 100%;
  border-radius: 20px;
  transition: width 1.5s ease-out;
  position: relative;
}

.sub-score-bar .score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: bold;
  font-size: 0.85rem;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  z-index: 1;
}

.fortune-text {
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  letter-spacing: -0.02em;
  text-align: justify;
  margin-top: 25px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.fortune-text :deep(.fortune-list) {
  list-style: none;
  padding: 0;
  margin: 0;
}

.fortune-text :deep(.fortune-list li) {
  position: relative;
  padding-left: 1.5rem;
  margin-bottom: 0.8rem;
  text-align: left;
}

.fortune-text :deep(.fortune-list li):last-child {
  margin-bottom: 0;
}

.fortune-text :deep(.fortune-list li)::before {
  content: '';
  position: absolute;
  left: 0;
  color: #a78bfa;
  font-size: 1.2rem;
  line-height: 1.6;
}

.fortune-text :deep(.fortune-list.color-purple li)::before { color: #a78bfa; }
.fortune-text :deep(.fortune-list.color-yellow li)::before { color: #fbbf24; }
.fortune-text :deep(.fortune-list.color-red li)::before { color: #f87171; }
.fortune-text :deep(.fortune-list.color-blue li)::before { color: #60a5fa; }
.fortune-text :deep(.fortune-list.color-green li)::before { color: #34d399; }
.fortune-text :deep(.fortune-list.color-teal li)::before { color: #2dd4bf; }

.fortune-text :deep(.fortune-list li.today-highlight strong) {
  color: #fff;
  font-weight: 700;
}
</style>
