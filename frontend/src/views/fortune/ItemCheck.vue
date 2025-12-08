        </div>

        <!-- Item Selection Modal -->
        <div v-if="showItemModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
          <div class="modal-dialog modal-lg">
            <div class="modal-content glass-card border-0" style="background: #1e293b;">
              <div class="modal-header border-bottom border-secondary border-opacity-25">
                <h5 class="modal-title text-white"><i class="fas fa-folder-open me-2"></i> 내 아이템 선택</h5>
                <button type="button" class="btn-close btn-close-white" @click="showItemModal = false"></button>
              </div>
              <div class="modal-body">
                <div class="row g-3">
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
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'
import { API_BASE_URL } from '@/config/api'

const authStore = useAuthStore()

// 이미지 URL에 base URL 추가
const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}
const fileInput = ref(null)
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

const colorMap = {
  '빨간색': '#FF0000', '진한 빨간색': '#8B0000', '주황색': '#FFA500', '노란색': '#FFFF00',
  '초록색': '#00FF00', '연두색': '#90EE90', '하늘색': '#87CEEB',
  '파란색': '#0000FF', '남색': '#000080', '보라색': '#800080',
  '분홍색': '#FFC0CB', '갈색': '#8B4513', '베이지색': '#F5DEB3',
  '검은색': '#000000', '흰색': '#FFFFFF', '회색': '#808080', '금색': '#FFD700'
}

