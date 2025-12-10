// 아이템-운세 관련도 계산 유틸리티

// 운세 카테고리별 키워드 매핑
export const fortuneKeywords = {
  'overall': ['종합운', '행운', '대박', '럭키', '운세', '길운'],
  'love': ['애정운', '연애운', '사랑', '로맨스', '인연', '매력', '이성', '커플'],
  'money': ['금전운', '재물운', '돈', '부자', '재운', '재물', '경제', '수익', '투자'],
  'work': ['직장운', '사업운', '업무', '승진', '취업', '커리어', '회사', '일'],
  'health': ['건강운', '건강', '체력', '활력', '힐링', '운동', '에너지'],
  'study': ['학업운', '시험운', '공부', '합격', '수험', '학습', '교육', '지식']
}

// 코사인 유사도 계산용 키워드 목록
const featureKeywords = [
  // 운세 관련
  '애정운', '연애운', '사랑', '로맨스', '인연',
  '금전운', '재물운', '돈', '부자', '재물',
  '직장운', '사업운', '업무', '승진', '취업', '커리어',
  '건강운', '건강', '체력', '활력',
  '학업운', '시험운', '공부', '합격', '수험',
  '행운', '대박', '럭키',
  // 아이템 카테고리
  '액세서리', '악세서리', '장신구', '귀걸이', '반지', '목걸이', '팔찌',
  '가방', '파우치', '지갑', '케이스',
  '패션', '의류', '옷', '스카프', '머플러',
  '문구', '펜', '노트', '다이어리', '메모',
  '화장품', '향수', '립밤', '뷰티',
  '시계', '키링', '키홀더', '거울'
]

// 텍스트를 특성 벡터로 변환
const textToVector = (texts) => {
  const vector = new Array(featureKeywords.length).fill(0)
  const textArray = Array.isArray(texts) ? texts : [texts]

  for (let i = 0; i < featureKeywords.length; i++) {
    const keyword = featureKeywords[i]
    for (const text of textArray) {
      if (text && text.includes(keyword)) {
        vector[i] = 1
        break
      }
    }
  }
  return vector
}

// 코사인 유사도 계산
const cosineSimilarity = (vecA, vecB) => {
  let dotProduct = 0
  let normA = 0
  let normB = 0

  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i]
    normA += vecA[i] * vecA[i]
    normB += vecB[i] * vecB[i]
  }

  normA = Math.sqrt(normA)
  normB = Math.sqrt(normB)

  if (normA === 0 || normB === 0) return 0
  return dotProduct / (normA * normB)
}

/**
 * 오늘의 행운 아이템과 유저 아이템의 코사인 유사도 계산
 * @param {Object} item - 유저 아이템 { item_name, ai_analysis: { tags: [] } }
 * @param {Object} luckyItem - 행운 아이템 { main, description, weak_fortunes }
 * @returns {number} 0~100 점수
 */
export const getLuckyItemSimilarity = (item, luckyItem) => {
  if (!item || !luckyItem || !luckyItem.main) return 0

  const itemTags = item.ai_analysis?.tags || []
  const itemName = item.item_name || ''

  // 행운 아이템 텍스트
  const luckyTexts = [
    luckyItem.main || '',
    luckyItem.description || '',
    luckyItem.weak_fortunes || ''
  ]

  // 유저 아이템 텍스트
  const itemTexts = [...itemTags, itemName]

  // 벡터 변환 및 코사인 유사도 계산
  const luckyVector = textToVector(luckyTexts)
  const itemVector = textToVector(itemTexts)

  return Math.round(cosineSimilarity(luckyVector, itemVector) * 100)
}

/**
 * 아이템이 특정 운세 카테고리와 얼마나 관련있는지 점수 계산
 * AI 분석 시 저장된 fortune_scores 사용, 없으면 태그 기반 fallback
 * @param {Object} item - 유저 아이템
 * @param {string} category - 운세 카테고리 (love, money, work, health, study, overall)
 * @returns {number} 0~100 점수
 */
export const getItemCategoryScore = (item, category) => {
  if (!item) return 0

  // 1. AI 분석 시 저장된 fortune_scores가 있으면 사용
  const fortuneScores = item.ai_analysis?.fortune_scores
  if (fortuneScores && category !== 'overall') {
    const score = fortuneScores[category]
    if (typeof score === 'number') {
      return Math.max(0, Math.min(100, score))
    }
  }

  // 2. overall(종합운)이거나 fortune_scores가 없으면 태그 기반 계산
  const itemTags = item.ai_analysis?.tags || []
  const itemName = item.item_name || ''
  const keywords = fortuneKeywords[category] || []

  if (keywords.length === 0) return 0

  const allTexts = [...itemTags, itemName].join(' ').toLowerCase()

  let matchCount = 0
  let hasDirectMatch = false

  for (const keyword of keywords) {
    if (allTexts.includes(keyword)) {
      matchCount++
      if (itemTags.some(tag => tag.includes(keyword))) {
        hasDirectMatch = true
      }
    }
  }

  if (hasDirectMatch) {
    return Math.min(100, 70 + matchCount * 10)
  }

  return Math.min(100, Math.round((matchCount / keywords.length) * 100))
}

/**
 * 아이템의 운세 부스트 점수 계산 (최종 점수)
 * @param {Object} item - 유저 아이템
 * @param {Array} luckyColors - 행운색 배열
 * @param {string} category - 운세 카테고리
 * @param {Function} getColorMatchScore - 색상 매칭 점수 함수
 * @param {Object} luckyItem - 오늘의 행운 아이템
 * @returns {number} 40~90 점수 (종합운은 40~100)
 */
export const getFortuneBoostScore = (item, luckyColors, category, getColorMatchScore, luckyItem) => {
  if (!item) return 40

  // 1. 아이템-카테고리 관련도 점수 (0~100)
  const categoryScore = getItemCategoryScore(item, category)

  // 2. 색상 유사도 점수 (0~100)
  const colorScore = getColorMatchScore(item.dominant_colors, luckyColors)

  // 3. 오늘의 행운 아이템과 코사인 유사도 (0~100)
  const similarityScore = getLuckyItemSimilarity(item, luckyItem)

  // 4. 최종 점수: 카테고리(35%) + 색상(35%) + 행운아이템 유사도(30%)
  const rawScore = Math.round(categoryScore * 0.35 + colorScore * 0.35 + similarityScore * 0.30)

  // 5. 점수 범위 압축: 0~100 → 40~90
  let finalScore = Math.round(40 + (Math.min(100, rawScore) / 100) * 50)
  finalScore = Math.max(40, Math.min(90, finalScore))

  // 6. 종합운 보너스 (40~90 점수 조정 후 추가, 최대 100점 가능)
  if (category === 'overall') {
    const itemTags = item.ai_analysis?.tags || []
    const fortuneCategories = ['love', 'money', 'work', 'health', 'study']
    let matchedCount = 0

    for (const cat of fortuneCategories) {
      const keywords = fortuneKeywords[cat] || []
      if (keywords.some(kw => itemTags.some(tag => tag.includes(kw)))) {
        matchedCount++
      }
    }

    // 매칭된 카테고리 수에 따라 보너스 (최대 5개 × 2점 = 10점)
    const overallBonus = matchedCount * 2
    finalScore = Math.min(100, finalScore + overallBonus)
  }

  return finalScore
}
