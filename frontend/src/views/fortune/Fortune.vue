<template>
  <DefaultLayout>
    <div class="page-container">
      <div class="content-wrapper">
        <!-- 페이지 헤더 -->
        <div class="page-header">
          <h1 class="page-title">
            <img src="@/assets/images/logo.png" alt="" class="page-title-icon" />
            {{ periodTitle }}
          </h1>
          <p class="page-subtitle">{{ periodSubtitle }}</p>
        </div>

        <!-- 기간 선택 버튼 (한 줄) -->
        <div class="period-selector mb-3">
          <div class="btn-group-period">
            <button
              class="btn-period"
              :class="{ active: selectedPeriod === 'daily' }"
              @click="changePeriod('daily')"
            >오늘</button>
            <button
              class="btn-period"
              :class="{ active: selectedPeriod === 'weekly' }"
              @click="changePeriod('weekly')"
            >이번 주</button>
            <button
              class="btn-period"
              :class="{ active: selectedPeriod === 'monthly' }"
              @click="changePeriod('monthly')"
            >이번 달</button>
          </div>
        </div>

      <div v-if="fortune" class="card-base card-lg section-spacing">
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
                <span class="score-wrapper"><span class="score">{{ displayScore }}</span><span class="label">점</span></span>
              </div>
            </div>

            <div class="badge-row mt-5">
              <div class="text-center">
                <h6 class="text-primary-light mb-2">별자리</h6>
                <span class="badge zodiac-badge rounded-pill bg-primary bg-opacity-25 border border-primary text-white fs-5 px-4 py-2 d-inline-flex align-items-center justify-content-center gap-2" style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(167, 139, 250, 0.2)); border-color: rgba(167, 139, 250, 0.5) !important;">
                  <img v-if="getZodiacIcon(fortune.zodiac_sign)" :src="getZodiacIcon(fortune.zodiac_sign)" alt="" class="zodiac-icon">
                  {{ fortune.zodiac_sign || '-' }}
                </span>
              </div>
              <div class="text-center">
                <h6 class="text-primary-light mb-2">띠</h6>
                <span class="badge zodiac-badge rounded-pill bg-primary bg-opacity-25 border border-primary text-white fs-5 px-4 py-2 d-inline-flex align-items-center justify-content-center gap-2" style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(167, 139, 250, 0.2)); border-color: rgba(167, 139, 250, 0.5) !important;">
                  {{ getChineseZodiacEmoji(fortune.chinese_zodiac) }} {{ fortune.chinese_zodiac || '-' }}
                </span>
              </div>
            </div>
      </div>

      <!-- Fortune Details Tabs -->
      <div v-if="fortune" class="card-base card-lg section-spacing overflow-hidden">
            <div class="card-header border-0 responsive-padding-header">
              <div class="fortune-tabs-wrapper">
                <a class="fortune-tab-pill" :class="{ active: activeTab === 'total' }" @click.prevent="changeTab('total')">
                  <span class="tab-icon">⭐️</span>
                  <span class="tab-label">종합운</span>
                </a>
                <a class="fortune-tab-pill" :class="{ active: activeTab === 'love' }" @click.prevent="changeTab('love')">
                  <span class="tab-icon">❤️</span>
                  <span class="tab-label">애정운</span>
                </a>
                <a class="fortune-tab-pill" :class="{ active: activeTab === 'money' }" @click.prevent="changeTab('money')">
                  <span class="tab-icon">💰</span>
                  <span class="tab-label">금전운</span>
                </a>
                <a class="fortune-tab-pill" :class="{ active: activeTab === 'work' }" @click.prevent="changeTab('work')">
                  <span class="tab-icon">💼</span>
                  <span class="tab-label">직장운</span>
                </a>
                <a class="fortune-tab-pill" :class="{ active: activeTab === 'health' }" @click.prevent="changeTab('health')">
                  <span class="tab-icon">💪</span>
                  <span class="tab-label">건강운</span>
                </a>
                <a class="fortune-tab-pill" :class="{ active: activeTab === 'study' }" @click.prevent="changeTab('study')">
                  <span class="tab-icon">📚</span>
                  <span class="tab-label">학업운</span>
                </a>
              </div>
            </div>
            <div class="card-body responsive-padding">
              <div class="tab-content">
                <!-- 종합운 -->
                <div v-show="activeTab === 'total'" id="total">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-star text-primary me-2" style="color: #a78bfa !important;"></i> 종합운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_score || 0 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_score || 0 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_score || 0}%; background: linear-gradient(90deg, #7c3aed, #a78bfa);`" :data-target="fortune.fortune_score || 0"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.total || '오늘의 운세 내용', 'color-purple')"></p>
                </div>

                <!-- 재물운 -->
                <div v-show="activeTab === 'money'" id="money">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-coins text-warning me-2" style=" -webkit-text-stroke: 1px rgba(255,255,255,0.1);"></i> 재물운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_scores?.money || 70 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_scores?.money || 70 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_scores?.money || 70}%; background: linear-gradient(90deg, #f59e0b, #fbbf24);`" :data-target="fortune.fortune_scores?.money || 70"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.money || '재물운 내용', 'color-yellow')"></p>
                </div>

                <!-- 애정운 -->
                <div v-show="activeTab === 'love'" id="love">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-heart text-danger me-2"></i> 애정운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_scores?.love || 65 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_scores?.love || 65 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_scores?.love || 65}%; background: linear-gradient(90deg, #ef4444, #f87171);`" :data-target="fortune.fortune_scores?.love || 65"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.love || '애정운 내용', 'color-red')"></p>
                </div>

                <!-- 학업운 -->
                <div v-show="activeTab === 'study'" id="study">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-graduation-cap text-info me-2"></i> 학업운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_scores?.study || 75 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_scores?.study || 75 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_scores?.study || 75}%; background: linear-gradient(90deg, #3b82f6, #60a5fa);`" :data-target="fortune.fortune_scores?.study || 75"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.study || '학업운 내용', 'color-blue')"></p>
                </div>

                <!-- 직장운 -->
                <div v-show="activeTab === 'work'" id="work">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-briefcase text-success me-2"></i> 직장운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_scores?.work || 80 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_scores?.work || 80 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_scores?.work || 80}%; background: linear-gradient(90deg, #10b981, #34d399);`" :data-target="fortune.fortune_scores?.work || 80"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.work || '직장운 내용', 'color-green')"></p>
                </div>

                <!-- 건강운 -->
                <div v-show="activeTab === 'health'" id="health">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="text-white"><i class="fas fa-heartbeat me-2" style="color: #2dd4bf;"></i> 건강운</h4>
                    <span class="text-white opacity-50 small">{{ fortune.fortune_scores?.health || 70 }} / 100</span>
                  </div>
                  <div class="sub-score-bar">
                    <span class="score-text">{{ fortune.fortune_scores?.health || 70 }}%</span>
                    <div class="sub-score-fill" :style="`width: ${fortune.fortune_scores?.health || 70}%; background: linear-gradient(90deg, #2dd4bf, #99f6e4);`" :data-target="fortune.fortune_scores?.health || 70"></div>
                  </div>
                  <p class="fortune-text" v-html="formatFortuneText(fortune.fortune_texts?.health || '건강운 내용', 'color-teal')"></p>
                </div>
              </div>
            </div>
      </div>

      <!-- Lucky Colors Section (일간 운세에서만 표시) -->
      <div v-if="fortune && selectedPeriod === 'daily'" class="card-base card-lg section-spacing">
              <h4 class="text-white text-center mb-2 d-flex align-items-center justify-content-center gap-2">
                <img src="@/assets/images/pallete.png" alt="" class="section-icon" />
                오늘의 행운색
              </h4>
              <p class="text-center text-white opacity-75 lucky-color-subtitle">오늘 당신에게 행운을 가져다 줄 색상</p>

              <div v-if="fortune.lucky_colors && fortune.lucky_colors.length > 0" class="d-flex justify-content-center align-items-center gap-3 gap-md-5">
                <div v-for="color in fortune.lucky_colors" :key="color" class="text-center">
                  <div class="lucky-color-circle" :style="`background: ${getColorBackground(color)};`"></div>
                  <p class="mt-3 mb-0 fw-bold text-white responsive-text-shadow">{{ color }}</p>
                </div>
              </div>
              <div v-else class="d-flex justify-content-center align-items-center gap-3 gap-md-5">
                <div class="text-center">
                  <div class="lucky-color-circle" style="background: #87CEEB;"></div>
                  <p class="mt-3 mb-0 fw-bold text-white responsive-text-shadow">하늘색</p>
                </div>
                <div class="text-center">
                  <div class="lucky-color-circle" style="background: #90EE90;"></div>
                  <p class="mt-3 mb-0 fw-bold text-white responsive-text-shadow">연두색</p>
                </div>
                <div class="text-center">
                  <div class="lucky-color-circle" style="background: #800080;"></div>
                  <p class="mt-3 mb-0 fw-bold text-white responsive-text-shadow">보라색</p>
                </div>
              </div>

              <p class="text-center text-white opacity-75 mt-4 mb-0">
                이 색상들은 오늘 하루 당신을 지켜주고 자신감을 불어넣어 줄 것입니다!
              </p>
      </div>

      <!-- Lucky Item Section (일간 운세에서만 표시) -->
      <div v-if="fortune && selectedPeriod === 'daily'" class="card-base card-lg section-spacing">
              <h4 class="text-white text-center mb-2">
                <span class="section-emoji">💎</span>
                오늘의 행운 아이템
              </h4>
              <p class="text-center text-white opacity-75 mb-5">오늘 당신에게 행운을 가져다 줄 아이템들</p>

              <div v-if="fortune.lucky_item" class="row g-4">
                <div class="col-6">
                  <div class="lucky-item-card text-center p-4 h-100"
                       style="background: rgba(124, 58, 237, 0.15); border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 15px; cursor: pointer;"
                       @click.stop.prevent="showMainItemDesc = !showMainItemDesc">
                    <div class="mb-2">
                      <span class="badge" style="background: #a78bfa; color: white;">운세 기반</span>
                    </div>
                    <img v-if="getLuckyItemImage(fortune.lucky_item?.main)"
                         :src="getLuckyItemImage(fortune.lucky_item?.main)"
                         :alt="fortune.lucky_item?.main"
                         class="lucky-item-img d-block mb-3 mx-auto">
                    <span v-else class="lucky-item-icon d-block mb-3">{{ fortune.lucky_item?.emoji || '🎁' }}</span>
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
                <div class="col-6">
                  <div class="lucky-item-card text-center p-4 h-100"
                       style="background: rgba(124, 58, 237, 0.15); border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 15px; cursor: pointer;"
                       @click.stop.prevent="showZodiacItemDesc = !showZodiacItemDesc">
                    <div class="mb-2">
                      <span class="badge" style="background: #a78bfa; color: white;">{{ fortune.zodiac_sign }} 추천</span>
                    </div>
                    <img v-if="getLuckyItemImage(fortune.lucky_item?.zodiac)"
                         :src="getLuckyItemImage(fortune.lucky_item?.zodiac)"
                         :alt="fortune.lucky_item?.zodiac"
                         class="lucky-item-img d-block mb-3 mx-auto">
                    <span v-else class="lucky-item-icon d-block mb-3">{{ fortune.lucky_item?.zodiac_emoji || '⭐' }}</span>
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
                <h5 class="text-white mt-3">열쇠고리</h5>
                <p class="text-white opacity-75">새로운 문을 여는 열쇠가 됩니다</p>
              </div>

              <div class="text-center mt-4">
                <router-link to="/fortune/item-check" class="btn btn-outline-light rounded-pill px-4">
                  <i class="fas fa-search me-2"></i> 내 아이템 행운도 측정하기
                </router-link>
              </div>
      </div>

      <!-- Lucky Numbers Section (일간 운세 + 성인만 표시) -->
      <div v-if="fortune && selectedPeriod === 'daily' && !isMinor" class="card-base card-lg section-spacing">
              <h4 class="text-white text-center mb-4 lotto-title">
                <span class="section-emoji">🎲</span>
                재미로 보는 오늘의 추천 로또 번호
              </h4>
              <div v-if="fortune.lotto_numbers && fortune.lotto_numbers.length > 0" class="lotto-numbers d-flex justify-content-center flex-nowrap gap-2 gap-md-3">
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

      <!-- Recommendations -->
      <div v-if="fortune" class="card-grid cols-2 section-spacing">
            <router-link to="/recommendations/ootd" class="card-base card-md card-interactive text-center recommend-card recommend-card-link">
                <div class="recommend-icon-wrapper">
                  <img src="@/assets/images/ootd-icon2.png" alt="" class="recommend-icon" />
                </div>
                <h5 class="text-white recommend-title">OOTD 추천 받기</h5>
                <p class="text-white opacity-75 small recommend-desc">오늘의 날씨와 행운색 기반 코디</p>
                <span class="btn btn-outline-light rounded-pill px-4 recommend-btn">
                  추천 받기 →
                </span>
            </router-link>
            <router-link to="/recommendations/menu" class="card-base card-md card-interactive text-center recommend-card recommend-card-link">
                <div class="recommend-icon-wrapper">
                  <img src="@/assets/images/recommendations_menu_icon.png" alt="" class="recommend-icon" />
                </div>
                <h5 class="text-white recommend-title">오늘의 메뉴 추천 받기</h5>
                <p class="text-white opacity-75 small recommend-desc">운세에 맞는 행운의 메뉴</p>
                <span class="btn btn-outline-light rounded-pill px-4 recommend-btn">
                  추천 받기 →
                </span>
            </router-link>
      </div>

      <!-- No Fortune Yet (로딩 중이 아닐 때만 표시) -->
      <div v-if="!fortune && !isLoading" class="card-base card-lg">
        <div class="empty-state">
          <i class="fas fa-question-circle empty-icon"></i>
          <h3 class="empty-title">운세 정보가 없습니다</h3>
          <p class="empty-text">먼저 운세를 계산해주세요</p>
          <router-link to="/fortune/calculate" class="btn btn-primary btn-lg rounded-pill px-5">
            <i class="fas fa-calculator me-2"></i> 운세 계산하기
          </router-link>
        </div>
      </div>

      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFortuneStore } from '@/stores/fortune'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { getColorBackground } from '@/utils/colors'
