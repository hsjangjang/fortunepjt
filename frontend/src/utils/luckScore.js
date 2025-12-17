/**
 * 행운 점수 계산 유틸리티
 * - 색상 매칭 + 아이템 유사도 기반 종합 점수 계산
 * - 점수 구간별 메시지 및 아이콘 제공
 * - 하이브리드 유사도 (FastText + GMS Embedding) 지원
 */

import { calculateColorMatchScore } from './colorDistance'
import { getMaxSimilarityWithLuckyItems, getHybridSimilarity, similarityToScore } from './itemSimilarity'

// 점수 가중치 상수
const SCORE_WEIGHTS = {
  BASE: 35,      // 기본 점수 (35점)
  COLOR: 0.35,   // 색상 매칭 가중치 (35점 만점)
  ITEM: 0.30     // 아이템 유사도 가중치 (30점 만점)
}

// 점수 구간별 메시지 설정
const SCORE_MESSAGES = [
  { min: 95, title: '🎉 완벽한 매치!', shortMsg: '완벽한 매치! 최고의 행운이 함께합니다', icon: '🎉' },
  { min: 90, title: '✨ 훌륭한 매치!', shortMsg: '훌륭해요! 오늘의 행운과 잘 어울립니다', icon: '✨' },
  { min: 80, title: '👍 좋은 매치', shortMsg: '좋은 선택이에요', icon: '👍' },
  { min: 70, title: '🙂 나쁘지 않은 선택', shortMsg: '나쁘지 않은 선택입니다', icon: '🙂' },
  { min: 60, title: '😐 무난한 선택', shortMsg: '무난한 선택입니다', icon: '😐' },
  { min: 50, title: '🤔 조금 아쉬운 선택', shortMsg: '오늘의 운세와는 거리가 있어요', icon: '🤔' },
  { min: 0, title: '💫 다른 아이템 추천', shortMsg: '다른 아이템을 추천드려요', icon: '💫' }
]

// 점수별 색상 설정
const SCORE_COLORS = [
  { min: 70, color: '#10b981' },  // 녹색
  { min: 50, color: '#3b82f6' },  // 파란색
  { min: 35, color: '#f59e0b' },  // 주황색
  { min: 0, color: '#ef4444' }    // 빨간색
]

/**
 * 행운 점수 계산 - 동기 버전 (FastText만 사용)
 * 기본 35점 + 색상 35점 + 아이템 유사도 30점
 * @param {string} itemName - 아이템 이름
 * @param {Array<{hex: string}>} itemColors - 아이템 색상 배열
 * @param {string[]} luckyColorNames - 행운색 이름 배열
 * @param {string[]} luckyItemList - 행운 아이템 이름 배열
 * @returns {{score: number, matchedColor: string|null, bestItemHex: string|null, itemSimilarity: number}}
 */
export const calculateLuckScore = (itemName, itemColors, luckyColorNames, luckyItemList) => {
  // 1. 색상 점수 계산 (0-35점)
  const colorResult = calculateColorMatchScore(itemColors, luckyColorNames)
  const colorScore = Math.round(colorResult.score * SCORE_WEIGHTS.COLOR)

  // 2. 아이템 유사도 계산 (0-30점) - FastText
  const { similarity } = getMaxSimilarityWithLuckyItems(itemName, luckyItemList)
  const itemScoreRaw = similarityToScore(similarity)
  const itemScore = Math.round(itemScoreRaw * SCORE_WEIGHTS.ITEM)

  // 3. 최종 점수: 기본 35점 + 색상 35점 + 아이템 30점
  const finalScore = Math.min(100, SCORE_WEIGHTS.BASE + itemScore + colorScore)

  return {
    score: finalScore,
    matchedColor: colorResult.matchedColor,
    bestItemHex: colorResult.bestItemHex,
    itemSimilarity: similarity,
    colorScore,
    itemScore,
    source: 'fasttext'
  }
}

