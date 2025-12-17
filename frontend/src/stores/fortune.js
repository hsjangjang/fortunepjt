import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/config/api'

export const useFortuneStore = defineStore('fortune', () => {
  // State - DB 캐시 기반 (Django와 완전히 동일한 데이터 소스)
  const fortuneData = ref(null)
  const fortuneDate = ref(null)
  const loading = ref(false)
  // 비로그인 사용자의 폼 데이터 (weekly/monthly 생성시 필요)
  const formData = ref(null)

  // 주간/월간 운세 캐시
  const weeklyFortuneData = ref(null)
  const weeklyFortuneKey = ref(null)  // "year_week" 형식 (예: "2025_51")
  const monthlyFortuneData = ref(null)
  const monthlyFortuneKey = ref(null)  // "year_month" 형식 (예: "2025_12")

  // 로컬 시간 기준 오늘 날짜 (YYYY-MM-DD)
  const getLocalToday = () => {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  // Getters
  const hasTodayFortune = computed(() => {
    const today = getLocalToday()
    return fortuneData.value !== null && fortuneDate.value === today
  })

  const fortuneScores = computed(() => {
    return fortuneData.value?.fortune_scores || {}
  })

  const fortuneTexts = computed(() => {
    return fortuneData.value?.fortune_texts || {}
  })

  const luckyColors = computed(() => {
    return fortuneData.value?.lucky_colors || []
  })

  const luckyItem = computed(() => {
    return fortuneData.value?.lucky_item || {}
  })

  // Actions

  /**
   * 오늘의 운세 확인 (DB 캐시에서 가져오기)
   * Django와 Vue가 동일한 DB 캐시를 공유하므로 완전히 동일한 운세 반환
   */
  async function checkTodayFortune() {
    const today = getLocalToday()

    // 항상 API 호출 (DB 캐시에서 가져옴, Django와 동일한 소스)
    console.log('[Fortune Store] DB 캐시에서 운세 확인, 오늘:', today)
    try {
      const response = await apiClient.get('/api/fortune/today/')

      if (response.data.success && response.data.fortune) {
        const fortuneDateFromAPI = response.data.date || today

        // Django API에서 받은 날짜가 오늘과 다르면 운세 없음으로 처리
        if (fortuneDateFromAPI !== today) {
          console.log('[Fortune Store] API 응답 날짜와 오늘 날짜 불일치:', fortuneDateFromAPI, '!=', today)
          fortuneData.value = null
          fortuneDate.value = null
          return false
        }

        fortuneData.value = response.data.fortune
        fortuneDate.value = fortuneDateFromAPI
        console.log('[Fortune Store] DB 캐시에서 운세 로드 완료:', fortuneDateFromAPI)
        return true
      } else {
        // 운세 없음
        fortuneData.value = null
        fortuneDate.value = null
        return false
      }
    } catch (error) {
      console.error('운세 확인 실패:', error)
      fortuneData.value = null
      fortuneDate.value = null
      return false
    }
  }

  /**
   * 운세 계산 (API 호출)
   * DB 캐시에 저장되므로 Django와 Vue가 동일한 운세 공유
   */
  async function calculateFortune(formData) {
    loading.value = true
    try {
      // 빈 값 제거 (선택적 필드)
      const cleanedData = {}
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '' && formData[key] !== null && formData[key] !== undefined) {
          cleanedData[key] = formData[key]
        }
      })

      console.log('[Fortune Store] API 호출 시작 (원본):', formData)
      console.log('[Fortune Store] API 호출 시작 (정제):', cleanedData)
      const response = await apiClient.post('/api/fortune/calculate/', cleanedData)
      console.log('[Fortune Store] API 응답:', response.data)

      if (response.data.success && response.data.fortune) {
        fortuneData.value = response.data.fortune
        fortuneDate.value = getLocalToday()
        console.log('[Fortune Store] 운세 계산 완료 및 DB 캐시에 저장')
        return { success: true, fortune: response.data.fortune }
      } else {
        const errorMsg = response.data.error || '운세 계산에 실패했습니다'
        console.error('[Fortune Store] API 응답 오류:', errorMsg)
        throw new Error(errorMsg)
      }
    } catch (error) {
      console.error('[Fortune Store] 운세 계산 실패:', error)
      console.error('[Fortune Store] 에러 응답:', error.response?.data)

      // 에러 객체를 그대로 던져서 response.data에 접근 가능하도록
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 운세 초기화 (강제 새로고침)
   * DB 캐시와 세션 모두 삭제
   */
  async function resetFortune() {
    try {
      const response = await apiClient.post('/api/fortune/reset/')

      if (response.data.success) {
        fortuneData.value = null
        fortuneDate.value = null
        console.log('[Fortune Store] 운세 초기화 완료')
        return true
      }
      return false
    } catch (error) {
      console.error('운세 초기화 실패:', error)
      return false
    }
  }

  /**
   * 로컬 상태 초기화 (로그인/로그아웃 시)
   */
  function clearFortune() {
    fortuneData.value = null
    fortuneDate.value = null
    console.log('[Fortune Store] 로컬 상태 초기화')
  }

  /**
   * 운세 데이터 직접 설정 (Loading.vue에서 사용)
   */
  function setFortune(fortune, date, form = null) {
    fortuneData.value = fortune
    fortuneDate.value = date
    if (form) {
      formData.value = form
    }
    console.log('[Fortune Store] 운세 데이터 설정:', date)
  }

  /**
   * 폼 데이터만 설정 (Loading.vue에서 사용)
   */
  function setFormData(form) {
    formData.value = form
    console.log('[Fortune Store] 폼 데이터 설정:', form)
  }

  /**
   * 주간 운세 설정
   */
  function setWeeklyFortune(fortune, year, week) {
    weeklyFortuneData.value = fortune
    weeklyFortuneKey.value = `${year}_${week}`
    console.log('[Fortune Store] 주간 운세 설정:', weeklyFortuneKey.value)
  }

  /**
   * 주간 운세 가져오기 (캐시 히트 시 반환, 미스 시 null)
   */
  function getWeeklyFortune(year, week) {
    const key = `${year}_${week}`
    if (weeklyFortuneKey.value === key && weeklyFortuneData.value) {
      console.log('[Fortune Store] 주간 운세 캐시 히트:', key)
      return weeklyFortuneData.value
    }
    return null
  }

  /**
   * 월간 운세 설정
   */
  function setMonthlyFortune(fortune, year, month) {
    monthlyFortuneData.value = fortune
    monthlyFortuneKey.value = `${year}_${month}`
    console.log('[Fortune Store] 월간 운세 설정:', monthlyFortuneKey.value)
  }

  /**
   * 월간 운세 가져오기 (캐시 히트 시 반환, 미스 시 null)
   */
  function getMonthlyFortune(year, month) {
    const key = `${year}_${month}`
    if (monthlyFortuneKey.value === key && monthlyFortuneData.value) {
      console.log('[Fortune Store] 월간 운세 캐시 히트:', key)
      return monthlyFortuneData.value
    }
    return null
  }

  return {
    // State
    fortuneData,
    fortuneDate,
    loading,
    formData,
    weeklyFortuneData,
    weeklyFortuneKey,
    monthlyFortuneData,
    monthlyFortuneKey,

    // Getters
    hasTodayFortune,
    fortuneScores,
    fortuneTexts,
    luckyColors,
    luckyItem,

    // Actions
    checkTodayFortune,
    calculateFortune,
    resetFortune,
    clearFortune,
    setFortune,
    setFormData,
    setWeeklyFortune,
    getWeeklyFortune,
    setMonthlyFortune,
    getMonthlyFortune
  }
})
