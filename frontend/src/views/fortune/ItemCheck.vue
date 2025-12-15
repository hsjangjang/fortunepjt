<template>
  <DefaultLayout>
    <div class="page-container">
      <div class="content-wrapper wide">
        <!-- 페이지 헤더 -->
        <div class="page-header">
          <h1 class="page-title">
            <i class="fas fa-search" style="color: #a78bfa !important;"></i>
            아이템 행운도 측정
          </h1>
          <p class="page-subtitle">
            가지고 있는 아이템을 촬영하거나 업로드하여<br>
            오늘의 행운 아이템과 얼마나 일치하는지 확인해보세요!
          </p>
        </div>

        <div class="card-base card-lg">

            <!-- Upload Area -->
            <div v-if="!showResult"
                 class="upload-area"
                 :class="{ dragover: isDragging }"
                 @dragover.prevent="isDragging = true"
                 @dragleave="isDragging = false"
                 @drop.prevent="handleDrop">
              <i class="fas fa-camera fa-3x mb-3" style="color: #a78bfa;"></i>
              <h4 class="text-white">아이템 사진을 업로드하세요</h4>
              <p class="text-white opacity-50 mb-4">
                JPG, PNG 파일 (최대 10MB)
              </p>
              <div class="d-flex justify-content-center gap-3 flex-wrap">
                <button class="btn btn-primary rounded-pill upload-btn" @click="triggerCameraInput">
                  <i class="fas fa-camera me-2"></i> 카메라로 촬영
                </button>
                <button class="btn btn-outline-light rounded-pill upload-btn" @click="triggerGalleryInput">
                  <i class="fas fa-images me-2"></i> 갤러리에서 선택
                </button>
              </div>
              <!-- 카메라용 input -->
              <input
                type="file"
                ref="cameraInput"
                accept="image/*"
                capture="environment"
                style="display: none;"
                @change="handleFileSelect">
              <!-- 갤러리용 input -->
              <input
                type="file"
                ref="galleryInput"
                accept="image/*"
                style="display: none;"
                @change="handleFileSelect">
            </div>

            <!-- Select from My Items Button -->
            <div v-if="!showResult" class="text-center mt-4">
              <button class="btn btn-outline-light rounded-pill px-4" @click="showItemModal = true">
                <i class="fas fa-folder-open me-2"></i> 내 아이템에서 선택하기
              </button>
            </div>
            
             <!-- Analysis Result -->
            <div v-if="showResult" class="result-card card-base card-md mt-4">
              <div class="card-body">
                <h4 class="text-center text-white mb-4">분석 결과</h4>

                <!-- Item Preview -->
                <div class="text-center mb-4">
                  <img :src="itemPreview" alt="업로드된 아이템" class="item-preview" style="border: 1px solid rgba(255,255,255,0.2);">
                </div>

                <!-- Detected Item Info -->
                <div class="text-center mb-4">
                  <h5 class="text-primary-light">인식된 아이템</h5>
                  <p class="fs-4 text-white fw-bold mb-3">{{ detectedItem }}</p>
                  <h5 class="text-primary-light">감지된 색상</h5>
                  <div class="d-flex align-items-center justify-content-center gap-2 pb-2">
                    <div v-for="color in detectedColors" :key="color.hex"
                         class="flex-shrink-0"
                         :style="`width: 40px; height: 40px; border-radius: 50%; background: ${color.hex}; box-shadow: 0 2px 8px rgba(0,0,0,0.2);`"></div>
                  </div>
                </div>

                <!-- Luck Score -->
                <div class="text-center">
                  <div class="luck-score-circle mx-auto">
                    <svg width="200" height="200">
                      <circle cx="100" cy="100" r="90" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="20"></circle>
                      <circle cx="100" cy="100" r="90" fill="none" stroke="url(#luckGradient)"
                              stroke-width="20" stroke-dasharray="565" :stroke-dashoffset="luckProgressOffset"
                              style="transition: stroke-dashoffset 1.5s ease-out; transform: rotate(-90deg); transform-origin: center;"></circle>
                      <defs>
                        <linearGradient id="luckGradient">
                          <stop offset="0%" stop-color="#10b981"></stop>
                          <stop offset="100%" stop-color="#3b82f6"></stop>
                        </linearGradient>
                      </defs>
                    </svg>
                    <div class="luck-score-text">
                      <h1 class="text-white fw-bold mb-0">{{ displayLuckScore }}</h1>
                      <p class="text-white opacity-75 mb-0">행운 지수</p>
                    </div>
                  </div>
                </div>

                <!-- Color Match Visualization -->
                <div class="color-match-container">
                  <div class="color-labels">
                    <span class="text-white opacity-75">아이템 색상</span>
                    <span class="text-white opacity-75">오늘의 행운색</span>
                  </div>
                  <div class="color-circles">
                    <div class="color-circle" :style="`background: ${itemColor}; border: 2px solid rgba(255,255,255,0.2);`"></div>
                    <div class="match-arrow text-white opacity-50">
                      <i class="fas fa-arrows-alt-h"></i>
                    </div>
                    <div class="color-circle" :style="`background: ${luckyColor}; border: 2px solid rgba(255,255,255,0.2);`"></div>
                  </div>
                </div>

                <!-- Match Details -->
                <div class="alert mt-4 text-center" style="background: rgba(124, 58, 237, 0.2); border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 15px;">
                  <h5 class="text-white fw-bold mb-2">{{ matchTitle }}</h5>
                  <p class="text-white opacity-90 mb-0">{{ matchDescription }}</p>
                </div>

                <!-- Today's Lucky Item Reference -->
                <div class="info-box info-primary mt-4">
                  <h6 class="text-white mb-3"><i class="fas fa-star text-warning me-2"></i> 오늘의 행운 아이템</h6>
                  <div class="reference-grid">
                    <div class="reference-item">
                      <span class="label">메인</span>
                      <span class="value">{{ luckyItems.main }}</span>
                    </div>
                    <div class="reference-item">
                      <span class="label">별자리</span>
                      <span class="value">{{ luckyItems.zodiac }}</span>
                    </div>
                  </div>
                  <div class="mt-3 d-flex align-items-center justify-content-center flex-wrap gap-1">
                    <span class="text-white opacity-75 me-2 lucky-color-label"><i class="fas fa-palette text-primary me-1"></i>오늘의 행운색:</span>
                    <span v-for="color in luckyColorsWithHex" :key="color.name"
                          class="badge rounded-pill me-1 border border-light border-opacity-25 flex-shrink-0 px-2"
                          :style="`background-color: ${color.hex}; color: ${getTextColor(color.hex)}; text-shadow: 0 1px 2px rgba(0,0,0,0.3);`">
                      {{ color.name }}
                    </span>
                  </div>
                </div>

                <div class="d-flex flex-column flex-sm-row justify-content-center gap-3 mt-4">
                  <button
                    class="btn btn-primary btn-lg rounded-pill px-4"
                    :disabled="isAnalyzing"
                    @click="resetUpload"
                  >
                    <i class="fas fa-redo me-2"></i> 다른 아이템 측정
                  </button>
                  <button
                    v-if="canSaveItem"
                    class="btn btn-outline-light btn-lg rounded-pill px-4"
                    :disabled="isRegistering || isAnalyzing"
                    @click="registerAsMyItem"
                  >
                    <span v-if="isRegistering">
                      <i class="fas fa-spinner fa-spin me-2"></i> 등록 중...
                    </span>
                    <span v-else>
                      <i class="fas fa-plus me-2"></i> 등록하기
                    </span>
                  </button>
                </div>
              </div>
            </div>

        </div>
      </div>
    </div>

    <!-- Item Selection Modal -->
    <Teleport to="body">
      <div v-if="showItemModal" class="modal-overlay" @click.self="showItemModal = false">
        <div class="modal-container">
          <div class="modal-content-box">
            <div class="modal-header border-bottom border-secondary border-opacity-25">
              <h5 class="modal-title text-white"><i class="fas fa-folder-open me-2"></i> 내 아이템 선택</h5>
              <button type="button" class="btn-close btn-close-white" @click="showItemModal = false"></button>
            </div>
            <div class="modal-body">
              <!-- 등록된 아이템이 없을 때 -->
              <div v-if="!userItems.length" class="text-center py-5">
                <i class="fas fa-box-open fa-3x text-white opacity-50 mb-3"></i>
                <p class="text-white opacity-75 mb-3">등록된 아이템이 없습니다.</p>
                <router-link to="/items/upload" class="btn btn-primary rounded-pill px-4" @click="showItemModal = false">
                  <i class="fas fa-plus me-2"></i> 아이템 등록하기
                </router-link>
              </div>
              <!-- 등록된 아이템이 있을 때 -->
              <div v-else class="row g-3">
                <div v-for="item in userItems" :key="item.id" class="col-md-4">
                  <div class="card h-100 item-select-card border-0"
                       style="cursor: pointer; background: rgba(255,255,255,0.05);"
                       @click="selectExistingItem(item)">
                    <img :src="getImageUrl(item.image)" class="card-img-top" :alt="item.item_name"
                         style="height: 150px; object-fit: cover; opacity: 0.8;">
                    <div class="card-body text-center p-2">
                      <h6 class="mb-1 text-white">{{ item.item_name }}</h6>
                      <small class="text-white opacity-50">{{ formatDate(item.created_at) }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'
import { API_BASE_URL } from '@/config/api'
import { colorMap, getTextColor } from '@/utils/colors'

const router = useRouter()
const authStore = useAuthStore()
const { showToast } = useToast()

// 이미지 URL에 base URL 추가
const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}
const cameraInput = ref(null)
const galleryInput = ref(null)
const isDragging = ref(false)
const showResult = ref(false)
const showItemModal = ref(false)
const itemPreview = ref('')
const detectedItem = ref('분석중...')
const detectedColors = ref([])
const luckScore = ref(0)
const displayLuckScore = ref(0)
const itemColor = ref('rgba(255,255,255,0.1)')
const luckyColor = ref('#667eea')
const matchTitle = ref('분석 중...')
const matchDescription = ref('아이템을 분석하고 있습니다.')
const userItems = ref([])
const currentAnalysisFile = ref(null)  // 분석한 원본 파일 저장
const isFromExistingItem = ref(false)  // 기존 아이템에서 선택한 경우
const isRegistering = ref(false)  // 등록 중 상태
const isAnalyzing = ref(false)  // 분석 중 상태
const analysisResult = ref(null)  // AI 분석 결과 저장
const luckyItems = ref({
  main: '미니 키링',
  zodiac: '실버 키링',
  special: '폰 스트랩'
})
const luckyColorsWithHex = ref([])