import { getLuckyItemImage } from '@/utils/luckyItems'
import { getZodiacIcon, getChineseZodiacEmoji } from '@/utils/zodiac'
import {
  getCachedFortune,
  cacheFortune,
  fetchFortune,
  generateFortune,
  generateFortuneWithForm,
  formatFortuneText as baseFormatFortuneText,
  formatDescription
} from '@/utils/fortuneLoader'
import {
  animateScore as baseAnimateScore,
  animateActiveTabBar,
  setupTabAnimations,
  getLottoBallStyle
} from '@/utils/fortuneAnimations'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const fortuneStore = useFortuneStore()
const fortune = ref(null)
const displayScore = ref(0)
const isMinor = ref(false)
const isLoading = ref(true)
const showMainItemDesc = ref(false)
const showZodiacItemDesc = ref(false)
const activeTab = ref('total')

// URL 경로에서 기간 결정
const getPeriodFromRoute = () => {
  const path = route.path
  if (path.includes('/weekly')) return 'weekly'
  if (path.includes('/monthly')) return 'monthly'
  return 'daily'
}

const selectedPeriod = ref(getPeriodFromRoute())

// 기간별 제목
const periodTitle = computed(() => {
  switch (selectedPeriod.value) {
    case 'weekly': return '이 주의 운세'
    case 'monthly': return '이 달의 운세'
    default: return '오늘의 운세'
  }
})

