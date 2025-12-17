/**
 * 색상 유틸리티 (통합 export)
 * colorMap.js와 colorDistance.js의 기능을 re-export
 */

// colorMap에서 기본 색상 데이터 re-export
export { colorMap, RAINBOW_GRADIENT, isRainbowColor } from './colorMap'

// colorDistance에서 계산 함수 re-export
export { hexToRgb, euclideanDistance, distanceToScore, calculateColorMatchScore } from './colorDistance'

import { calculateColorMatchScore } from './colorDistance'

// 기존 API 호환용: 아이템 색상과 행운색 배열 간의 최대 유사도 점수 (숫자만 반환)
export const getColorMatchScore = (itemColors, luckyColorNames) => {
  const result = calculateColorMatchScore(itemColors, luckyColorNames)
  return result.score
}

import { colorMap, isRainbowColor, RAINBOW_GRADIENT } from './colorMap'

// 색상 배경 스타일 반환 (다양이면 무지개 그라데이션)
export const getColorBackground = (colorNameOrHex) => {
  if (isRainbowColor(colorNameOrHex)) {
    return RAINBOW_GRADIENT
  }
  // HEX 값이면 그대로 반환
  if (colorNameOrHex?.startsWith('#')) {
    return colorNameOrHex
  }
  // 색상 이름이면 HEX로 변환
  return colorMap[colorNameOrHex] || '#808080'
}

// 색상 이름으로 HEX 값 가져오기
export const getColorHex = (colorName) => {
  return colorMap[colorName] || '#8B5CF6'
}

// 배경색에 따른 텍스트 색상 결정 (밝은 배경 -> 어두운 글자)
export const getTextColor = (bgColor) => {
  if (!bgColor) return '#fff'
  const hex = bgColor.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000
  return brightness > 128 ? '#1f2937' : '#fff'
}
