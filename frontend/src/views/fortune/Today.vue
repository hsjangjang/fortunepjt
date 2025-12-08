<template>
  <DefaultLayout>
    <div class="container py-5">
      <div class="row justify-content-center mb-5">
        <div class="col-lg-8 text-center">
          <h1 class="display-4 text-white mb-3 fw-bold">
            <i class="fas fa-crystal-ball text-primary me-3"></i>
            오늘의 운세
          </h1>
          <p class="lead text-white opacity-75">당신의 오늘을 빛낼 운세를 확인해보세요</p>
        </div>
      </div>

      <div v-if="fortune" class="row justify-content-center mb-4">
        <div class="col-lg-8">
          <div class="glass-card p-4 p-md-5">
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
                        :data-score="fortune.fortune_score || 0"></circle>
              </svg>
              <div class="fortune-score-text">
                <div class="score">{{ displayScore }}</div>
                <div class="label">점</div>
              </div>
            </div>

            <div class="row text-center mt-5 g-3 justify-content-center">
              <div class="col-md-4">
                <h6 class="text-primary-light mb-2">별자리</h6>
                <span class="badge rounded-pill bg-primary bg-opacity-25 border border-primary text-white fs-5 px-4 py-2" style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(167, 139, 250, 0.2)); border-color: rgba(167, 139, 250, 0.5) !important;">
                  {{ fortune.zodiac_sign || '-' }}
                </span>
              </div>
              <div class="col-md-4">
                <h6 class="text-primary-light mb-2">띠</h6>
                <span class="badge rounded-pill bg-primary bg-opacity-25 border border-primary text-white fs-5 px-4 py-2" style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(167, 139, 250, 0.2)); border-color: rgba(167, 139, 250, 0.5) !important;">
                  {{ fortune.chinese_zodiac || '-' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Fortune Details Tabs -->
      <div v-if="fortune" class="row justify-content-center mb-4">
        <div class="col-lg-8">
          <div class="glass-card overflow-hidden">
            <div class="card-header border-0 p-4">
              <ul class="nav nav-pills fortune-tabs nav-fill gap-2" role="tablist">
                <li class="nav-item">
                  <a class="nav-link active" id="tab-total" data-bs-toggle="tab" href="#total">종합운</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" id="tab-money" data-bs-toggle="tab" href="#money">재물운</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" id="tab-love" data-bs-toggle="tab" href="#love">연애운</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" id="tab-study" data-bs-toggle="tab" href="#study">학업운</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" id="tab-work" data-bs-toggle="tab" href="#work">직장운</a>
                </li>
              </ul>
            </div>
            <div class="card-body p-4 p-md-5">
              <div class="tab-content">
                <!-- 종합운 -->
                <div class="tab-pane fade show active" id="total">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-star text-primary me-2" style="color: #a78bfa !important;"></i> 종합운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_score || 0 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_score || 0 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_score || 0}%; background: linear-gradient(90deg, #7c3aed, #a78bfa);`" :data-target="fortune.fortune_score || 0"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.total || '오늘의 운세 내용')"></p>
                </div>

                <!-- 재물운 -->
                <div class="tab-pane fade" id="money">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-coins text-warning me-2" style=" -webkit-text-stroke: 1px rgba(255,255,255,0.1);"></i> 재물운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_scores?.money || 70 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_scores?.money || 70 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_scores?.money || 70}%; background: linear-gradient(90deg, #f59e0b, #fbbf24);`" :data-target="fortune.fortune_scores?.money || 70"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.money || '재물운 내용')"></p>
                </div>

                <!-- 연애운 -->
                <div class="tab-pane fade" id="love">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-heart text-danger me-2"></i> 연애운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_scores?.love || 65 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_scores?.love || 65 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_scores?.love || 65}%; background: linear-gradient(90deg, #ef4444, #f87171);`" :data-target="fortune.fortune_scores?.love || 65"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.love || '연애운 내용')"></p>
                </div>

                <!-- 학업운 -->
                <div class="tab-pane fade" id="study">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-graduation-cap text-info me-2"></i> 학업운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_scores?.study || 75 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_scores?.study || 75 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_scores?.study || 75}%; background: linear-gradient(90deg, #3b82f6, #60a5fa);`" :data-target="fortune.fortune_scores?.study || 75"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.study || '학업운 내용')"></p>
                </div>

                <!-- 직장운 -->
                <div class="tab-pane fade" id="work">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-briefcase text-success me-2"></i> 직장운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_scores?.work || 80 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_scores?.work || 80 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_scores?.work || 80}%; background: linear-gradient(90deg, #10b981, #34d399);`" :data-target="fortune.fortune_scores?.work || 80"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.work || '직장운 내용')"></p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Lucky Colors Section -->
      <div v-if="fortune" class="row justify-content-center mb-4">
        <div class="col-lg-8">
          <div class="glass-card">
            <div class="card-body p-4 p-md-5">
              <h4 class="text-white text-center mb-4">
                <i class="fas fa-palette text-primary me-2" style="color: #a78bfa !important;"></i>
                오늘의 행운색
              </h4>
              <h5 class="text-center text-white opacity-90 mb-4">오늘 당신에게 행운을 가져다 줄 색상</h5>

              <div v-if="fortune.lucky_colors && fortune.lucky_colors.length > 0" class="d-flex justify-content-center flex-wrap">
                <div v-for="color in fortune.lucky_colors" :key="color" class="m-3 text-center">
                  <div :style="`width: 100px; height: 100px; border-radius: 50%; margin: 0 auto; box-shadow: 0 8px 20px rgba(0,0,0,0.3), inset 0 -5px 10px rgba(0,0,0,0.2), inset 0 5px 10px rgba(255,255,255,0.2); border: 3px solid rgba(255, 255, 255, 0.3); background: ${getColorHex(color)};`"></div>
                  <p class="mt-3 mb-0 fw-bold text-white" style="font-size: 1.1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">{{ color }}</p>
                </div>
              </div>
              <div v-else class="d-flex justify-content-center flex-wrap">
                <div class="m-3 text-center">
                  <div style="width: 100px; height: 100px; border-radius: 50%; margin: 0 auto; box-shadow: 0 8px 20px rgba(0,0,0,0.3), inset 0 -5px 10px rgba(0,0,0,0.2), inset 0 5px 10px rgba(255,255,255,0.2); border: 3px solid rgba(255, 255, 255, 0.3); background: #87CEEB;"></div>
                  <p class="mt-3 mb-0 fw-bold text-white" style="font-size: 1.1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">하늘색</p>
                </div>
                <div class="m-3 text-center">
                  <div style="width: 100px; height: 100px; border-radius: 50%; margin: 0 auto; box-shadow: 0 8px 20px rgba(0,0,0,0.3), inset 0 -5px 10px rgba(0,0,0,0.2), inset 0 5px 10px rgba(255,255,255,0.2); border: 3px solid rgba(255, 255, 255, 0.3); background: #90EE90;"></div>
                  <p class="mt-3 mb-0 fw-bold text-white" style="font-size: 1.1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">연두색</p>
                </div>
                <div class="m-3 text-center">
                  <div style="width: 100px; height: 100px; border-radius: 50%; margin: 0 auto; box-shadow: 0 8px 20px rgba(0,0,0,0.3), inset 0 -5px 10px rgba(0,0,0,0.2), inset 0 5px 10px rgba(255,255,255,0.2); border: 3px solid rgba(255, 255, 255, 0.3); background: #800080;"></div>
                  <p class="mt-3 mb-0 fw-bold text-white" style="font-size: 1.1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">보라색</p>
                </div>
              </div>

              <p class="text-center text-white opacity-75 mt-4 mb-0">
                이 색상들을 옷이나 액세서리에 활용하면 오늘 하루가 더욱 행운으로 가득할 것입니다!
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Lucky Item Section -->
      <div v-if="fortune" class="row justify-content-center mb-4">
        <div class="col-lg-8">
          <div class="glass-card">
            <div class="card-body p-4 p-md-5">
              <h4 class="text-white text-center mb-4">
                <i class="fas fa-gem text-primary me-2" style="color: #a78bfa !important;"></i>
                오늘의 행운 아이템
              </h4>
              <p class="text-center text-white opacity-75 mb-4">오늘 당신에게 행운을 가져다 줄 아이템들</p>

              <div v-if="fortune.lucky_item" class="row g-4 justify-content-center align-items-stretch">
                <div class="col-md-5 d-flex">
                  <div class="lucky-item-card text-center p-4 w-100 d-flex flex-column"
                       style="background: rgba(124, 58, 237, 0.15); border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 15px; cursor: pointer;"
                       @click="showMainItemDesc = !showMainItemDesc">
                    <div class="mb-2">
                      <span class="badge" style="background: #a78bfa; color: white;">운세 기반</span>
                    </div>
                    <span class="lucky-item-icon d-block mb-3">{{ fortune.lucky_item?.emoji || '🎁' }}</span>
                    <h5 class="text-white fw-bold mb-2" style="word-break: keep-all;">{{ fortune.lucky_item?.main || '행운 아이템' }}</h5>
                    <div class="item-desc-toggle" :class="{ 'show': showMainItemDesc }">
                      <p class="text-white opacity-75 small mb-0" v-html="formatDescription(fortune.lucky_item?.description || '', fortune.lucky_item?.main)"></p>
                    </div>
                    <div class="toggle-hint mt-2">
                      <i class="fas" :class="showMainItemDesc ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                      <span class="small text-white opacity-50 ms-1">{{ showMainItemDesc ? '접기' : '설명 보기' }}</span>
                    </div>
                  </div>
                </div>
                <div class="col-md-5 d-flex">
                  <div class="lucky-item-card text-center p-4 w-100 d-flex flex-column"
                       style="background: rgba(124, 58, 237, 0.15); border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 15px; cursor: pointer;"
                       @click="showZodiacItemDesc = !showZodiacItemDesc">
                    <div class="mb-2">
                      <span class="badge" style="background: #a78bfa; color: white;">{{ fortune.zodiac_sign }} 추천</span>
                    </div>
                    <span class="lucky-item-icon d-block mb-3">{{ fortune.lucky_item?.zodiac_emoji || '⭐' }}</span>
                    <h5 class="text-white fw-bold mb-2" style="word-break: keep-all;">{{ fortune.lucky_item?.zodiac || '별자리 아이템' }}</h5>
                    <div class="item-desc-toggle" :class="{ 'show': showZodiacItemDesc }">
                      <p class="text-white opacity-75 small mb-0" v-html="formatDescription(fortune.lucky_item?.zodiac_description || '', fortune.lucky_item?.zodiac)"></p>
                    </div>
                    <div class="toggle-hint mt-2">
                      <i class="fas" :class="showZodiacItemDesc ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                      <span class="small text-white opacity-50 ms-1">{{ showZodiacItemDesc ? '접기' : '설명 보기' }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center">
                <span class="lucky-item-icon">🎁</span>
                <h5 class="text-white mt-3">미니 키링</h5>
                <p class="text-white opacity-75">새로운 문을 여는 열쇠가 됩니다</p>
              </div>

              <div class="text-center mt-4">
                <router-link to="/fortune/item-check" class="btn btn-outline-light rounded-pill px-4">
                  <i class="fas fa-search me-2"></i> 내 아이템 행운도 측정하기
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Lucky Numbers Section (성인만 표시) -->
      <div v-if="fortune && !isMinor" class="row justify-content-center mb-4">
        <div class="col-lg-8">
          <div class="glass-card">
            <div class="card-body p-4 p-md-5">
              <h4 class="text-white text-center mb-4">
                <i class="fas fa-dice text-primary me-2" style="color: #a78bfa !important;"></i>
                재미로 보는 오늘의 추천 로또 번호
              </h4>
              <div v-if="fortune.lotto_numbers && fortune.lotto_numbers.length > 0" class="lotto-numbers">
                <div v-for="number in fortune.lotto_numbers" :key="number"
                     class="lotto-ball"
                     :style="getLottoBallStyle(number)">
                  {{ number }}
                </div>
              </div>
              <div v-else class="text-center">
                <p class="text-white opacity-75">로또 번호를 불러오는 중...</p>
              </div>
              <p class="text-white opacity-50 mt-4 text-center">
                <small>※ 오락용이며 실제 당첨과는 무관합니다</small>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div v-if="fortune" class="row justify-content-center mb-4">
        <div class="col-lg-8">
          <div class="row g-4">
            <div class="col-md-6">
              <div class="glass-card h-100 p-4 text-center hover-lift">
                <i class="fas fa-tshirt fa-3x mb-3" style="color: #a78bfa;"></i>
                <h5 class="text-white">OOTD 추천 받기</h5>
                <p class="text-white opacity-75 small mb-4">오늘의 날씨와 행운색 기반 코디</p>
                <router-link to="/recommendations/ootd" class="btn btn-outline-light rounded-pill px-4">
                  추천 받기 <i class="fas fa-arrow-right ms-2"></i>
                </router-link>
              </div>
            </div>
            <div class="col-md-6">
              <div class="glass-card h-100 p-4 text-center hover-lift">
                <i class="fas fa-utensils fa-3x mb-3" style="color: #a78bfa;"></i>
                <h5 class="text-white">메뉴 추천 받기</h5>
                <p class="text-white opacity-75 small mb-4">운세에 맞는 행운의 메뉴</p>
                <router-link to="/recommendations/menu" class="btn btn-outline-light rounded-pill px-4">
                  추천 받기 <i class="fas fa-arrow-right ms-2"></i>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Fortune Yet -->
      <div v-if="!fortune" class="glass-card p-5 text-center">
        <i class="fas fa-question-circle fa-5x text-white opacity-50 mb-4"></i>
        <h3 class="text-white mb-3">운세 정보가 없습니다</h3>
        <p class="text-white opacity-75 mb-4">먼저 운세를 계산해주세요</p>
        <router-link to="/fortune/calculate" class="btn btn-primary btn-lg rounded-pill px-5">
          <i class="fas fa-calculator me-2"></i> 운세 계산하기
        </router-link>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFortuneStore } from '@/stores/fortune'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import apiClient from '@/config/api'

