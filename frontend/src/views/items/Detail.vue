<template>
  <DefaultLayout>
    <div class="page-container">
      <div class="content-wrapper">
        <!-- 페이지 헤더 -->
        <div class="page-header">
          <h1 class="page-title">
            <i class="fas fa-search text-primary"></i>
            아이템 상세 분석
            <span v-if="item && item.user_order" class="item-number"></span>
          </h1>
          <p class="page-subtitle">AI가 분석한 아이템의 상세 정보입니다</p>
        </div>

        <div v-if="item" class="card-base card-lg">
          <!-- 이미지 섹션 (상단) -->
          <div class="item-image-container">
            <img
              v-if="item.image"
              :src="item.image"
              class="item-image"
              :alt="item.item_name"
            >
            <div
              v-else
              class="item-image-placeholder"
            >
              <span class="text-muted">이미지 없음</span>
            </div>
          </div>

          <!-- 콘텐츠 섹션 (하단) -->
          <div class="card-body p-4">
                <!-- 아이템 이름 (수정 모드) -->
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div v-if="isEditing" class="flex-grow-1 me-2">
                    <input
                      v-model="editForm.item_name"
                      type="text"
                      class="form-control form-control-lg fw-bold"
                      placeholder="아이템 이름"
                    >
                  </div>
                  <h2 v-else class="card-title fw-bold mb-0">{{ item.item_name }}</h2>
                  <div class="d-flex align-items-center gap-2">
                    <button
                      v-if="!isEditing"
                      class="btn btn-sm btn-outline-secondary"
                      @click="startEditing"
                      title="수정"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <span v-if="item.is_favorite" class="text-warning">
                      <i class="fas fa-star fa-lg"></i>
                    </span>
                  </div>
                </div>

                <!-- 카테고리 (수정 모드) -->
                <div v-if="isEditing" class="mb-4">
                  <label class="form-label text-muted small">카테고리</label>
                  <select v-model="editForm.main_category" class="form-select">
                    <option value="clothing">의류</option>
                    <option value="cosmetics">화장품</option>
                    <option value="electronics">전자제품</option>
                    <option value="accessories">악세서리</option>
                    <option value="etc">기타</option>
                  </select>
                </div>
                <p v-else class="text-muted mb-4">
                  <span class="badge bg-secondary me-2">{{ item.category_display }}</span>
                  <small>{{ formatDate(item.created_at) }} 등록</small>
                </p>

                <!-- 수정 버튼들 -->
                <div v-if="isEditing" class="d-flex gap-2 mb-4">
                  <button class="btn btn-primary" @click="saveEdit" :disabled="isSaving">
                    <i class="fas fa-check me-1"></i> 저장
                  </button>
                  <button class="btn btn-outline-secondary" @click="cancelEdit">
                    <i class="fas fa-times me-1"></i> 취소
                  </button>
                </div>

                <hr class="my-4">

                <!-- 운세 미생성 시 유도 배너 -->
                <div v-if="!fortuneStore.hasTodayFortune" class="fortune-prompt-banner mb-4">
                  <div class="fortune-prompt-content">
                    <i class="fas fa-magic fortune-prompt-icon"></i>
                    <div class="fortune-prompt-text">
                      <p class="fortune-prompt-title">오늘의 운세를 아직 확인하지 않으셨네요!</p>
                      <p class="fortune-prompt-desc">이 아이템이 오늘 어떤 행운을 불러올지 궁금하다면, 지금 운세를 확인해보세요!</p>
                    </div>
                    <router-link to="/fortune/today" class="btn btn-primary rounded-pill px-4">
                      <i class="fas fa-crystal-ball me-1"></i> 운세 확인하기
                    </router-link>
                  </div>
                </div>

                <!-- 행운 지수 표시 (운세 있을 때만) -->
                <div v-else class="luck-score-section mb-4">
                  <h6 class="text-center mb-3"><i class="fas fa-magic text-primary me-2"></i>오늘의 행운 지수</h6>

                  <!-- 행운 지수 원형 -->
                  <div class="text-center mb-3">
                    <div class="luck-score-circle mx-auto">
                      <svg width="120" height="120">
                        <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="12"></circle>
                        <circle cx="60" cy="60" r="50" fill="none" :stroke="luckScoreColor"
                                stroke-width="12" stroke-dasharray="314" :stroke-dashoffset="luckProgressOffset"
                                style="transition: stroke-dashoffset 1s ease-out; transform: rotate(-90deg); transform-origin: center;"></circle>
                      </svg>
                      <div class="luck-score-text">
                        <span class="luck-score-number">{{ luckScore }}</span>
                        <span class="luck-score-label">점</span>
                      </div>
                    </div>
                  </div>

                  <!-- 색상 비교 -->
                  <div class="color-compare-section">
                    <div class="color-compare-item">
                      <span class="color-label">아이템 색상</span>
                      <div class="color-circle" :style="`background: ${bestItemColor};`"></div>
                    </div>
                    <div class="color-compare-arrow">
                      <i class="fas fa-arrows-alt-h"></i>
                    </div>
                    <div class="color-compare-item">
                      <span class="color-label">오늘의 행운색</span>
                      <div class="color-circle" :style="`background: ${matchedLuckyColor};`"></div>
                    </div>
                  </div>

                  <!-- 매치 메시지 -->
                  <div class="match-message mt-3" :class="matchMessageClass">
                    <span class="match-icon">{{ matchIcon }}</span>
                    <span class="match-text">{{ matchMessage }}</span>
                  </div>

                  <!-- 색상 안 맞을 때 다른 아이템 추천 -->
                  <div v-if="luckScore < 70 && recommendedItem" class="recommend-section mt-3">
                    <p class="recommend-text">
                      <i class="fas fa-lightbulb text-warning me-1"></i>
                      오늘은 <router-link :to="`/items/${recommendedItem.id}`" class="recommend-link">{{ recommendedItem.item_name }}</router-link>을(를) 사용해보는 건 어떨까요?
                    </p>
                  </div>

                  <!-- 추천할 좋은 아이템이 없을 때 새 아이템 등록 유도 -->
                  <div v-else-if="luckScore < 70 && noGoodItemAvailable" class="recommend-section no-item mt-3">
                    <p class="recommend-text">
                      <i class="fas fa-box-open text-info me-1"></i>
                      등록해주신 아이템 중 오늘 행운을 확실히 가져다줄만한 아이템이 없어요.
                    </p>
                    <router-link to="/items/upload" class="btn btn-outline-primary btn-sm rounded-pill mt-2">
                      <i class="fas fa-plus me-1"></i> 새 아이템 등록하기
                    </router-link>
                  </div>
                </div>

                <!-- 주요 색상 -->
                <h5 class="fw-bold mb-3"><i class="fas fa-palette text-primary"></i> 주요 색상</h5>
                <div v-if="item.dominant_colors && item.dominant_colors.length > 0" class="mb-4">
                  <div
                    v-for="(color, index) in item.dominant_colors"
                    :key="index"
                    class="d-flex align-items-center mb-2"
                  >
                    <div
                      class="rounded-circle border me-3"
                      :style="{
                        width: '30px',
                        height: '30px',
                        backgroundColor: color.hex
                      }"
                    ></div>
                    <div>
                      <span class="fw-bold">{{ color.korean_name }}</span>
                      <small class="text-muted ms-2">({{ color.hex }})</small>
                    </div>
                  </div>
                </div>
                <p v-else class="text-muted mb-4">분석된 색상 정보가 없습니다.</p>

                <!-- AI 분석 결과 - 해시태그만 표시 -->
                <div v-if="aiAnalysis.tags && aiAnalysis.tags.length > 0" class="mb-4">
                  <h5 class="fw-bold mb-3"><i class="fas fa-robot text-success"></i> AI 분석 결과</h5>
                  <div class="d-flex flex-wrap gap-2">
                    <span
                      v-for="(tag, index) in aiAnalysis.tags.slice(0, 4)"
                      :key="index"
                      class="badge rounded-pill"
                      style="background: rgba(124, 58, 237, 0.3); color: #c4b5fd; font-size: 0.9rem; padding: 10px 16px;"
                    >
                      #{{ tag }}
                    </span>
                  </div>
                </div>

                <!-- 운세별 보완력 (운세 있을 때만) -->
                <div v-if="fortuneStore.hasTodayFortune" class="fortune-boost-section mb-4">
                  <h5 class="fw-bold mb-3"><i class="fas fa-chart-bar text-info"></i> 운세별 보완력</h5>
                  <p class="text-muted small mb-3">이 아이템이 각 운세에 얼마나 도움을 줄 수 있는지 나타냅니다</p>
                  <div class="fortune-stats">
                    <div v-for="cat in fortuneCategories" :key="cat.key" class="stat-row">
                      <span class="stat-label">
                        <i :class="'fas ' + cat.icon" :style="{ color: cat.color }"></i>
                        {{ cat.label }}
                      </span>
                      <div class="stat-bar-container">
                        <div
                          class="stat-bar"
                          :style="{
                            width: getFortuneBoost(cat.key) + '%',
                            background: `linear-gradient(90deg, ${cat.color}, ${cat.color}dd)`
                          }"
                        ></div>
                      </div>
                      <span class="stat-value" :style="{ color: cat.color }">{{ getFortuneBoost(cat.key) }}</span>
                    </div>
                  </div>
                  <div v-if="primaryFortuneTag" class="mt-3 text-center">
                    <span class="badge rounded-pill px-3 py-2" :style="{ background: getPrimaryFortuneColor(), color: '#fff' }">
                      <i class="fas fa-star me-1"></i> {{ primaryFortuneTag }} 보완에 최적화된 아이템
                    </span>
                  </div>
                </div>

                <div class="d-grid gap-3 mt-4">
                  <router-link to="/items" class="btn btn-outline-light rounded-pill py-2">
                    <i class="fas fa-list me-2"></i> 목록으로 돌아가기
                  </router-link>
                  <button class="btn btn-outline-danger rounded-pill py-2" @click="handleDelete">
                    <i class="fas fa-trash me-2"></i> 삭제하기
                  </button>
                </div>
              </div>
        </div>

        <!-- Loading State -->
        <div v-else class="card-base card-lg">
          <div class="empty-state">
            <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="empty-text">아이템 정보를 불러오는 중...</p>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'