const luckProgressOffset = computed(() => {
  const circumference = 2 * Math.PI * 90
  return circumference - (displayLuckScore.value / 100 * circumference)
})

// 저장 가능 여부 (새로 업로드한 아이템만 저장 가능)
// 파일이 없어도 이미지 미리보기(base64)가 있으면 저장 가능
const canSaveItem = computed(() => {
  return showResult.value &&
         (currentAnalysisFile.value !== null || itemPreview.value) &&
         !isFromExistingItem.value &&
         authStore.isAuthenticated
})


const formatDate = (dateString) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

const triggerCameraInput = () => {
  cameraInput.value.click()
}

const triggerGalleryInput = () => {
  galleryInput.value.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    handleFile(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = event.dataTransfer.files
  if (files.length > 0) {
    handleFile(files[0])
  }
}

const handleFile = (file) => {
  if (!file.type.startsWith('image/')) {
    showToast('이미지 파일만 업로드 가능합니다.', 'error')
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    showToast('파일 크기는 10MB 이하여야 합니다.', 'error')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    analyzeItem(file, e.target.result)
  }
  reader.readAsDataURL(file)
}

const analyzeItem = async (file, imageData) => {
  itemPreview.value = imageData
  showResult.value = true
  currentAnalysisFile.value = file  // 원본 파일 저장
  isFromExistingItem.value = false  // 새로 업로드한 아이템
  isAnalyzing.value = true  // 분석 중 상태 설정
  // 분석 시작 시 이전 결과 초기화
  detectedItem.value = '분석 중...'
  detectedColors.value = []
  itemColor.value = 'rgba(255,255,255,0.1)'
  displayLuckScore.value = 0
  luckScore.value = 0
  matchTitle.value = '분석 중...'
  matchDescription.value = '아이템을 분석하고 있습니다.'
  analysisResult.value = null  // 분석 결과 초기화

  const formData = new FormData()
  formData.append('image', file)
  formData.append('item_name', '임시_' + Date.now())
  formData.append('category', 'etc')
  formData.append('is_temporary', 'true')

  try {
    const response = await api.post('/api/items/analyze/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000 // 파일 업로드는 60초 타임아웃
    })
    const data = response.data

    if (data.success) {
      const analysis = data.analysis
      const colors = analysis.colors || []

      detectedItem.value = data.suggested_name || data.item_name || '알 수 없음'
      detectedColors.value = colors.slice(0, 3)

      // AI 분석 결과 저장 (등록 시 사용)
      analysisResult.value = {
        colors: colors,
        ai_analysis: analysis.ai_analysis || {}
      }

      if (colors.length > 0) {
        itemColor.value = colors[0].hex
        const result = calculateLuckScore(detectedItem.value, colors[0].korean_name, colors)
        animateLuckScore(result.score)
        // 가장 매칭된 아이템 색상으로 업데이트
        if (result.bestItemHex) {
          itemColor.value = result.bestItemHex
        }
        updateMatchDescription(result.score, detectedItem.value, result.matchedColor)
      }
      isAnalyzing.value = false  // 분석 완료
    } else {
      showToast(data.message || '분석에 실패했습니다.', 'error')
      resetUpload()
    }
  } catch (error) {
    console.error('분석 실패:', error)
    console.error('에러 상세:', {
      message: error.message,
      code: error.code,
      response: error.response,
      request: error.request ? 'exists' : 'none'
    })

    // 에러 타입에 따른 구체적인 메시지
    let errorMessage = '분석 중 오류가 발생했습니다.'

    if (error.response) {
      const status = error.response.status
      if (status === 413) {
        errorMessage = '파일 용량이 너무 큽니다. 최대 10MB까지 업로드 가능합니다.'
      } else if (status === 503) {
        // API 할당량 초과
        errorMessage = error.response.data?.message || 'AI 분석 서비스가 일시적으로 제한되었습니다. 잠시 후 다시 시도해주세요.'
      } else if (status === 400) {
        errorMessage = error.response.data?.message || '잘못된 요청입니다.'
      } else if (status === 500) {
        errorMessage = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
      } else {
        errorMessage = `서버 오류 (${status})`
      }
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      errorMessage = '요청 시간이 초과되었습니다. 다시 시도해주세요.'
    } else if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
      // 413 에러가 Network Error로 올 수 있음 (nginx가 본문 없이 응답할 때)
      errorMessage = '파일 업로드에 실패했습니다. 파일 크기를 확인해주세요. (최대 10MB)'
    } else if (error.request) {
      errorMessage = '서버 응답이 없습니다. 잠시 후 다시 시도해주세요.'
    }

    showToast(errorMessage, 'error')
    resetUpload()
  }
}

