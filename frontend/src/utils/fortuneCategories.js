/**
 * 운세 카테고리 공통 상수
 * - List.vue, Detail.vue 등에서 공유
 */

export const FORTUNE_CATEGORIES = [
  { key: 'overall', label: '종합운', icon: 'fa-star', color: '#a78bfa' },
  { key: 'love', label: '애정운', icon: 'fa-heart', color: '#f472b6' },
  { key: 'money', label: '금전운', icon: 'fa-coins', color: '#facc15' },
  { key: 'work', label: '직장운', icon: 'fa-briefcase', color: '#60a5fa' },
  { key: 'health', label: '건강운', icon: 'fa-heartbeat', color: '#4ade80' },
  { key: 'study', label: '학업운', icon: 'fa-book', color: '#38bdf8' }
]

/**
 * 카테고리 키로 카테고리 정보 찾기
 * @param {string} key - 카테고리 키 (overall, love, money, etc.)
 * @returns {Object|undefined} 카테고리 정보
 */
export const getCategoryByKey = (key) => {
  return FORTUNE_CATEGORIES.find(c => c.key === key)
}

/**
 * 카테고리 키로 색상 가져오기
 * @param {string} key - 카테고리 키
 * @returns {string} 색상 HEX 값
 */
export const getCategoryColor = (key) => {
  return getCategoryByKey(key)?.color || '#a78bfa'
}

/**
 * 카테고리 키로 라벨 가져오기
 * @param {string} key - 카테고리 키
 * @returns {string} 카테고리 라벨
 */
export const getCategoryLabel = (key) => {
  return getCategoryByKey(key)?.label || '종합운'
}