/**
 * 행운 점수 계산 - 비동기 하이브리드 버전 (FastText + GMS Embedding)
 * 두 방식 중 높은 유사도 점수를 사용
 * @param {string} itemName - 아이템 이름
 * @param {Array<{hex: string}>} itemColors - 아이템 색상 배열
 * @param {string[]} luckyColorNames - 행운색 이름 배열
 * @param {string[]} luckyItemList - 행운 아이템 이름 배열
 * @returns {Promise<{score: number, matchedColor: string|null, bestItemHex: string|null, itemSimilarity: number, source: string}>}
 */
export const calculateLuckScoreAsync = async (itemName, itemColors, luckyColorNames, luckyItemList) => {
  // 1. 색상 점수 계산 (0-35점) - 동기
  const colorResult = calculateColorMatchScore(itemColors, luckyColorNames)
  const colorScore = Math.round(colorResult.score * SCORE_WEIGHTS.COLOR)

  // 2. 아이템 유사도 계산 (0-30점) - 하이브리드 (비동기)
  const { similarity, source } = await getHybridSimilarity(itemName, luckyItemList)
  const itemScoreRaw = similarityToScore(similarity)
  const itemScore = Math.round(itemScoreRaw * SCORE_WEIGHTS.ITEM)

  // 3. 최종 점수: 기본 35점 + 색상 35점 + 아이템 30점
  const finalScore = Math.min(100, SCORE_WEIGHTS.BASE + itemScore + colorScore)

  return {
    score: finalScore,
    matchedColor: colorResult.matchedColor,
    bestItemHex: colorResult.bestItemHex,
    itemSimilarity: similarity,
    colorScore,
    itemScore,
    source  // 'fasttext' 또는 'embedding'
  }
}

/**
 * 점수에 따른 메시지 정보 가져오기
 * @param {number} score - 점수 (0-100)
 * @returns {{title: string, shortMsg: string, icon: string}}
 */
export const getScoreMessage = (score) => {
  const msg = SCORE_MESSAGES.find(m => score >= m.min)
  return msg || SCORE_MESSAGES[SCORE_MESSAGES.length - 1]
}

/**
 * 점수에 따른 색상 가져오기
 * @param {number} score - 점수 (0-100)
 * @returns {string} HEX 색상 코드
 */
export const getScoreColor = (score) => {
  const config = SCORE_COLORS.find(c => score >= c.min)
  return config?.color || '#ef4444'
}

/**
 * 점수에 따른 상세 설명 생성
 * @param {number} score - 점수
 * @param {string} itemName - 아이템 이름
 * @param {string|null} matchedColor - 매칭된 행운색
 * @param {string} recommendedItem - 추천 아이템 이름
 * @returns {string} 설명 텍스트
 */
export const generateMatchDescription = (score, itemName, matchedColor, recommendedItem) => {
  const colorText = matchedColor ? `${matchedColor} 색상이 ` : ''

  if (score >= 95) {
    return `${itemName}이(가) 오늘의 행운 아이템과 완벽하게 일치합니다! 최고의 행운이 함께할 것입니다.`
  } else if (score >= 90) {
    return `${itemName}이(가) 오늘의 행운과 잘 어울립니다. ${colorText}행운을 더해줄 것입니다.`
  } else if (score >= 80) {
    return `${itemName}이(가) 오늘의 운세와 어울립니다. 긍정적인 에너지를 느낄 수 있을 거예요.`
  } else if (score >= 70) {
    return `${itemName}은(는) 괜찮은 선택입니다. ${colorText ? colorText + '도움이 됩니다.' : ''}`
  } else if (score >= 60) {
    return `${itemName}은(는) 평범한 선택입니다. 행운 아이템인 '${recommendedItem}'을 활용해보세요.`
  } else if (score >= 50) {
    return `${itemName}은(는) 오늘의 운세와 조금 거리가 있어요. '${recommendedItem}'을 추천드립니다.`
  } else {
    return `'${recommendedItem}' 같은 행운 아이템을 함께 사용하면 좋은 결과가 있을 거예요!`
  }
}

/**
 * 원형 프로그레스 오프셋 계산
 * @param {number} score - 점수 (0-100)
 * @param {number} radius - 원의 반지름 (기본값: 50)
 * @returns {number} stroke-dashoffset 값
 */
export const calculateProgressOffset = (score, radius = 50) => {
  const circumference = 2 * Math.PI * radius
  return circumference - (score / 100 * circumference)
}