const selectExistingItem = (item) => {
  showItemModal.value = false
  itemPreview.value = getImageUrl(item.image)
  showResult.value = true
  currentAnalysisFile.value = null  // 기존 아이템은 파일 없음
  isFromExistingItem.value = true   // 기존 아이템에서 선택

  // AI 분석 결과에서 아이템 이름 가져오기 (더 정확한 인식)
  const aiAnalysis = item.ai_analysis || {}
  const aiItemName = aiAnalysis.item_name || item.item_name
  detectedItem.value = aiItemName

  const colors = item.dominant_colors || []
  detectedColors.value = colors.slice(0, 3)

  if (colors.length > 0) {
    itemColor.value = colors[0].hex
    const result = calculateLuckScore(aiItemName, colors[0].korean_name, colors)
    animateLuckScore(result.score)
    // 가장 매칭된 아이템 색상으로 업데이트
    if (result.bestItemHex) {
      itemColor.value = result.bestItemHex
    }
    updateMatchDescription(result.score, aiItemName, result.matchedColor)
  }
}

// 아이템 유사도 계산 (카테고리/키워드 기반)
const calculateItemSimilarity = (item1, item2) => {
  const categoryKeywords = {
    '액세서리': ['목걸이', '반지', '팔찌', '귀걸이', '펜던트', '브레이슬릿', '키링', '열쇠고리'],
    '가방류': ['가방', '백', '파우치', '지갑', '캐리어', '토트', '클러치'],
    '전자기기': ['이어폰', '헤드폰', '시계', '카메라', '태블릿', '폰'],
    '패션소품': ['스카프', '모자', '선글라스', '안경', '벨트', '장갑'],
    '필기구': ['펜', '만년필', '다이어리', '노트'],
    '음료용품': ['텀블러', '머그컵', '컵', '보틀']
  }

  let maxSimilarity = 0

  for (const [, keywords] of Object.entries(categoryKeywords)) {
    const item1Match = keywords.some(kw => item1.includes(kw))
    const item2Match = keywords.some(kw => item2.includes(kw))

    if (item1Match && item2Match) {
      maxSimilarity = Math.max(maxSimilarity, 0.5)
    }
  }

  // 공통 단어 체크 (2글자 이상)
  const words1 = item1.split(/[\s,_-]+/)
  const words2 = item2.split(/[\s,_-]+/)

  for (const w1 of words1) {
    for (const w2 of words2) {
      if (w1.length >= 2 && w2.length >= 2) {
        if (w1.includes(w2) || w2.includes(w1)) {
          maxSimilarity = Math.max(maxSimilarity, 0.6)
        }
      }
    }
  }

  return maxSimilarity
}