import { getColorMatchScore, colorMap } from '@/utils/colors'
import { getFortuneBoostScore, fortuneKeywords } from '@/utils/similarity'
import { getMaxSimilarityWithLuckyItems, similarityToScore } from '@/utils/itemSimilarity'
import { useFortuneStore } from '@/stores/fortune'

const route = useRoute()
const router = useRouter()
const fortuneStore = useFortuneStore()
const item = ref(null)
const isEditing = ref(false)
const isSaving = ref(false)
const editForm = ref({
  item_name: '',
  main_category: ''
})
const userItems = ref([]) // 다른 아이템 추천용

// 카테고리 한글 매핑
const categoryDisplayMap = {
  'clothing': '의류',
  'cosmetics': '화장품',
  'electronics': '전자제품',
  'accessories': '악세서리',
  'etc': '기타'
}

// AI 분석 결과 computed
const aiAnalysis = computed(() => {
  if (!item.value) return {}
  return item.value.ai_analysis_result || item.value.ai_analysis || {}
})

// 운세 카테고리 정의
const fortuneCategories = [
  { key: 'overall', label: '종합운', icon: 'fa-star', color: '#a78bfa' },
  { key: 'love', label: '애정운', icon: 'fa-heart', color: '#f472b6' },
  { key: 'money', label: '금전운', icon: 'fa-coins', color: '#facc15' },
  { key: 'work', label: '직장운', icon: 'fa-briefcase', color: '#60a5fa' },
  { key: 'health', label: '건강운', icon: 'fa-heartbeat', color: '#4ade80' },
  { key: 'study', label: '학업운', icon: 'fa-book', color: '#38bdf8' }
]