// 기간별 부제목
const periodSubtitle = computed(() => {
  switch (selectedPeriod.value) {
    case 'weekly': return '당신의 한 주를 빛낼 운세를 확인해보세요'
    case 'monthly': return '당신의 한 달을 빛낼 운세를 확인해보세요'
    default: return '당신의 오늘을 빛낼 운세를 확인해보세요'
  }
})

// 운세 텍스트 포맷팅 (현재 선택된 기간 전달)
const formatFortuneText = (text, colorClass = '') => {
  return baseFormatFortuneText(text, colorClass, selectedPeriod.value)
}

// 애니메이션 래퍼 (displayScore ref 전달)
const animateScore = () => {
  baseAnimateScore({ setDisplayScore: (val) => { displayScore.value = val } })
}

// 탭 변경 함수
const changeTab = async (tab) => {
  activeTab.value = tab
  await nextTick()

  // 활성 탭의 점수 바 애니메이션
  const activePane = document.getElementById(tab)
  if (activePane) {
    const bar = activePane.querySelector('.sub-score-bar')
    if (bar) {
      const { animateBar } = await import('@/utils/fortuneAnimations')
      animateBar(bar)
    }
  }
}

// 기간 변경 함수
const changePeriod = async (period) => {
  if (selectedPeriod.value === period) return

  const routePaths = { daily: '/fortune/today', weekly: '/fortune/weekly', monthly: '/fortune/monthly' }
  router.push(routePaths[period])
}

