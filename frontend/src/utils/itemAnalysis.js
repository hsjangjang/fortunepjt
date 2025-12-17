/**
 * 아이템 분석 유틸리티
 * - 행운 점수 계산
 * - 아이템 추천 로직
 * - 에러 메시지 처리
 */

import { calculateLuckScore as calcLuckScoreUtil } from './luckScore'

/**
 * 사용자 아이템 중 가장 행운 점수가 높은 아이템 찾기
 * @param {Array} userItems - 사용자 아이템 목록
 * @param {Array} luckyColorNames - 행운색 이름 목록
 * @param {Array} luckyItemList - 행운 아이템 목록
 * @param {string} excludeItemName - 제외할 아이템 이름 (현재 분석 중인 아이템)
 * @param {number} minScore - 최소 추천 점수 (기본 80)
 * @returns {Object|null} 추천 아이템 또는 null
 */
export const findBestLuckyItem = (userItems, luckyColorNames, luckyItemList, excludeItemName = '', minScore = 80) => {
  if (!userItems?.length || !luckyColorNames?.length) return null

  let bestItem = null
  let bestScore = 0

  for (const item of userItems) {
    // 현재 분석 중인 아이템과 같은 아이템은 제외
    if (excludeItemName && item.item_name === excludeItemName) continue
    if (!item.dominant_colors?.length) continue

    const aiAnalysis = item.ai_analysis || {}
    const aiItemName = aiAnalysis.item_name || item.item_name
    const result = calcLuckScoreUtil(aiItemName, item.dominant_colors, luckyColorNames, luckyItemList)

    if (result.score > bestScore) {
      bestScore = result.score
      bestItem = item
    }
  }

  return bestScore >= minScore ? bestItem : null
}

/**
 * 추천할 좋은 아이템이 없는지 확인
 * @param {Array} userItems - 사용자 아이템 목록
 * @param {Array} luckyColorNames - 행운색 이름 목록
 * @param {Array} luckyItemList - 행운 아이템 목록
 * @param {string} excludeItemName - 제외할 아이템 이름
 * @param {number} minScore - 최소 추천 점수 (기본 80)
 * @returns {boolean}
 */
export const hasNoGoodItem = (userItems, luckyColorNames, luckyItemList, excludeItemName = '', minScore = 80) => {
  if (!luckyColorNames?.length) return false
  if (!userItems?.length) return true

  for (const item of userItems) {
    if (excludeItemName && item.item_name === excludeItemName) continue
    if (!item.dominant_colors?.length) continue

    const aiAnalysis = item.ai_analysis || {}
    const aiItemName = aiAnalysis.item_name || item.item_name
    const result = calcLuckScoreUtil(aiItemName, item.dominant_colors, luckyColorNames, luckyItemList)

    if (result.score >= minScore) return false
  }

  return true
}

/**
 * API 에러 메시지 생성
 * @param {Error} error - Axios 에러 객체
 * @returns {string} 사용자 친화적인 에러 메시지
 */
export const getAnalysisErrorMessage = (error) => {
  if (error.response) {
    const status = error.response.status
    const messages = {
      413: '파일 용량이 너무 큽니다. 최대 10MB까지 업로드 가능합니다.',
      503: error.response.data?.message || 'AI 분석 서비스가 일시적으로 제한되었습니다. 잠시 후 다시 시도해주세요.',
      400: error.response.data?.message || '잘못된 요청입니다.',
      500: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
    }
    return messages[status] || `서버 오류 (${status})`
  }

  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return '요청 시간이 초과되었습니다. 다시 시도해주세요.'
  }

  if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
    return '파일 업로드에 실패했습니다. 파일 크기를 확인해주세요. (최대 10MB)'
  }

  if (error.request) {
    return '서버 응답이 없습니다. 잠시 후 다시 시도해주세요.'
  }

  return '분석 중 오류가 발생했습니다.'
}

/**
 * 파일 유효성 검사
 * @param {File} file - 업로드된 파일
 * @param {number} maxSizeMB - 최대 파일 크기 (MB)
 * @returns {{valid: boolean, error: string|null}}
 */
export const validateImageFile = (file, maxSizeMB = 10) => {
  if (!file.type.startsWith('image/')) {
    return { valid: false, error: '이미지 파일만 업로드 가능합니다.' }
  }

  if (file.size > maxSizeMB * 1024 * 1024) {
    return { valid: false, error: `파일 크기는 ${maxSizeMB}MB 이하여야 합니다.` }
  }

  return { valid: true, error: null }
}

/**
 * 날짜 포맷팅 (YYYY.MM.DD)
 * @param {string} dateString - ISO 날짜 문자열
 * @returns {string}
 */
export const formatItemDate = (dateString) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}