// 아이템의 운세별 보완 점수 계산 (유틸리티 사용)
const getFortuneBoost = (category) => {
  return getFortuneBoostScore(item.value, fortuneStore.luckyColors, category, getColorMatchScore, fortuneStore.luckyItem)
}

// 주요 운세 태그 찾기 (가장 높은 점수의 운세)
const primaryFortuneTag = computed(() => {
  const itemTags = aiAnalysis.value?.tags || []

  for (const [key, keywords] of Object.entries(fortuneKeywords)) {
    if (key === 'overall') continue
    for (const keyword of keywords) {
      if (itemTags.some(tag => tag.includes(keyword) || keyword.includes(tag))) {
        return fortuneCategories.find(c => c.key === key)?.label || null
      }
    }
  }
  return null
})

// 주요 운세의 색상 가져오기
const getPrimaryFortuneColor = () => {
  if (!primaryFortuneTag.value) return '#a78bfa'
  const cat = fortuneCategories.find(c => c.label === primaryFortuneTag.value)
  return cat?.color || '#a78bfa'
}

// ===== 행운 지수 계산 로직 =====

// HEX를 RGB로 변환
const hexToRgb = (hex) => {
  if (!hex) return { r: 128, g: 128, b: 128 }
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : { r: 128, g: 128, b: 128 }
}

