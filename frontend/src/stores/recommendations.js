import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/config/api'

export const useRecommendationsStore = defineStore('recommendations', () => {
  // State
  const ootdData = ref(null)
  const menuData = ref(null)
  const weatherData = ref(null)
  const loading = ref(false)

  // Actions
  async function getOOTD(lat, lon) {
    loading.value = true
    try {
      const params = {}
      if (lat && lon) {
        params.lat = lat
        params.lon = lon
      }
      const response = await apiClient.get('/api/recommendations/ootd/', { params })
      if (response.data.success) {
        ootdData.value = response.data
        return { success: true, data: response.data }
      }
    } catch (error) {
      console.error('OOTD 추천 실패:', error)
      return { success: false, error: error.response?.data?.error }
    } finally {
      loading.value = false
    }
  }

  async function getMenuRecommendation() {
    loading.value = true
    try {
      const response = await apiClient.get('/api/recommendations/menu/')
      if (response.data.success) {
        menuData.value = response.data
        return { success: true, data: response.data }
      }
    } catch (error) {
      console.error('메뉴 추천 실패:', error)
      return { success: false, error: error.response?.data?.error }
    } finally {
      loading.value = false
    }
  }

  async function getWeather(lat, lon) {
    loading.value = true
    try {
      const response = await apiClient.post('/api/recommendations/weather/location/', {
        lat,
        lon
      })
      if (response.data.success) {
        weatherData.value = response.data
        return { success: true, data: response.data }
      }
    } catch (error) {
      console.error('날씨 정보 가져오기 실패:', error)
      return { success: false, error: error.response?.data?.error }
    } finally {
      loading.value = false
    }
  }

  // 로그아웃 시 모든 데이터 초기화
  function clearAll() {
    ootdData.value = null
    menuData.value = null
    weatherData.value = null
    console.log('[Recommendations Store] 모든 데이터 초기화')
  }

  return {
    ootdData,
    menuData,
    weatherData,
    loading,
    getOOTD,
    getMenuRecommendation,
    getWeather,
    clearAll
  }
})