// 행운 점수 계산 (색상 + 아이템 유사도 반영)
const calculateLuckScore = (item, color, itemColors) => {
  // 1. 색상 점수 계산 (0-100)
  const luckyColorNames = luckyColorsWithHex.value.map(c => c.name)
  const colorResult = calculateColorMatchScore(itemColors || detectedColors.value, luckyColorNames)
  const colorScore = colorResult.score

  // 2. 아이템 유사도 계산 (행운 아이템들과 비교)
  let maxItemSimilarity = 0
  const luckyItemList = [
    luckyItems.value.main,
    luckyItems.value.zodiac,
    luckyItems.value.special
  ].filter(Boolean)

  for (const luckyItem of luckyItemList) {
    const similarity = calculateItemSimilarity(item, luckyItem)
    maxItemSimilarity = Math.max(maxItemSimilarity, similarity)
  }

  // 3. 최종 점수: 색상 70% + 아이템 유사도 30%
  // 아이템 유사도가 0.5 이상이면 보너스 점수 추가
  let finalScore = colorScore
  if (maxItemSimilarity >= 0.5) {
    // 아이템이 비슷하면 색상 점수에 최대 20점 보너스
    const itemBonus = Math.round(maxItemSimilarity * 40)
    finalScore = Math.min(100, Math.round(colorScore * 0.7 + itemBonus))
  }

  return {
    score: finalScore,
    matchedColor: colorResult.matchedColor,
    bestItemHex: colorResult.bestItemHex
  }
}

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