// 유클리드 거리 계산
const euclideanDistance = (rgb1, rgb2) => {
  return Math.sqrt(
    Math.pow(rgb1.r - rgb2.r, 2) +
    Math.pow(rgb1.g - rgb2.g, 2) +
    Math.pow(rgb1.b - rgb2.b, 2)
  )
}

// 거리를 점수로 변환 (0-100) - 더 엄격한 비선형 계산
const distanceToScore = (distance) => {
  const maxDistance = Math.sqrt(255 * 255 * 3) // ~441.67

  // 거리 임계값 설정 (더 엄격하게)
  // 거리 0-50: 90-100점 (거의 같은 색)
  // 거리 50-100: 70-90점 (비슷한 색)
  // 거리 100-150: 50-70점 (약간 다른 색)
  // 거리 150-200: 30-50점 (다른 색)
  // 거리 200+: 0-30점 (완전히 다른 색)

  if (distance <= 50) {
    return Math.round(90 + (50 - distance) / 50 * 10)
  } else if (distance <= 100) {
    return Math.round(70 + (100 - distance) / 50 * 20)
  } else if (distance <= 150) {
    return Math.round(50 + (150 - distance) / 50 * 20)
  } else if (distance <= 200) {
    return Math.round(30 + (200 - distance) / 50 * 20)
  } else {
    return Math.round(Math.max(0, 30 - (distance - 200) / (maxDistance - 200) * 30))
  }
}

// 아이템 색상과 행운색 매칭 계산 (색상 40% + 아이템 유사도 60%)
// FastText(cc.ko.300) 기반 의미적 유사도 사용
const colorMatchResult = computed(() => {
  if (!item.value?.dominant_colors || !fortuneStore.luckyColors?.length) {
    return { score: 0, matchedColor: null, bestItemHex: '#808080' }
  }

  const itemColors = item.value.dominant_colors
  const luckyColorNames = fortuneStore.luckyColors

  // 행운색 이름을 HEX로 변환
  const luckyColorHexes = luckyColorNames.map(name => ({
    name,
    hex: colorMap[name] || '#808080'
  }))

  let maxColorScore = 0
  let matchedColor = null
  let bestItemHex = itemColors[0]?.hex || '#808080'

  for (const itemColor of itemColors) {
    const itemHex = itemColor.hex || '#808080'
    const itemRgb = hexToRgb(itemHex)

    for (const luckyColor of luckyColorHexes) {
      const luckyRgb = hexToRgb(luckyColor.hex)
      const distance = euclideanDistance(itemRgb, luckyRgb)
      const score = distanceToScore(distance)

      if (score > maxColorScore) {
        maxColorScore = score
        matchedColor = luckyColor.name
        bestItemHex = itemHex
      }
    }
  }

  // 아이템 유사도 계산 (FastText 기반 코사인 유사도)
  let itemScore = 0
  const luckyItem = fortuneStore.luckyItem
  if (luckyItem && item.value?.item_name) {
    const luckyItemList = [
      luckyItem.main,
      luckyItem.zodiac,
      luckyItem.today_special
    ].filter(Boolean)

    const { similarity } = getMaxSimilarityWithLuckyItems(item.value.item_name, luckyItemList)
    itemScore = similarityToScore(similarity)
  }

  // 최종 점수: 색상 40% + 아이템 유사도 60%
  const finalScore = Math.min(100, Math.round(maxColorScore * 0.4 + itemScore * 0.6))

  return { score: finalScore, matchedColor, bestItemHex }
})