// 실제 운세 데이터 로드 함수 (유틸리티 사용)
const loadFortuneData = async (period) => {
  fortune.value = null

  // Store 캐시 먼저 확인
  const cached = getCachedFortune(period, fortuneStore)
  if (cached) {
    fortune.value = cached
    setupFortuneUI()
    return
  }

  try {
    // GET으로 캐시 확인
    const response = await fetchFortune(period)

    if (response.success && response.fortune) {
      fortune.value = response.fortune
      cacheFortune(period, fortuneStore, response.fortune, response)
    } else if (response.need_calculate) {
      // 운세 생성 필요
      await generateAndCacheFortune(period)
      return
    }
  } catch (error) {
    console.error(`[Fortune] ${period} 운세 로드 실패:`, error)
    handleFortuneError()
    return
  } finally {
    if (fortune.value) {
      await nextTick()
      setTimeout(() => {
        animateScore()
        animateActiveTabBar()
      }, 200)
    }
  }
}

// 운세 생성 및 캐시 저장
const generateAndCacheFortune = async (period) => {
  const redirectPaths = { daily: '/fortune/today', weekly: '/fortune/weekly', monthly: '/fortune/monthly' }

  if (authStore.isAuthenticated) {
    // 로그인 사용자
    try {
      const response = await generateFortune(period)
      if (response.success && response.fortune) {
        fortune.value = response.fortune
        cacheFortune(period, fortuneStore, response.fortune, response)
        await nextTick()
        setTimeout(() => { animateScore(); animateActiveTabBar() }, 200)
      } else {
        router.replace({ name: 'fortune-loading', query: { redirect: '/fortune/today' } })
      }
    } catch {
      router.replace({ name: 'fortune-loading', query: { redirect: '/fortune/today' } })
    }
  } else {
    // 비로그인 사용자
    const formInfo = fortuneStore.formData || {}
    const fortuneInfo = fortuneStore.fortuneData || {}
    const birthDate = formInfo.birth_date || fortuneInfo.birth_date
    const gender = formInfo.gender || fortuneInfo.gender

    if (birthDate && gender) {
      try {
        const response = await generateFortuneWithForm(period, {
          birth_date: birthDate,
          gender: gender,
          birth_time: formInfo.birth_time || fortuneInfo.birth_time || '',
          chinese_name: formInfo.chinese_name || fortuneInfo.chinese_name || '',
          mbti: formInfo.mbti || fortuneInfo.mbti || ''
        })
        if (response.success && response.fortune) {
          fortune.value = response.fortune
          cacheFortune(period, fortuneStore, response.fortune, response)
          await nextTick()
          setTimeout(() => { animateScore(); animateActiveTabBar() }, 200)
        }
      } catch (error) {
        console.error(`[Fortune] ${period} 운세 생성 실패 (비로그인):`, error)
      }
    } else {
      router.replace({ name: 'fortune-calculate', query: { redirect: redirectPaths[period] } })
    }
  }
}