// 유클리드 거리 계산 (0 ~ 441.67 범위, sqrt(255^2 * 3))
const euclideanDistance = (rgb1, rgb2) => {
  return Math.sqrt(
    Math.pow(rgb1.r - rgb2.r, 2) +
    Math.pow(rgb1.g - rgb2.g, 2) +
    Math.pow(rgb1.b - rgb2.b, 2)
  )
}

// 유클리드 거리를 0-100 점수로 변환 - 더 엄격한 비선형 계산
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

// 아이템의 모든 색상과 행운색들 간의 최대 유사도 점수 계산 (유클리드 거리 기반)
const calculateColorMatchScore = (itemColors, luckyColorNames) => {
  if (!itemColors || itemColors.length === 0) return { score: 0, matchedColor: null, bestItemHex: null }
  if (!luckyColorNames || luckyColorNames.length === 0) return { score: 0, matchedColor: null, bestItemHex: null }

  // 행운색 이름을 HEX로 변환
  const luckyColorHexes = luckyColorNames.map(name => ({
    name,
    hex: colorMap[name] || '#808080'
  }))

  let maxScore = 0
  let matchedColor = null
  let bestItemHex = null

  // 아이템 각 색상과 행운색들 간의 유클리드 거리 계산
  for (const itemColor of itemColors) {
    const itemHex = itemColor.hex || '#808080'
    const itemRgb = hexToRgb(itemHex)

    for (const luckyColor of luckyColorHexes) {
      const luckyRgb = hexToRgb(luckyColor.hex)
      const distance = euclideanDistance(itemRgb, luckyRgb)
      const score = distanceToScore(distance)

      if (score > maxScore) {
        maxScore = score
        matchedColor = luckyColor.name
        bestItemHex = itemHex
      }
    }
  }

  return { score: maxScore, matchedColor, bestItemHex }
}