// 행운 지수
const luckScore = computed(() => colorMatchResult.value.score)

// 행운 지수 원형 프로그레스 오프셋
const luckProgressOffset = computed(() => {
  const circumference = 2 * Math.PI * 50
  return circumference - (luckScore.value / 100 * circumference)
})

// 행운 지수 색상 (점수에 따라)
const luckScoreColor = computed(() => {
  const score = luckScore.value
  if (score >= 70) return '#10b981' // 녹색
  if (score >= 50) return '#3b82f6' // 파란색
  if (score >= 35) return '#f59e0b' // 주황색
  return '#ef4444' // 빨간색
})

// 아이템 색상 (가장 매칭되는)
const bestItemColor = computed(() => colorMatchResult.value.bestItemHex)

// 매칭된 행운색
const matchedLuckyColor = computed(() => {
  const matched = colorMatchResult.value.matchedColor
  return matched ? (colorMap[matched] || '#808080') : '#808080'
})

// 매치 메시지 (더 엄격한 기준)
const matchMessage = computed(() => {
  const score = luckScore.value
  if (score >= 95) return '완벽한 매치! 최고의 행운이 함께합니다'
  if (score >= 90) return '훌륭해요! 오늘의 행운과 잘 어울립니다'
  if (score >= 80) return '좋은 선택이에요'
  if (score >= 70) return '나쁘지 않은 선택입니다'
  if (score >= 60) return '무난한 선택입니다'
  if (score >= 50) return '오늘의 운세와는 거리가 있어요'
  return '다른 아이템을 추천드려요'
})

// 매치 아이콘 (더 엄격한 기준)
const matchIcon = computed(() => {
  const score = luckScore.value
  if (score >= 95) return '🎉'
  if (score >= 90) return '✨'
  if (score >= 80) return '👍'
  if (score >= 70) return '🙂'
  if (score >= 60) return '😐'
  if (score >= 50) return '🤔'
  return '💫'
})

// 매치 메시지 클래스
const matchMessageClass = computed(() => {
  const score = luckScore.value
  if (score >= 70) return 'match-good'
  if (score >= 50) return 'match-normal'
  return 'match-low'
})

// 다른 아이템 중 행운색과 가장 잘 맞는 것 추천 (80점 이상만)
const recommendedItem = computed(() => {
  if (luckScore.value >= 70) return null
  if (!userItems.value.length) return null

  const currentItemId = item.value?.id
  let bestItem = null
  let bestScore = 0

  const luckyColorNames = fortuneStore.luckyColors || []
  const luckyColorHexes = luckyColorNames.map(name => ({
    name,
    hex: colorMap[name] || '#808080'
  }))

  for (const otherItem of userItems.value) {
    if (otherItem.id === currentItemId) continue
    if (!otherItem.dominant_colors?.length) continue

    let maxScore = 0
    for (const itemColor of otherItem.dominant_colors) {
      const itemRgb = hexToRgb(itemColor.hex)
      for (const luckyColor of luckyColorHexes) {
        const luckyRgb = hexToRgb(luckyColor.hex)
        const distance = euclideanDistance(itemRgb, luckyRgb)
        const score = distanceToScore(distance)
        if (score > maxScore) maxScore = score
      }
    }

    if (maxScore > bestScore) {
      bestScore = maxScore
      bestItem = otherItem
    }
  }

  // 80점 이상인 아이템만 추천
  if (bestScore < 80) return null
  return bestItem
})