// 에러 처리
const handleFortuneError = () => {
  if (!fortune.value) {
    const redirectName = authStore.isAuthenticated ? 'fortune-loading' : 'fortune-calculate'
    router.replace({ name: redirectName, query: { redirect: route.fullPath } })
  }
}

// 라우트 변경 감지
watch(() => route.path, () => {
  const newPeriod = getPeriodFromRoute()
  if (selectedPeriod.value !== newPeriod) {
    selectedPeriod.value = newPeriod
    loadFortuneData(newPeriod)
  }
})

// 미성년자 체크
const checkMinorStatus = () => {
  const birthDateStr = authStore.user?.birth_date || fortune.value?.birth_date
  if (birthDateStr) {
    const birthDate = new Date(birthDateStr)
    const age = new Date().getFullYear() - birthDate.getFullYear()
    isMinor.value = age < 19
  }
}

// UI 설정 및 애니메이션 시작
const setupFortuneUI = () => {
  if (!fortune.value) return

  checkMinorStatus()

  setTimeout(() => {
    animateScore()
    animateActiveTabBar()
    setupTabAnimations()
  }, 100)
}

onMounted(async () => {
  const currentPeriod = getPeriodFromRoute()
  selectedPeriod.value = currentPeriod
  isLoading.value = true

  try {
    // 모든 기간에 대해 통합 로직 사용
    const cached = getCachedFortune(currentPeriod, fortuneStore)
    if (cached) {
      fortune.value = cached
      setupFortuneUI()
      return
    }

    // API 호출
    const response = await fetchFortune(currentPeriod)

    if (response.success && response.fortune) {
      fortune.value = response.fortune
      cacheFortune(currentPeriod, fortuneStore, response.fortune, response)
      setupFortuneUI()
    } else if (response.need_calculate) {
      await generateAndCacheFortune(currentPeriod)
    } else if (!authStore.isAuthenticated && fortuneStore.fortuneData) {
      // 비로그인 + API 실패 + Store에 데이터 있음
      fortune.value = fortuneStore.fortuneData
      setupFortuneUI()
    }
  } catch (error) {
    console.error('Failed to fetch fortune:', error)
    if (!authStore.isAuthenticated && fortuneStore.fortuneData) {
      fortune.value = fortuneStore.fortuneData
      setupFortuneUI()
    }
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
/* 기간 선택 버튼 스타일 */
.period-selector {
  margin-bottom: 1.5rem;
}

.btn-group-period {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-period {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.3);
  color: rgba(255, 255, 255, 0.7);
  padding: 0.6rem 1.2rem;
  border-radius: 25px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.btn-period:hover:not(:disabled) {
  background: rgba(167, 139, 250, 0.2);
  border-color: rgba(167, 139, 250, 0.5);
  color: white;
}

.btn-period.active {
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  border-color: #a78bfa;
  color: white;
  font-weight: 600;
  box-shadow: 0 0 15px rgba(167, 139, 250, 0.4);
}

.btn-period:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 별자리/띠 배지 동일 높이 */
.zodiac-badge {
  min-height: 48px;
  min-width: 140px;
}

.zodiac-icon {
  width: 28px;
  height: 28px;
  object-fit: contain;
  filter: brightness(1.2);
}

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

.fortune-score-text .score-wrapper {
  display: inline-flex;
  align-items: baseline;
  gap: 0.1rem;
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
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 400;
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
  content: '•';
  position: absolute;
  left: 0;
  color: #a78bfa;
  font-size: 1.2rem;
  line-height: 1.6;
}

/* 운세별 점 색상 */
.fortune-text :deep(.fortune-list.color-purple li)::before {
  color: #a78bfa;
}
.fortune-text :deep(.fortune-list.color-yellow li)::before {
  color: #fbbf24;
}
.fortune-text :deep(.fortune-list.color-red li)::before {
  color: #f87171;
}
.fortune-text :deep(.fortune-list.color-blue li)::before {
  color: #60a5fa;
}
.fortune-text :deep(.fortune-list.color-green li)::before {
  color: #34d399;
}
.fortune-text :deep(.fortune-list.color-teal li)::before {
  color: #2dd4bf;
}

/* 오늘 해당하는 구간 (주간/월간 운세용) - 볼드만 적용 */
.fortune-text :deep(.fortune-list li.today-highlight strong) {
  color: #fff;
  font-weight: 700;
}

.lotto-numbers {
  display: flex;
  justify-content: center;
  gap: 15px;
}

/* 섹션 아이콘 스타일 */
.section-icon {
  width: 28px;
  height: 28px;
  object-fit: contain;
}

/* 페이지 타이틀 아이콘 */
.page-title-icon {
  width: 42px;
  height: 42px;
  margin-right: -8px;
  vertical-align: middle;
  object-fit: contain;
}

/* 추천 카드 레이아웃 */
.recommend-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100%;
}

.recommend-icon-wrapper {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

/* 추천 아이콘 스타일 */
.recommend-icon {
  width: 64px;
  height: 64px;
  object-fit: contain;
}

.recommend-title {
  margin-bottom: 0.5rem;
}

.recommend-desc {
  flex-grow: 1;
  margin-bottom: 0.5rem;
}

.recommend-btn {
  margin-top: auto;
}

/* 전체 클릭 가능한 추천 카드 링크 */
.recommend-card-link {
  text-decoration: none;
  cursor: pointer;
}

/* 추천 이모지 스타일 */
.recommend-emoji {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.75rem;
}

/* .hover-lift는 전역 CSS에서 관리 */

.lucky-item-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
}

.lucky-item-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
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

/* 운세 탭 래퍼 - 6개 탭 가로 배치 */
.fortune-tabs-wrapper {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

/* 운세 탭 Pill 버튼 스타일 (첨부 이미지 참고) */
.fortune-tab-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  background: rgba(40, 40, 50, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 30px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  font-size: 0.9rem;
}

.fortune-tab-pill:hover {
  background: rgba(60, 60, 70, 0.9);
  color: white;
  border-color: rgba(167, 139, 250, 0.5);
}

.fortune-tab-pill .tab-icon {
  font-size: 1rem;
}

.fortune-tab-pill .tab-label {
  font-weight: 500;
  white-space: nowrap;
}

/* Pill 버튼 활성 상태 - 보라색 배경 */
.fortune-tab-pill.active {
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  border-color: #a78bfa;
  color: white;
  font-weight: 600;
  box-shadow: 0 0 15px rgba(167, 139, 250, 0.4);
}

/* Responsive Padding Utilities */
.responsive-padding {
  padding: 3rem !important; /* Desktop Default */
}
.responsive-padding-header {
  padding: 2rem !important;
}

/* Lucky Color Circle Responsive */
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

.lucky-color-subtitle {
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  /* 모바일 기간 선택 버튼 - 한 줄 유지 */
  .btn-group-period {
    flex-direction: row;
    gap: 0.5rem !important;
    justify-content: center;
  }

  .btn-period {
    flex: 1;
    max-width: 100px;
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }

  /* Percentage based padding for mobile */
  .responsive-padding {
    padding: 3% !important;
  }
  .responsive-padding-header {
    padding: 3% !important;
  }

  .glass-card {
    border-radius: 12px;
  }

  /* 모바일 별자리/띠 글자 크기 줄이기 */
  .zodiac-badge {
    font-size: 0.85rem !important;
    padding: 0.35rem 0.7rem !important;
    min-width: 90px;
    min-height: 36px;
  }

  .zodiac-icon {
    width: 20px;
    height: 20px;
  }

  /* 모바일 별자리/띠 라벨 */
  .badge-row h6 {
    font-size: 0.75rem !important;
    margin-bottom: 0.3rem !important;
  }

  /* 모바일 운세 탭 - 3x2 그리드 */
  .fortune-tabs-wrapper {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.4rem;
    margin-bottom: 1.5rem;
  }

  .fortune-tab-pill {
    padding: 0.5rem 0.6rem;
    font-size: 0.75rem;
    gap: 0.25rem;
  }

  .fortune-tab-pill .tab-icon {
    font-size: 0.85rem;
  }

  .fortune-tab-pill .tab-label {
    font-size: 0.7rem;
  }

  /* Responsive Lucky Color Circle */
  .lucky-color-circle {
    width: 60px;
    height: 60px;
    border-width: 2px;
  }

  .responsive-text-shadow {
    font-size: 0.9rem;
  }

  /* Responsive Lotto Ball */
  .lotto-ball {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
    border-width: 1px;
  }

  /* 모바일 행운 아이템 카드 */
  .lucky-item-card {
    padding: 0.75rem !important;
  }

  .lucky-item-card .lucky-item-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem !important;
  }

  .lucky-item-card .lucky-item-img {
    width: 50px;
    height: 50px;
    margin-bottom: 0.5rem !important;
  }

  .lucky-item-card h5 {
    font-size: 0.9rem;
  }

  .lucky-item-card .badge {
    font-size: 0.65rem;
    padding: 0.25rem 0.5rem;
  }

  .lucky-item-card .toggle-hint {
    font-size: 0.7rem;
  }

  .lucky-item-card .item-desc-toggle p {
    font-size: 0.75rem;
    padding: 10px;
  }

  /* 모바일 로또 타이틀 */
  .lotto-title {
    font-size: 0.9rem;
    white-space: nowrap;
  }

  /* 모바일 추천 타이틀 */
  .recommend-title {
    font-size: 0.9rem !important;
    white-space: nowrap;
  }

  /* 모바일 별자리/띠 배열 */
  .badge-row {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: center;
    gap: 1rem;
  }
}
</style>
