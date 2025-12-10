// 아이템-운세 관련도 계산 유틸리티 (간결화 버전)

// 운세 카테고리별 키워드 매핑
export const fortuneKeywords = {
  'overall': ['종합운', '행운', '대박', '럭키', '운세', '길운'],
  'love': ['애정운', '연애운', '사랑', '로맨스', '인연', '매력', '이성', '커플'],
  'money': ['금전운', '재물운', '돈', '부자', '재운', '재물', '경제', '수익', '투자'],
  'work': ['직장운', '사업운', '업무', '승진', '취업', '커리어', '회사', '일'],
  'health': ['건강운', '건강', '체력', '활력', '힐링', '운동', '에너지'],
  'study': ['학업운', '시험운', '공부', '합격', '수험', '학습', '교육', '지식']
}

/**
 * 아이템이 특정 운세 카테고리와 얼마나 관련있는지 점수 계산
 * @param {Object} item - 유저 아이템 { item_name, ai_analysis: { tags: [] } }
 * @param {string} category - 운세 카테고리 (overall, love, money, work, health, study)
 * @returns {number} 0~100 점수
 */
export const getItemCategoryScore = (item, category) => {
  if (!item) return 0

  const itemTags = item.ai_analysis?.tags || []
  const itemName = item.item_name || ''
  const keywords = fortuneKeywords[category] || []

  if (keywords.length === 0) return 0

  // 태그와 아이템명에서 키워드 매칭 확인
  const allTexts = [...itemTags, itemName].join(' ').toLowerCase()

  let matchCount = 0
  let hasDirectMatch = false

  for (const keyword of keywords) {
    if (allTexts.includes(keyword)) {
      matchCount++
      // 직접적인 운세 태그 매칭 (예: #애정운, #금전운)
      if (itemTags.some(tag => tag.includes(keyword))) {
        hasDirectMatch = true
      }
    }
  }

  // 직접 태그 매칭이 있으면 높은 점수
  if (hasDirectMatch) {
    return Math.min(100, 70 + matchCount * 10)
  }

  // 키워드 매칭 비율로 점수 계산
  return Math.min(100, Math.round((matchCount / keywords.length) * 100))
}

/**
 * 아이템의 운세 부스트 점수 계산 (최종 점수)
 * @param {Object} item - 유저 아이템
 * @param {Array} luckyColors - 행운색 배열 ['하늘색', '연두색']
 * @param {string} category - 운세 카테고리
 * @param {Function} getColorMatchScore - 색상 매칭 점수 함수 (colors.js에서 import)
 * @returns {number} 20~100 점수
 */
export const getFortuneBoostScore = (item, luckyColors, category, getColorMatchScore) => {
  if (!item) return 30

  // 1. 아이템-카테고리 관련도 점수 (0~100)
  const categoryScore = getItemCategoryScore(item, category)

  // 2. 색상 유사도 점수 (0~100)
  const colorScore = getColorMatchScore(item.dominant_colors, luckyColors)

  // 3. 종합운은 모든 카테고리 키워드 확인
  let overallBonus = 0
  if (category === 'overall') {
    const allKeywords = Object.values(fortuneKeywords).flat()
    const itemTags = item.ai_analysis?.tags || []
    for (const keyword of allKeywords) {
      if (itemTags.some(tag => tag.includes(keyword))) {
        overallBonus = 15
        break
      }
    }
  }

  // 4. 최종 점수: 카테고리 관련도(50%) + 색상(50%) + 종합운 보너스
  const finalScore = Math.round(categoryScore * 0.5 + colorScore * 0.5) + overallBonus

  return Math.max(20, Math.min(100, finalScore))
}