const router = useRouter()
const authStore = useAuthStore()
const fortuneStore = useFortuneStore()
const fortune = ref(null)
const displayScore = ref(0)
const isMinor = ref(false)
const isLoading = ref(true)
const showMainItemDesc = ref(false)
const showZodiacItemDesc = ref(false)

// 문장 단위 줄바꿈 포맷팅 + 아이템명 굵게/밑줄 표시
const formatDescription = (text, itemName) => {
  if (!text) return ''
  let result = text
  // 아이템명을 굵게 + 밑줄 표시
  if (itemName) {
    const escapedName = itemName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    result = result.replace(new RegExp(escapedName, 'g'), `<strong style="text-decoration: underline;">${itemName}</strong>`)
  }
  // 문장 끝(.!?)을 찾아서 줄바꿈 추가
  return result.replace(/([.!?])(\s+)/g, '$1<br>')
}

// 운세 텍스트 문장 단위 줄바꿈
const formatFortuneText = (text) => {
  if (!text) return ''
  return text.replace(/([.!?])(\s+)/g, '$1<br>')
}

// Django today.html의 색상 매핑과 동일
const getColorHex = (colorName) => {
  const colorMap = {
    '빨간색': '#FF0000',
    '진한 빨간색': '#8B0000',
    '주황색': '#FFA500',
    '노란색': '#FFFF00',
    '초록색': '#00FF00',
    '연두색': '#90EE90',
    '하늘색': '#87CEEB',
    '파란색': '#0000FF',
    '남색': '#000080',
    '보라색': '#800080',
    '연보라색': '#DA70D6',
    '분홍색': '#FFC0CB',
    '갈색': '#8B4513',
    '베이지색': '#F5DEB3',
    '검은색': '#000000',
    '흰색': '#FFFFFF',
    '회색': '#808080',
    '은색': '#C0C0C0',
    '금색': '#FFD700'
  }
  return colorMap[colorName] || '#7c3aed'
}

