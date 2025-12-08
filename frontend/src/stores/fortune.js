import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/config/api'

export const useFortuneStore = defineStore('fortune', () => {
  // State - DB 캐시 기반 (Django와 완전히 동일한 데이터 소스)
  const fortuneData = ref(null)
  const fortuneDate = ref(null)
  const loading = ref(false)

  // Getters
  const hasTodayFortune = computed(() => {
    const today = new Date().toISOString().split('T')[0]
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
    const today = new Date().toISOString().split('T')[0]

    // 항상 API 호출 (DB 캐시에서 가져옴, Django와 동일한 소스)
    console.log('[Fortune Store] DB 캐시에서 운세 확인')
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
        fortuneDate.value = new Date().toISOString().split('T')[0]
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

  return {
    // State
    fortuneData,
    fortuneDate,
    loading,

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
    clearFortune
  }
})