// 추천할 좋은 아이템이 없는 경우 (모든 아이템이 80점 미만)
const noGoodItemAvailable = computed(() => {
  if (luckScore.value >= 70) return false

  const currentItemId = item.value?.id
  const luckyColorNames = fortuneStore.luckyColors || []
  if (!luckyColorNames.length) return false

  const luckyColorHexes = luckyColorNames.map(name => ({
    name,
    hex: colorMap[name] || '#808080'
  }))

  // 아이템이 없거나, 있어도 80점 이상인 게 없으면 true
  if (!userItems.value.length) return true

  for (const otherItem of userItems.value) {
    if (otherItem.id === currentItemId) continue
    if (!otherItem.dominant_colors?.length) continue

    let maxScore = 0
    for (const itemColor of otherItem.dominant_colors) {
      const itemRgb = hexToRgb(itemColor.hex)
      for (const luckyColor of luckyColorHexes) {
        const luckyRgb = hexToRgb(luckyColor.hex)
        const distance = euclideanDistance(itemRgb, luckyRgb)
        const score = distanceToScore(distance)
        if (score > maxScore) maxScore = score
      }
    }

    if (maxScore >= 80) return false
  }

  return true
})

// 유저 아이템 목록 가져오기 (추천용)
const fetchUserItems = async () => {
  try {
    const response = await api.get('/api/items/')
    userItems.value = response.data.items || []
  } catch (error) {
    console.error('아이템 목록 가져오기 실패:', error)
  }
}

const fetchItemDetail = async () => {
  try {
    const itemId = route.params.id
    const response = await api.get(`/api/items/${itemId}/`)
    // API 응답 구조: { success: true, item: {...} }
    const itemData = response.data.item || response.data
    // category_display 추가
    itemData.category_display = categoryDisplayMap[itemData.main_category] || itemData.main_category || '기타'
    // image 필드 매핑 (image_url -> image)
    if (!itemData.image && itemData.image_url) {
      itemData.image = itemData.image_url
    }
    item.value = itemData
  } catch (error) {
    console.error('아이템 상세 정보 가져오기 실패:', error)
    alert('아이템을 찾을 수 없습니다.')
    router.push('/items')
  }
}

// 수정 모드 시작
const startEditing = () => {
  editForm.value = {
    item_name: item.value.item_name,
    main_category: item.value.main_category || 'etc'
  }
  isEditing.value = true
}

// 수정 취소
const cancelEdit = () => {
  isEditing.value = false
  editForm.value = { item_name: '', main_category: '' }
}