// Django today.html의 로또볼 스타일과 동일
const getLottoBallStyle = (number) => {
  let background
  if (number <= 10) background = 'linear-gradient(135deg, #fbbf24, #d97706)'
  else if (number <= 20) background = 'linear-gradient(135deg, #60a5fa, #2563eb)'
  else if (number <= 30) background = 'linear-gradient(135deg, #f87171, #dc2626)'
  else if (number <= 40) background = 'linear-gradient(135deg, #34d399, #059669)'
  else background = 'linear-gradient(135deg, #c084fc, #7c3aed)'

  return `background: ${background};`
}

// Django today.html의 JavaScript와 동일한 애니메이션
const easeOutCubic = (x) => {
  return 1 - Math.pow(1 - x, 3)
}

const animateValue = (duration, onUpdate) => {
  const startTime = performance.now()

  const step = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easedProgress = easeOutCubic(progress)

    onUpdate(easedProgress)

    if (progress < 1) {
      requestAnimationFrame(step)
    }
  }

  requestAnimationFrame(step)
}

const animateScore = () => {
  const progressCircle = document.querySelector('.fortune-circle-progress')
  const scoreElement = document.querySelector('.fortune-score-text .score')

  if (progressCircle && scoreElement) {
    let targetScore = parseInt(progressCircle.getAttribute('data-score'))
    if (isNaN(targetScore)) targetScore = 0

    const circumference = 2 * Math.PI * 100

    progressCircle.style.transition = 'none'
    progressCircle.style.strokeDasharray = circumference
    progressCircle.style.strokeDashoffset = circumference
    displayScore.value = 0

    animateValue(1500, (progress) => {
      const currentScore = targetScore * progress
      const offset = circumference - (currentScore / 100 * circumference)

      displayScore.value = Math.round(currentScore)
      progressCircle.style.strokeDashoffset = offset
    })
  }
}

