/**
 * Fortune 데이터 로딩 유틸리티
 * - daily/weekly/monthly 캐시 처리 통합
 * - API 호출 로직 추상화
 */

import apiClient from '@/config/api'

// 기간별 API 엔드포인트
const ENDPOINTS = {
  daily: '/api/fortune/today/',
  weekly: '/api/fortune/weekly/',
  monthly: '/api/fortune/monthly/'
}

/**
 * 현재 날짜/주차/월 정보 계산
 */
export const getDateInfo = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1
  const today = `${year}-${String(month).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

  // ISO 주차 계산
  const startOfYear = new Date(year, 0, 1)
  const days = Math.floor((now - startOfYear) / (24 * 60 * 60 * 1000))
  const week = Math.ceil((days + startOfYear.getDay() + 1) / 7)

  return { year, month, week, today }
}

/**
 * Store에서 캐시된 운세 가져오기
 * @param {string} period - 'daily' | 'weekly' | 'monthly'
 * @param {Object} fortuneStore - Pinia fortuneStore 인스턴스
 * @returns {Object|null} 캐시된 운세 데이터 또는 null
 */
export const getCachedFortune = (period, fortuneStore) => {
  const { year, month, week, today } = getDateInfo()

  if (period === 'daily') {
    if (fortuneStore.fortuneData && fortuneStore.fortuneDate === today) {
      console.log('[Fortune] Store에서 daily 운세 로드')
      return fortuneStore.fortuneData
    }
  } else if (period === 'weekly') {
    const cached = fortuneStore.getWeeklyFortune(year, week)
    if (cached) {
      console.log('[Fortune] Store에서 weekly 운세 로드')
      return cached
    }
  } else if (period === 'monthly') {
    const cached = fortuneStore.getMonthlyFortune(year, month)
    if (cached) {
      console.log('[Fortune] Store에서 monthly 운세 로드')
      return cached
    }
  }

  return null
}

/**
 * Store에 운세 캐시 저장
 * @param {string} period - 'daily' | 'weekly' | 'monthly'
 * @param {Object} fortuneStore - Pinia fortuneStore 인스턴스
 * @param {Object} fortune - 운세 데이터
 * @param {Object} responseData - API 응답 전체 (year, week, month 포함)
 */
export const cacheFortune = (period, fortuneStore, fortune, responseData = {}) => {
  const { today } = getDateInfo()

  if (period === 'daily') {
    fortuneStore.setFortune(fortune, today)
  } else if (period === 'weekly' && responseData.year && responseData.week) {
    fortuneStore.setWeeklyFortune(fortune, responseData.year, responseData.week)
  } else if (period === 'monthly' && responseData.year && responseData.month) {
    fortuneStore.setMonthlyFortune(fortune, responseData.year, responseData.month)
  }
}

/**
 * API에서 운세 로드 (GET)
 * @param {string} period - 'daily' | 'weekly' | 'monthly'
 * @returns {Promise<Object>} API 응답
 */
export const fetchFortune = async (period) => {
  const endpoint = ENDPOINTS[period]
  console.log(`[Fortune] ${period} 운세 로드 시작, endpoint: ${endpoint}`)

  const response = await apiClient.get(endpoint)
  console.log(`[Fortune] GET 응답:`, response.data)

  return response.data
}

/**
 * API에서 운세 생성 (POST - 로그인 사용자용)
 * @param {string} period - 'daily' | 'weekly' | 'monthly'
 * @returns {Promise<Object>} API 응답
 */
export const generateFortune = async (period) => {
  const endpoint = ENDPOINTS[period]
  console.log(`[Fortune] ${period} 운세 생성 요청`)

  const response = await apiClient.post(endpoint)
  return response.data
}

/**
 * API에서 운세 생성 (POST - 비로그인 사용자용)
 * @param {string} period - 'daily' | 'weekly' | 'monthly'
 * @param {Object} formData - 생년월일, 성별 등
 * @returns {Promise<Object>} API 응답
 */
export const generateFortuneWithForm = async (period, formData) => {
  const endpoint = ENDPOINTS[period]
  console.log(`[Fortune] ${period} 운세 생성 요청 (비로그인)`)

  const response = await apiClient.post(endpoint, formData)
  return response.data
}

/**
 * 오늘 날짜 기준 주간/월간 구간 인덱스 계산
 * @returns {{weeklyIndex: number, monthlyIndex: number}}
 */
export const getTodayPeriodIndex = () => {
  const now = new Date()
  const dayOfWeek = now.getDay() // 0=일, 1=월, 2=화, 3=수, 4=목, 5=금, 6=토
  const dayOfMonth = now.getDate()

  // 주간: 평일 초(월~화)=1, 평일 말(수~금)=2, 주말(토~일)=3
  let weeklyIndex = 0
  if (dayOfWeek === 1 || dayOfWeek === 2) {
    weeklyIndex = 1 // 평일 초 (월~화)
  } else if (dayOfWeek >= 3 && dayOfWeek <= 5) {
    weeklyIndex = 2 // 평일 말 (수~금)
  } else {
    weeklyIndex = 3 // 주말 (토~일)
  }

  // 월간: 월초(1~10)=1, 월중(11~20)=2, 월말(21~)=3
  let monthlyIndex = 0
  if (dayOfMonth <= 10) {
    monthlyIndex = 1 // 월초
  } else if (dayOfMonth <= 20) {
    monthlyIndex = 2 // 월중
  } else {
    monthlyIndex = 3 // 월말
  }

  return { weeklyIndex, monthlyIndex }
}

/**
 * 운세 텍스트 문장 단위로 리스트 형태로 변환
 * @param {string} text - 운세 텍스트
 * @param {string} colorClass - 색상 클래스
 * @param {string} period - 'daily' | 'weekly' | 'monthly'
 * @returns {string} HTML 문자열
 */
export const formatFortuneText = (text, colorClass = '', period = 'daily') => {
  if (!text) return ''

  const sentences = text.split(/(?<=[.!?])\s+/).filter(s => s.trim())
  if (sentences.length <= 1) return text

  const { weeklyIndex, monthlyIndex } = getTodayPeriodIndex()

  const listItems = sentences.map((s, index) => {
    let isBold = false

    if (period === 'weekly' && index === weeklyIndex) {
      isBold = true
    }
    if (period === 'monthly' && index === monthlyIndex) {
      isBold = true
    }

    if (isBold) {
      return `<li class="today-highlight"><strong>${s.trim()}</strong></li>`
    }
    return `<li>${s.trim()}</li>`
  }).join('')

  return `<ul class="fortune-list ${colorClass}">${listItems}</ul>`
}

/**
 * 아이템 설명 포맷팅 (아이템명 굵게/밑줄)
 * @param {string} text - 설명 텍스트
 * @param {string} itemName - 아이템명
 * @returns {string} HTML 문자열
 */
export const formatDescription = (text, itemName) => {
  if (!text) return ''
  let result = text

  if (itemName) {
    const escapedName = itemName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    result = result.replace(new RegExp(escapedName, 'g'), `<strong style="text-decoration: underline;">${itemName}</strong>`)
  }

  return result.replace(/([.!?])(\s+)/g, '$1<br>')
}