// 수정 저장
const saveEdit = async () => {
  if (!editForm.value.item_name.trim()) {
    alert('아이템 이름을 입력해주세요.')
    return
  }

  isSaving.value = true
  try {
    const response = await api.put(`/api/items/${item.value.id}/`, {
      item_name: editForm.value.item_name,
      main_category: editForm.value.main_category
    })

    if (response.data.success) {
      // 로컬 데이터 업데이트
      item.value.item_name = editForm.value.item_name
      item.value.main_category = editForm.value.main_category
      item.value.category_display = categoryDisplayMap[editForm.value.main_category] || '기타'
      isEditing.value = false
      alert('수정되었습니다.')
    } else {
      alert(response.data.message || '수정 중 오류가 발생했습니다.')
    }
  } catch (error) {
    console.error('수정 실패:', error)
    alert('수정 중 오류가 발생했습니다.')
  } finally {
    isSaving.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('정말 이 아이템을 삭제하시겠습니까?')) {
    return
  }

  try {
    const response = await api.delete(`/api/items/${item.value.id}/`)
    if (response.data.success) {
      alert('삭제되었습니다.')
      router.push('/items')
    } else {
      alert(response.data.message || '삭제 중 오류가 발생했습니다.')
    }
  } catch (error) {
    console.error('삭제 실패:', error)
    alert('삭제 중 오류가 발생했습니다.')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '날짜 정보 없음'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '날짜 정보 없음'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}.${month}.${day} ${hour}:${minute}`
}

onMounted(() => {
  fetchItemDetail()
  fetchUserItems()
})
</script>

<style scoped>
/* 아이템 번호 */
.item-number {
  font-size: 0.7em;
  color: #a78bfa;
  background: rgba(124, 58, 237, 0.2);
  padding: 0.2em 0.5em;
  border-radius: 8px;
  margin-left: 0.5rem;
  vertical-align: middle;
}

/* 아이템 이미지 섹션 */
.item-image-container {
  width: 100%;
  max-height: 400px;
  overflow: hidden;
  border-radius: 12px 12px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
}

.item-image {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.item-image-placeholder {
  width: 100%;
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
}

/* 운세별 보완력 섹션 */
.fortune-boost-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.fortune-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  width: 75px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.stat-label i {
  width: 16px;
  text-align: center;
}

.stat-bar-container {
  flex: 1;
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: hidden;
}

.stat-bar {
  height: 100%;
  border-radius: 5px;
  transition: width 0.6s ease-out;
}

.stat-value {
  font-size: 0.9rem;
  font-weight: 700;
  width: 32px;
  text-align: right;
  flex-shrink: 0;
}

/* 운세 미생성 시 유도 배너 */
.fortune-prompt-banner {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(59, 130, 246, 0.2));
  border: 1px solid rgba(124, 58, 237, 0.4);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
}

.fortune-prompt-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.fortune-prompt-icon {
  font-size: 2rem;
  color: #a78bfa;
  flex-shrink: 0;
}

.fortune-prompt-text {
  flex: 1;
  min-width: 200px;
  text-align: center;
}

.fortune-prompt-title {
  color: #fff;
  font-weight: 600;
  margin-bottom: 0.25rem;
  font-size: 1rem;
}

.fortune-prompt-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 0;
}

/* 행운 지수 섹션 */
.luck-score-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.luck-score-circle {
  position: relative;
  width: 120px;
  height: 120px;
}

.luck-score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.luck-score-number {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
}

.luck-score-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-left: 2px;
}

/* 색상 비교 섹션 */
.color-compare-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.color-compare-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.color-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

.color-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.color-compare-arrow {
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.2rem;
  margin-top: 1.2rem;
}

/* 매치 메시지 */
.match-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-size: 0.95rem;
}

.match-message.match-good {
  background: rgba(16, 185, 129, 0.15);
  color: #6ee7b7;
}

.match-message.match-normal {
  background: rgba(59, 130, 246, 0.15);
  color: #93c5fd;
}

.match-message.match-low {
  background: rgba(245, 158, 11, 0.15);
  color: #fcd34d;
}

.match-icon {
  font-size: 1.2rem;
}

/* 아이템 추천 섹션 */
.recommend-section {
  background: rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  text-align: center;
}

.recommend-text {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.85);
}

.recommend-link {
  color: #a78bfa;
  font-weight: 600;
  text-decoration: none;
}

.recommend-link:hover {
  text-decoration: underline;
  color: #c4b5fd;
}

/* 모바일 반응형 */
@media (max-width: 767.98px) {
  .fortune-boost-section {
    padding: 1rem;
  }

  .stat-label {
    font-size: 0.8rem;
    width: 65px;
  }

  .stat-bar-container {
    height: 8px;
  }

  .stat-value {
    font-size: 0.85rem;
    width: 28px;
  }

  .fortune-prompt-banner {
    padding: 1rem;
  }

  .fortune-prompt-icon {
    font-size: 1.5rem;
  }

  .fortune-prompt-title {
    font-size: 0.95rem;
  }

  .fortune-prompt-desc {
    font-size: 0.85rem;
  }

  /* 행운 지수 섹션 모바일 */
  .luck-score-section {
    padding: 1rem;
  }

  .luck-score-circle {
    width: 100px;
    height: 100px;
  }

  .luck-score-circle svg {
    width: 100px;
    height: 100px;
  }

  .luck-score-circle svg circle {
    cx: 50;
    cy: 50;
    r: 42;
  }

  .luck-score-number {
    font-size: 1.6rem;
  }

  .color-compare-section {
    gap: 0.75rem;
  }

  .color-circle {
    width: 32px;
    height: 32px;
  }

  .color-label {
    font-size: 0.8rem;
  }

  .match-message {
    font-size: 0.85rem;
    padding: 0.6rem 0.8rem;
  }

  .recommend-text {
    font-size: 0.85rem;
  }
}

.recommend-section.no-item {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}
</style>