const animateLuckScore = (targetScore) => {
  luckScore.value = targetScore
  let current = 0
  const interval = setInterval(() => {
    if (current < targetScore) {
      current += 2
      displayLuckScore.value = Math.min(current, targetScore)
    } else {
      clearInterval(interval)
    }
  }, 20)
}

// 매치 설명 업데이트 (점수 구간별 세분화)
const updateMatchDescription = (score, item, matchedColor) => {
  // 매칭된 행운색으로 "오늘의 행운색" 원 업데이트
  if (matchedColor && colorMap[matchedColor]) {
    luckyColor.value = colorMap[matchedColor]
  }

  // matchedColor는 실제로 행운색과 매칭된 경우에만 값이 있음
  const colorText = matchedColor ? `${matchedColor} 색상이 ` : ''

  // 더 엄격한 기준
  if (score >= 95) {
    matchTitle.value = '🎉 완벽한 매치!'
    matchDescription.value = `${item}이(가) 오늘의 행운 아이템과 완벽하게 일치합니다! 최고의 행운이 함께할 것입니다.`
  } else if (score >= 90) {
    matchTitle.value = '✨ 훌륭한 매치!'
    matchDescription.value = `${item}이(가) 오늘의 행운과 잘 어울립니다. ${colorText}행운을 더해줄 것입니다.`
  } else if (score >= 80) {
    matchTitle.value = '👍 좋은 매치'
    matchDescription.value = `${item}이(가) 오늘의 운세와 어울립니다. 긍정적인 에너지를 느낄 수 있을 거예요.`
  } else if (score >= 70) {
    matchTitle.value = '🙂 나쁘지 않은 선택'
    matchDescription.value = `${item}은(는) 괜찮은 선택입니다. ${colorText ? colorText + '도움이 됩니다.' : ''}`
  } else if (score >= 60) {
    matchTitle.value = '😐 무난한 선택'
    matchDescription.value = `${item}은(는) 평범한 선택입니다. 행운 아이템인 '${luckyItems.value.main || '추천 아이템'}'을 활용해보세요.`
  } else if (score >= 50) {
    matchTitle.value = '🤔 아쉬운 매치'
    matchDescription.value = `오늘의 행운 아이템과는 거리가 있네요. '${luckyItems.value.main || '추천 아이템'}'이나 '${luckyItems.value.zodiac || '다른 아이템'}'을 고려해보세요.`
  } else {
    matchTitle.value = '💫 다른 아이템을 추천드려요'
    matchDescription.value = `이 아이템보다는 오늘의 행운 아이템 '${luckyItems.value.main || '추천 아이템'}'을 사용해보시는 건 어떨까요?`
  }
}

const resetUpload = () => {
  showResult.value = false
  itemPreview.value = ''
  detectedItem.value = '분석중...'
  detectedColors.value = []
  displayLuckScore.value = 0
  currentAnalysisFile.value = null
  isFromExistingItem.value = false
  isAnalyzing.value = false  // 분석 상태 초기화
  analysisResult.value = null  // 분석 결과 초기화
  if (cameraInput.value) cameraInput.value.value = ''
  if (galleryInput.value) galleryInput.value.value = ''
}

// 내 아이템으로 바로 등록 (분석 결과 그대로 사용)
const registerAsMyItem = async () => {
  if (!currentAnalysisFile.value) {
    showToast('등록할 이미지가 없습니다.', 'error')
    return
  }

  isRegistering.value = true

  try {
    const formData = new FormData()
    formData.append('image', currentAnalysisFile.value)
    formData.append('item_name', detectedItem.value || '새 아이템')
    formData.append('main_category', 'etc')  // 기본 카테고리

    // 이미 분석된 색상과 AI 분석 결과를 함께 전송
    if (analysisResult.value) {
      formData.append('pre_analyzed', 'true')
      formData.append('dominant_colors', JSON.stringify(analysisResult.value.colors || []))
      formData.append('ai_analysis', JSON.stringify(analysisResult.value.ai_analysis || {}))
    }

    const response = await api.post('/api/items/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000
    })

    if (response.data.success) {
      showToast('아이템이 등록되었습니다!', 'success')
      // 내 아이템 목록으로 이동
      router.push('/items')
    } else {
      showToast(response.data.error || '등록에 실패했습니다.', 'error')
    }
  } catch (error) {
    console.error('아이템 등록 실패:', error)
    showToast('등록 중 오류가 발생했습니다.', 'error')
  } finally {
    isRegistering.value = false
  }
}

