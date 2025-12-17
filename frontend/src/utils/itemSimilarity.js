/**
 * 하이브리드 아이템 유사도 계산 유틸리티
 *
 * 1. FastText: cc.ko.300.vec 모델로 사전 계산된 유사도 매트릭스 (오프라인, 즉시)
 * 2. GMS Embedding: text-embedding-3-small API (온라인, 비동기)
 *
 * 두 방식 중 높은 점수를 반환하여 더 관대한 유사도 계산 제공
 */

import similarityData from '@/data/itemSimilarity.json'
import api from '@/services/api'

// 사전 계산된 유사도 매트릭스 (FastText)
const { matrix, synonyms, categories, words } = similarityData

// 단어 집합 (빠른 검색용)
const wordSet = new Set(words)

// ============================================
// FastText 기반 유사도 계산 (동기, 오프라인)
// ============================================

/**
 * 텍스트에서 키워드 추출
 */
const extractKeywords = (text) => {
  if (!text) return []

  const parts = text.split(/[\s,_\-/()]+/)
  const keywords = []

  for (const part of parts) {
    const trimmed = part.trim()
    if (trimmed.length >= 2) {
      keywords.push(trimmed)
    }
  }

  if (text.trim() && !keywords.includes(text.trim())) {
    keywords.push(text.trim())
  }

  return keywords
}

/**
 * 두 단어의 FastText 유사도 조회
 */
const getWordPairSimilarity = (word1, word2) => {
  if (!word1 || !word2) return 0
  if (word1 === word2) return 1.0
  if (word1.includes(word2) || word2.includes(word1)) return 0.85
  if (synonyms[word1]?.includes(word2) || synonyms[word2]?.includes(word1)) return 0.95

  const key1 = `${word1}:${word2}`
  const key2 = `${word2}:${word1}`
  if (matrix[key1]) return matrix[key1]
  if (matrix[key2]) return matrix[key2]

  for (const [, categoryWords] of Object.entries(categories)) {
    const inCat1 = categoryWords.some(w => word1.includes(w) || w.includes(word1))
    const inCat2 = categoryWords.some(w => word2.includes(w) || w.includes(word2))
    if (inCat1 && inCat2) return 0.5
  }

  return 0
}

/**
 * 아이템 이름에서 가장 적합한 키워드 찾기
 */
export const findBestKeyword = (itemName) => {
  if (!itemName) return null

  const name = itemName.toLowerCase()

  for (const word of words) {
    if (name === word) return word
  }
  for (const word of words) {
    if (name.includes(word)) return word
  }

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
 * FastText 기반 두 아이템 유사도 계산 (동기)
 */
export const calculateItemSimilarity = (item1, item2) => {
  if (!item1 || !item2) return 0
  if (item1 === item2) return 1.0

  const keywords1 = extractKeywords(item1)
  const keywords2 = extractKeywords(item2)

  if (keywords1.length === 0 || keywords2.length === 0) return 0

  let maxSimilarity = 0
  for (const kw1 of keywords1) {
    for (const kw2 of keywords2) {
      const sim = getWordPairSimilarity(kw1, kw2)
      if (sim > maxSimilarity) maxSimilarity = sim
    }
  }

  return maxSimilarity
}

/**
 * FastText 기반 최대 유사도 계산 (동기)
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

// ============================================
// GMS Embedding API 기반 유사도 계산 (비동기)
// ============================================

/**
 * GMS Embedding API로 유사도 계산
 * @param {string} itemName - 사용자 아이템 이름
 * @param {string[]} luckyItems - 행운 아이템 목록
 * @returns {Promise<{similarity: number, bestMatch: string|null}>}
 */
export const getEmbeddingSimilarity = async (itemName, luckyItems) => {
  if (!itemName || !luckyItems || luckyItems.length === 0) {
    return { similarity: 0, bestMatch: null }
  }

  try {
    const response = await api.post('/api/items/similarity/', {
      item_name: itemName,
      lucky_items: luckyItems
    })

    if (response.data.success) {
      return {
        similarity: response.data.max_similarity,
        bestMatch: response.data.best_match
      }
    }
    return { similarity: 0, bestMatch: null }
  } catch (error) {
    console.warn('[ItemSimilarity] GMS API failed:', error.message)
    return { similarity: 0, bestMatch: null }
  }
}

// ============================================
// 하이브리드 유사도 계산 (두 방식 중 높은 값)
// ============================================

/**
 * 하이브리드 최대 유사도 계산
 * FastText(즉시) + GMS Embedding(비동기) 중 높은 값 반환
 *
 * @param {string} itemName - 사용자 아이템 이름
 * @param {string[]} luckyItems - 행운 아이템 목록
 * @returns {Promise<{similarity: number, bestMatch: string|null, source: string}>}
 */
export const getHybridSimilarity = async (itemName, luckyItems) => {
  if (!itemName || !luckyItems || luckyItems.length === 0) {
    return { similarity: 0, bestMatch: null, source: 'none' }
  }

  // 1. FastText 결과 (즉시)
  const fastTextResult = getMaxSimilarityWithLuckyItems(itemName, luckyItems)

  // 2. GMS Embedding 결과 (비동기)
  const embeddingResult = await getEmbeddingSimilarity(itemName, luckyItems)

  // 3. 더 높은 유사도 선택
  if (embeddingResult.similarity > fastTextResult.similarity) {
    return {
      similarity: embeddingResult.similarity,
      bestMatch: embeddingResult.bestMatch,
      source: 'embedding'
    }
  }

  return {
    similarity: fastTextResult.similarity,
    bestMatch: fastTextResult.bestMatch,
    source: 'fasttext'
  }
}

// ============================================
// 유틸리티 함수
// ============================================

/**
 * 유사도를 0-100 점수로 변환
 */
export const similarityToScore = (similarity) => {
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
  // FastText (동기)
  calculateItemSimilarity,
  getMaxSimilarityWithLuckyItems,
  findBestKeyword,
  // GMS Embedding (비동기)
  getEmbeddingSimilarity,
  // 하이브리드 (비동기)
  getHybridSimilarity,
  // 유틸리티
  similarityToScore
}
