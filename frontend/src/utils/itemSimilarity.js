/**
 * FastText 기반 아이템 유사도 계산 유틸리티
 *
 * cc.ko.300.vec 모델로 사전 계산된 유사도 매트릭스를 사용하여
 * 아이템 이름 간의 의미적 유사도를 계산합니다.
 */

import similarityData from '@/data/itemSimilarity.json'

// 사전 계산된 유사도 매트릭스
const { matrix, synonyms, categories, words } = similarityData

// 단어 집합 (빠른 검색용)
const wordSet = new Set(words)

/**
 * 텍스트에서 키워드 추출
 * @param {string} text - 아이템 이름
 * @returns {string[]} 추출된 키워드 배열
 */
const extractKeywords = (text) => {
  if (!text) return []

  // 공백, 특수문자로 분리
  const parts = text.split(/[\s,_\-/()]+/)
  const keywords = []

  for (const part of parts) {
    const trimmed = part.trim()
    if (trimmed.length >= 2) {
      keywords.push(trimmed)
    }
  }

  // 원본 텍스트도 포함 (복합어 처리)
  if (text.trim() && !keywords.includes(text.trim())) {
    keywords.push(text.trim())
  }

  return keywords
}

/**
 * 두 단어의 유사도 조회
 * @param {string} word1
 * @param {string} word2
 * @returns {number} 0.0 ~ 1.0
 */
const getWordPairSimilarity = (word1, word2) => {
  if (!word1 || !word2) return 0

  // 동일 단어
  if (word1 === word2) return 1.0

  // 포함 관계
  if (word1.includes(word2) || word2.includes(word1)) {
    return 0.85
  }

  // 동의어 체크
  if (synonyms[word1]?.includes(word2) || synonyms[word2]?.includes(word1)) {
    return 0.95
  }

  // 매트릭스에서 조회
  const key1 = `${word1}:${word2}`
  const key2 = `${word2}:${word1}`

  if (matrix[key1]) return matrix[key1]
  if (matrix[key2]) return matrix[key2]

  // 같은 카테고리인지 확인
  for (const [, categoryWords] of Object.entries(categories)) {
    const inCat1 = categoryWords.some(w => word1.includes(w) || w.includes(word1))
    const inCat2 = categoryWords.some(w => word2.includes(w) || w.includes(word2))
    if (inCat1 && inCat2) {
      return 0.5  // 같은 카테고리 기본 유사도
    }
  }

  return 0
}

/**
 * 아이템 이름에서 가장 적합한 키워드 찾기
 * @param {string} itemName - 아이템 이름
 * @returns {string|null} 매칭된 키워드
 */
const findBestKeyword = (itemName) => {
  if (!itemName) return null

  const name = itemName.toLowerCase()

  // 정확히 일치하는 키워드
  for (const word of words) {
    if (name === word) return word
  }

  // 키워드가 포함된 경우
  for (const word of words) {
    if (name.includes(word)) return word
  }

  // 분리된 부분에서 매칭
  const keywords = extractKeywords(itemName)
  for (const kw of keywords) {
    if (wordSet.has(kw)) return kw
    for (const word of words) {
      if (kw.includes(word) || word.includes(kw)) return word
    }
  }

  return null
}

/**
 * 두 아이템 이름의 의미적 유사도 계산
 * @param {string} item1 - 첫 번째 아이템 이름
 * @param {string} item2 - 두 번째 아이템 이름
 * @returns {number} 0.0 ~ 1.0 유사도
 */
export const calculateItemSimilarity = (item1, item2) => {
  if (!item1 || !item2) return 0

  // 동일 이름
  if (item1 === item2) return 1.0

  // 키워드 추출
  const keywords1 = extractKeywords(item1)
  const keywords2 = extractKeywords(item2)

  if (keywords1.length === 0 || keywords2.length === 0) return 0

  let maxSimilarity = 0

  // 모든 키워드 쌍에서 최대 유사도 찾기
  for (const kw1 of keywords1) {
    for (const kw2 of keywords2) {
      const sim = getWordPairSimilarity(kw1, kw2)
      if (sim > maxSimilarity) {
        maxSimilarity = sim
      }
    }
  }

  return maxSimilarity
}

/**
 * 아이템과 행운 아이템 목록 중 최대 유사도 계산
 * @param {string} itemName - 사용자 아이템 이름
 * @param {string[]} luckyItems - 행운 아이템 이름 배열
 * @returns {{ similarity: number, bestMatch: string|null }}
 */
export const getMaxSimilarityWithLuckyItems = (itemName, luckyItems) => {
  if (!itemName || !luckyItems || luckyItems.length === 0) {
    return { similarity: 0, bestMatch: null }
  }

  let maxSimilarity = 0
  let bestMatch = null

  for (const luckyItem of luckyItems) {
    if (!luckyItem) continue

    const similarity = calculateItemSimilarity(itemName, luckyItem)
    if (similarity > maxSimilarity) {
      maxSimilarity = similarity
      bestMatch = luckyItem
    }
  }

  return { similarity: maxSimilarity, bestMatch }
}

/**
 * 유사도를 0-100 점수로 변환
 * @param {number} similarity - 0.0 ~ 1.0 유사도
 * @returns {number} 0 ~ 100 점수
 */
export const similarityToScore = (similarity) => {
  // 유사도 구간별 점수 매핑
  // 0.9+ : 90-100점 (거의 동일)
  // 0.7-0.9 : 70-90점 (매우 유사)
  // 0.5-0.7 : 50-70점 (같은 카테고리)
  // 0.3-0.5 : 30-50점 (약간 관련)
  // 0.3 미만 : 0-30점 (관련 없음)

  if (similarity >= 0.9) {
    return Math.round(90 + (similarity - 0.9) * 100)
  } else if (similarity >= 0.7) {
    return Math.round(70 + (similarity - 0.7) * 100)
  } else if (similarity >= 0.5) {
    return Math.round(50 + (similarity - 0.5) * 100)
  } else if (similarity >= 0.3) {
    return Math.round(30 + (similarity - 0.3) * 100)
  } else {
    return Math.round(similarity * 100)
  }
}

export default {
  calculateItemSimilarity,
  getMaxSimilarityWithLuckyItems,
  similarityToScore,
  findBestKeyword
}