const animateBar = (container) => {
  const fill = container.querySelector('.sub-score-fill')
  const text = container.querySelector('.score-text')

  if (fill && text) {
    let targetScore = parseFloat(fill.getAttribute('data-target'))
    if (isNaN(targetScore)) {
      targetScore = parseFloat(fill.style.width) || 0
      fill.setAttribute('data-target', targetScore)
    }

    fill.style.transition = 'none'
    fill.style.width = '0%'
    text.textContent = '0%'

    animateValue(1000, (progress) => {
      const currentScore = targetScore * progress

      fill.style.width = `${currentScore}%`
      text.textContent = `${Math.round(currentScore)}%`
    })
  }
}

onMounted(async () => {
  // Django 세션과 동기화된 운세 데이터 가져오기
  try {
    isLoading.value = true
    const today = new Date().toISOString().split('T')[0]

    // 1. 비로그인 사용자: Fortune Store에 이미 데이터가 있으면 사용
    if (!authStore.isAuthenticated && fortuneStore.fortuneData && fortuneStore.fortuneDate === today) {
      console.log('[Today] Fortune Store에서 운세 로드 (비로그인)')
      fortune.value = fortuneStore.fortuneData
    } else {
      // 2. 로그인 사용자 또는 Store에 데이터 없음: API 호출
      console.log('[Today] API에서 운세 로드')
      const response = await apiClient.get('/api/fortune/today/')

      if (response.data.success && response.data.fortune) {
        fortune.value = response.data.fortune

        // Fortune Store에도 저장 (action 사용으로 반응성 유지)
        fortuneStore.setFortune(response.data.fortune, today)
      } else if (!authStore.isAuthenticated && fortuneStore.fortuneData) {
        // 비로그인 + API 실패 + Store에 데이터 있음 → Store 데이터 사용
        console.log('[Today] API 실패, Fortune Store 데이터 사용')
        fortune.value = fortuneStore.fortuneData
      }
    }

    if (fortune.value) {
      // 미성년자 체크
      if (authStore.user?.birth_date) {
        const birthDate = new Date(authStore.user.birth_date)
        const todayDate = new Date()
        const age = todayDate.getFullYear() - birthDate.getFullYear()
        isMinor.value = age < 19
      }

      // 애니메이션 시작
      setTimeout(() => {
        animateScore()

        // 활성 탭의 bar 애니메이션
        const activeTabPane = document.querySelector('.tab-pane.active')
        if (activeTabPane) {
          const bar = activeTabPane.querySelector('.sub-score-bar')
          if (bar) animateBar(bar)
        }

        // 탭 변경 이벤트 리스너
        const tabEls = document.querySelectorAll('a[data-bs-toggle="tab"]')
        tabEls.forEach(tabEl => {
          tabEl.addEventListener('shown.bs.tab', function (event) {
            const targetId = event.target.getAttribute('href')
            const targetPane = document.querySelector(targetId)
            if (targetPane) {
              const bar = targetPane.querySelector('.sub-score-bar')
              if (bar) animateBar(bar)
            }
          })
        })
      }, 100)
    }
  } catch (error) {
    console.error('Failed to fetch fortune:', error)
    // 비로그인 + Store에 데이터 있으면 사용
    if (!authStore.isAuthenticated && fortuneStore.fortuneData) {
      console.log('[Today] API 에러, Fortune Store 데이터 사용')
      fortune.value = fortuneStore.fortuneData
    }
  } finally {
    isLoading.value = false
  }
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
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(167, 139, 250, 0.5);
}

.fortune-score-text .label {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 300;
}

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

.lotto-numbers {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin: 30px 0;
  flex-wrap: wrap;
}

.lotto-ball {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: white;
  font-size: 1.4rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3), inset 0 -5px 10px rgba(0,0,0,0.2), inset 0 5px 10px rgba(255,255,255,0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.hover-lift {
  transition: transform 0.3s;
}

.hover-lift:hover {
  transform: translateY(-5px);
}

.lucky-item-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
}

.lucky-item-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.lucky-item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
}

.item-desc-toggle {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out, opacity 0.3s ease-out, margin 0.3s ease-out;
  opacity: 0;
  margin-top: 0;
}

.item-desc-toggle.show {
  max-height: 200px;
  opacity: 1;
  margin-top: 15px;
}

.item-desc-toggle p {
  padding: 15px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  line-height: 1.6;
}

.toggle-hint {
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.2s;
}

.lucky-item-card:hover .toggle-hint {
  color: rgba(255, 255, 255, 0.8);
}

.nav-pills .nav-link {
  color: rgba(255,255,255,0.5);
  transition: all 0.3s;
  border-right: 1px solid rgba(255,255,255,0.1);
  border-radius: 0;
}
.nav-pills .nav-item:last-child .nav-link {
  border-right: none;
}
.nav-pills .nav-link.active {
  color: white;
  background-color: transparent;
  font-weight: bold;
}

@media (max-width: 768px) {
  .glass-card {
    padding: 1.5rem !important;
  }
}
</style>