const fetchFortuneData = async () => {
  try {
    const response = await api.get('/api/fortune/today/')
    const data = response.data

    // API 응답 구조: { success: true, fortune: {...}, date: '...' }
    const fortune = data.fortune || data

    if (fortune.lucky_item) {
      luckyItems.value = {
        main: fortune.lucky_item.main || '미니 키링',
        zodiac: fortune.lucky_item.zodiac || '실버 키링',
        special: fortune.lucky_item.today_special || '폰 스트랩'
      }
    }

    if (fortune.lucky_colors) {
      luckyColorsWithHex.value = fortune.lucky_colors.map(name => ({
        name,
        hex: colorMap[name] || '#7c3aed'
      }))
      if (luckyColorsWithHex.value.length > 0) {
        luckyColor.value = luckyColorsWithHex.value[0].hex
      }
    }
  } catch (error) {
    console.error('운세 정보 가져오기 실패:', error)
  }
}

const fetchUserItems = async () => {
  try {
    const response = await api.get('/api/items/')
    userItems.value = response.data.items || []
  } catch (error) {
    console.error('아이템 목록 가져오기 실패:', error)
  }
}

// 모달 열릴 때 body 스크롤 막기
watch(showItemModal, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  fetchFortuneData()
  if (authStore.isAuthenticated) {
    fetchUserItems()
  }

  // 아이템 상세 페이지에서 넘어온 경우 자동으로 행운 체크
  const savedItem = sessionStorage.getItem('checkLuckItem')
  if (savedItem) {
    try {
      const itemData = JSON.parse(savedItem)
      sessionStorage.removeItem('checkLuckItem') // 사용 후 삭제
      // 약간의 딜레이 후 자동 분석 (운세 데이터 로드 후)
      setTimeout(() => {
        selectExistingItem(itemData)
      }, 500)
    } catch (e) {
      console.error('저장된 아이템 파싱 실패:', e)
    }
  }
})
</script>

<style scoped>
.upload-area {
  border: 3px dashed rgba(124, 58, 237, 0.5);
  border-radius: 20px;
  padding: 60px 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: #7c3aed;
  box-shadow: 0 0 20px rgba(124, 58, 237, 0.2);
}

.upload-area.dragover {
  background: rgba(124, 58, 237, 0.1);
  border-color: #7c3aed;
  transform: scale(1.02);
}

.item-preview {
  width: 100%;
  max-width: 300px;
  max-height: 300px;
  object-fit: contain;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.luck-score-circle {
  width: 200px;
  height: 200px;
  position: relative;
  display: inline-block;
}

.luck-score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.color-match-container {
  margin: 30px 0;
  text-align: center;
}

.color-labels {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 8px;
}

.color-circles {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.color-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.match-arrow {
  font-size: 1.5rem;
  color: #9ca3af;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  overflow-y: auto;
}

.modal-container {
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content-box {
  background: #1e293b;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.modal-content-box .modal-header {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-content-box .modal-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.reference-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.reference-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  background: rgba(255, 255, 255, 0.08);
  padding: 0.75rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.reference-item .label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
  margin-bottom: 0.3rem;
}

.reference-item .value {
  color: #fff;
  font-weight: 600;
  font-size: 0.95rem;
  margin-left: 0;
  word-break: keep-all;
}

/* Result card compact padding */
.result-card .card-body {
  padding: 1rem 0.5rem !important;
}

@media (min-width: 768px) {
  .result-card .card-body {
    padding: 1.5rem !important;
  }
}

/* Responsive Padding - 모바일에서 좌우 여백 최소화 */
.responsive-padding {
  padding: 1.5rem 0.5rem !important;
}

@media (min-width: 768px) {
  .responsive-padding {
    padding: 2rem !important;
  }
}

/* 업로드 버튼 크기 통일 */
.upload-btn {
  min-width: 140px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  white-space: nowrap;
}

@media (max-width: 400px) {
  .upload-btn {
    min-width: 120px;
    padding: 0.45rem 0.8rem;
    font-size: 0.85rem;
  }
}

/* 오늘의 행운색 라벨 스타일 */
.lucky-color-label {
  font-size: 0.875rem;
}
</style>