const getTextColor = (hex) => {
  const r = parseInt(hex.substr(1, 2), 16)
  const g = parseInt(hex.substr(3, 2), 16)
  const b = parseInt(hex.substr(5, 2), 16)
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
  return (yiq >= 128) ? '#000' : '#fff'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

const triggerFileInput = () => {
  fileInput.value.click()
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
    alert('이미지 파일만 업로드 가능합니다.')
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    alert('파일 크기는 10MB 이하여야 합니다.')
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
  // 분석 시작 시 이전 결과 초기화
  detectedItem.value = '분석 중...'
  detectedColors.value = []
  itemColor.value = 'rgba(255,255,255,0.1)'
  displayLuckScore.value = 0
  luckScore.value = 0
  matchTitle.value = '분석 중...'
  matchDescription.value = '아이템을 분석하고 있습니다.'

  const formData = new FormData()
  formData.append('image', file)
  formData.append('item_name', '임시_' + Date.now())
  formData.append('category', 'etc')
  formData.append('is_temporary', 'true')

  try {
    const response = await api.post('/api/items/analyze/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const data = response.data

    if (data.success) {
      const analysis = data.analysis
      const colors = analysis.colors || []

      detectedItem.value = data.suggested_name || data.item_name || '알 수 없음'
      detectedColors.value = colors.slice(0, 3)

      if (colors.length > 0) {
        itemColor.value = colors[0].hex
        const result = calculateLuckScore(detectedItem.value, colors[0].korean_name)
        animateLuckScore(result.score)
        updateMatchDescription(result.score, detectedItem.value, result.matchedColor)
      }
    } else {
      alert(data.message || '분석에 실패했습니다.')
      resetUpload()
    }
  } catch (error) {
    console.error('분석 실패:', error)
    alert('분석 중 오류가 발생했습니다.')
    resetUpload()
  }
}

const selectExistingItem = (item) => {
  showItemModal.value = false
  itemPreview.value = getImageUrl(item.image)
  showResult.value = true

  // AI 분석 결과에서 아이템 이름 가져오기 (더 정확한 인식)
  const aiAnalysis = item.ai_analysis || {}
  const aiItemName = aiAnalysis.item_name || item.item_name
  detectedItem.value = aiItemName

  const colors = JSON.parse(item.colors_json || '[]')
  detectedColors.value = colors.slice(0, 3)

  if (colors.length > 0) {
    itemColor.value = colors[0].hex
    const result = calculateLuckScore(aiItemName, colors[0].korean_name)
    animateLuckScore(result.score)
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

// 행운 점수 계산 (아이템 유사도 기반 + 색상 추가점)
const calculateLuckScore = (item, color) => {
  let baseScore = 30   // 기본 점수 (낮춤)
  let itemScore = 0    // 아이템 유사도 점수
  let colorScore = 0   // 색상 매칭 점수

  const luckyItemsList = [
    { name: luckyItems.value.main, weight: 40 },        // 메인 아이템: 최대 40점
    { name: luckyItems.value.zodiac, weight: 25 },      // 별자리 아이템: 최대 25점
    { name: luckyItems.value.special, weight: 20 }      // 특별 아이템: 최대 20점
  ].filter(i => i.name)

  const itemLower = (item || '').toLowerCase().trim()

  // 아이템 유사도 계산 (부분 일치, 유사 단어 등)
  for (const luckyItem of luckyItemsList) {
    const luckyLower = (luckyItem.name || '').toLowerCase().trim()

    // 완전 일치
    if (itemLower === luckyLower) {
      itemScore = Math.max(itemScore, luckyItem.weight)
      continue
    }

    // 포함 관계 (한쪽이 다른쪽을 포함)
    if (itemLower.includes(luckyLower) || luckyLower.includes(itemLower)) {
      itemScore = Math.max(itemScore, Math.floor(luckyItem.weight * 0.8))
      continue
    }

    // 유사 카테고리 매칭 (키워드 기반)
    const similarity = calculateItemSimilarity(itemLower, luckyLower)
    if (similarity > 0) {
      itemScore = Math.max(itemScore, Math.floor(luckyItem.weight * similarity))
    }
  }

  // 색상 매칭 (최대 15점 추가)
  const luckyColorNames = luckyColorsWithHex.value.map(c => c.name)
  let matchedColor = null

  if (color && luckyColorNames.length > 0) {
    // 1. 정확히 일치하는 경우
    if (luckyColorNames.includes(color)) {
      colorScore = 15
      matchedColor = color
    } else {
      // 2. 유사 색상 매칭 - 가장 가까운 행운색 찾기
      const closestLuckyColor = findClosestLuckyColor(color, luckyColorNames)
      if (closestLuckyColor) {
        colorScore = 10  // 유사 색상은 10점
        matchedColor = closestLuckyColor
      }
    }
  }

  return { score: Math.min(100, baseScore + itemScore + colorScore), matchedColor }
}

// 색상 이름 -> RGB 매핑
const colorToRGB = {
  '빨간색': { r: 255, g: 0, b: 0 },
  '주황색': { r: 255, g: 165, b: 0 },
  '노란색': { r: 255, g: 255, b: 0 },
  '초록색': { r: 0, g: 128, b: 0 },
  '연두색': { r: 144, g: 238, b: 144 },
  '하늘색': { r: 135, g: 206, b: 235 },
  '파란색': { r: 0, g: 0, b: 255 },
  '남색': { r: 0, g: 0, b: 128 },
  '보라색': { r: 128, g: 0, b: 128 },
  '자주색': { r: 128, g: 0, b: 128 },
  '분홍색': { r: 255, g: 192, b: 203 },
  '갈색': { r: 139, g: 69, b: 19 },
  '베이지색': { r: 245, g: 222, b: 179 },
  '검은색': { r: 0, g: 0, b: 0 },
  '흰색': { r: 255, g: 255, b: 255 },
  '회색': { r: 128, g: 128, b: 128 },
  '금색': { r: 255, g: 215, b: 0 }
}

// 가장 가까운 행운색 찾기 (RGB 차이 기반)
const findClosestLuckyColor = (itemColor, luckyColors) => {
  const itemRGB = colorToRGB[itemColor]
  if (!itemRGB || luckyColors.length === 0) {
    return luckyColors[0] || null
  }

  let closestColor = luckyColors[0]
  let minDiff = Infinity

  for (const luckyColorName of luckyColors) {
    const luckyRGB = colorToRGB[luckyColorName]
    if (!luckyRGB) continue

    // RGB 값의 차이 합계 계산
    const diff = Math.abs(itemRGB.r - luckyRGB.r) +
                 Math.abs(itemRGB.g - luckyRGB.g) +
                 Math.abs(itemRGB.b - luckyRGB.b)

    if (diff < minDiff) {
      minDiff = diff
      closestColor = luckyColorName
    }
  }

  return closestColor
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

  if (score >= 85) {
    matchTitle.value = '🎉 완벽한 매치!'
    matchDescription.value = `${item}이(가) 오늘의 행운 아이템과 완벽하게 일치합니다! 최고의 행운이 함께할 것입니다.`
  } else if (score >= 70) {
    matchTitle.value = '✨ 훌륭한 매치!'
    matchDescription.value = `${item}이(가) 오늘의 행운과 잘 어울립니다. ${colorText}행운을 더해줄 것입니다.`
  } else if (score >= 55) {
    matchTitle.value = '👍 좋은 매치'
    matchDescription.value = `${item}이(가) 오늘의 운세와 어느 정도 어울립니다. 긍정적인 에너지를 느낄 수 있을 거예요.`
  } else if (score >= 45) {
    matchTitle.value = '😐 무난한 선택'
    matchDescription.value = `${item}은(는) 평범한 선택입니다. 행운 아이템인 '${luckyItems.value.main || '추천 아이템'}'을 활용해보세요.`
  } else if (score >= 35) {
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
  if (fileInput.value) fileInput.value.value = ''
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

onMounted(() => {
  fetchFortuneData()
  if (authStore.isAuthenticated) {
    fetchUserItems()
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
  max-width: 300px;
  max-height: 300px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.luck-score-circle {
  width: 200px;
  height: 200px;
  position: relative;
  margin: 0 auto;
}

.luck-score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.color-match {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  margin: 30px 0;
}

.color-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.match-arrow {
  font-size: 2rem;
  color: #9ca3af;
}

.modal.show {
  display: block !important;
}

.reference-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
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
/* Responsive Padding */
.responsive-padding {
  padding: 3rem;
}

@media (max-width: 768px) {
  .responsive-padding {
    padding: 3% !important;
  }
  
  .glass-card {
    border-radius: 12px;
    padding: 0 !important; /* Override any other padding */
  }
}
</style>
