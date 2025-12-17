/**
 * 색상 거리 계산 유틸리티
 * - HEX <-> RGB 변환
 * - 유클리드 거리 계산
 * - 색상 매칭 점수 계산
 */

import { colorMap } from './colorMap'

/**
 * HEX를 RGB로 변환
 * @param {string} hex - HEX 색상 코드 (예: '#FF5733')
 * @returns {{r: number, g: number, b: number}} RGB 객체
 */
export const hexToRgb = (hex) => {
  if (!hex) return { r: 128, g: 128, b: 128 }
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : { r: 128, g: 128, b: 128 }
}

/**
 * 유클리드 거리 계산 (0 ~ 441.67 범위)
 * @param {{r: number, g: number, b: number}} rgb1 - 첫 번째 RGB
 * @param {{r: number, g: number, b: number}} rgb2 - 두 번째 RGB
 * @returns {number} 유클리드 거리
 */
export const euclideanDistance = (rgb1, rgb2) => {
  return Math.sqrt(
    Math.pow(rgb1.r - rgb2.r, 2) +
    Math.pow(rgb1.g - rgb2.g, 2) +
    Math.pow(rgb1.b - rgb2.b, 2)
  )
}

/**
 * 거리 임계값 설정 (엄격한 비선형 계산)
 * - 거리 0-50: 90-100점 (거의 같은 색)
 * - 거리 50-100: 70-90점 (비슷한 색)
 * - 거리 100-150: 50-70점 (약간 다른 색)
 * - 거리 150-200: 30-50점 (다른 색)
 * - 거리 200+: 0-30점 (완전히 다른 색)
 */
const DISTANCE_THRESHOLDS = [
  { max: 50, baseScore: 90, range: 10 },
  { max: 100, baseScore: 70, range: 20 },
  { max: 150, baseScore: 50, range: 20 },
  { max: 200, baseScore: 30, range: 20 }
]

const MAX_DISTANCE = Math.sqrt(255 * 255 * 3) // ~441.67

/**
 * 유클리드 거리를 0-100 점수로 변환
 * @param {number} distance - 유클리드 거리
 * @returns {number} 점수 (0-100)
 */
export const distanceToScore = (distance) => {
  let prevMax = 0

  for (const threshold of DISTANCE_THRESHOLDS) {
    if (distance <= threshold.max) {
      const ratio = (threshold.max - distance) / (threshold.max - prevMax)
      return Math.round(threshold.baseScore + ratio * threshold.range)
    }
    prevMax = threshold.max
  }

  // 거리 200+ 처리
  return Math.round(Math.max(0, 30 - (distance - 200) / (MAX_DISTANCE - 200) * 30))
}

/**
 * 아이템 색상과 행운색 간의 최대 유사도 점수 계산
 * @param {Array<{hex: string}>} itemColors - 아이템 색상 배열
 * @param {string[]} luckyColorNames - 행운색 이름 배열
 * @returns {{score: number, matchedColor: string|null, bestItemHex: string|null}}
 */
export const calculateColorMatchScore = (itemColors, luckyColorNames) => {
  if (!itemColors?.length || !luckyColorNames?.length) {
    return { score: 0, matchedColor: null, bestItemHex: null }
  }

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
