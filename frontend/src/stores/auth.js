import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/config/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)
  const mustChangePassword = ref(false)

  // Getters
  const userId = computed(() => user.value?.id)
  const username = computed(() => user.value?.username)
  const userEmail = computed(() => user.value?.email)

  // Actions
  async function login(username, password) {
    loading.value = true
    try {
      const response = await apiClient.post('/api/auth/login/', {
        username,
        password
      })

      // JWT 토큰 저장
      if (response.data.access && response.data.refresh) {
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)

        // 사용자 정보 저장
        user.value = response.data.user
        isAuthenticated.value = true
        localStorage.setItem('user', JSON.stringify(response.data.user))

        // 임시 비밀번호 변경 필요 여부 저장
        mustChangePassword.value = response.data.must_change_password || false
        localStorage.setItem('must_change_password', mustChangePassword.value)

        return { mustChangePassword: mustChangePassword.value }
      } else {
        throw new Error('로그인에 실패했습니다')
      }
    } catch (error) {
      console.error('로그인 실패:', error)
      throw new Error(error.response?.data?.detail || error.message || '로그인에 실패했습니다')
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    loading.value = true
    try {
      const response = await apiClient.post('/api/auth/register/', userData)

      if (response.data.success) {
        return
      } else {
        throw new Error(response.data.error || '회원가입에 실패했습니다')
      }
    } catch (error) {
      console.error('회원가입 실패:', error)
      console.error('에러 응답:', error.response?.data)

      // 상세 에러 메시지 생성
      let errorMessage = '회원가입에 실패했습니다'
      if (error.response?.data?.errors) {
        const errors = error.response.data.errors
        const errorMessages = Object.entries(errors).map(([field, msgs]) => {
          const fieldName = {
            'username': '아이디',
            'email': '이메일',
            'password': '비밀번호',
            'password2': '비밀번호 확인',
            'first_name': '이름',
            'last_name': '성',
            'birth_date': '생년월일',
            'gender': '성별'
          }[field] || field
          return `${fieldName}: ${Array.isArray(msgs) ? msgs[0] : msgs}`
        })
        errorMessage = errorMessages.join('\n')
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      }

      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      await apiClient.post('/api/auth/logout/', { refresh: refreshToken })

      // 로컬 스토리지 정리
      user.value = null
      isAuthenticated.value = false
      mustChangePassword.value = false
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('must_change_password')
      return { success: true }
    } catch (error) {
      console.error('로그아웃 실패:', error)
      // 로그아웃은 실패해도 로컬 상태 초기화
      user.value = null
      isAuthenticated.value = false
      mustChangePassword.value = false
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('must_change_password')
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  async function checkAuth() {
    try {
      const response = await apiClient.get('/api/auth/me/')
      if (response.data.success) {
        user.value = response.data.user
        isAuthenticated.value = true
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }
    } catch (error) {
      user.value = null
      isAuthenticated.value = false
      localStorage.removeItem('user')
    }
  }

  // fetchUser: 서버에서 최신 사용자 정보 가져오기
  async function fetchUser() {
    try {
      const response = await apiClient.get('/api/auth/me/')
      if (response.data.success) {
        user.value = response.data.user
        localStorage.setItem('user', JSON.stringify(response.data.user))
        return response.data.user
      }
    } catch (error) {
      console.error('사용자 정보 가져오기 실패:', error)
    }
    return null
  }

  async function updateProfile(profileData) {
    loading.value = true
    try {
      const response = await apiClient.put('/api/auth/me/', profileData)
      if (response.data.success) {
        user.value = response.data.user
        localStorage.setItem('user', JSON.stringify(response.data.user))
        return { success: true }
      }
      return { success: false, error: '업데이트 실패' }
    } catch (error) {
      console.error('프로필 업데이트 실패:', error)
      return { success: false, error: error.response?.data?.errors || error.message }
    } finally {
      loading.value = false
    }
  }

  // 초기화: 로컬 스토리지에서 사용자 정보 복원
  function init() {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
      isAuthenticated.value = true
      mustChangePassword.value = localStorage.getItem('must_change_password') === 'true'
      // 서버와 동기화
      checkAuth()
    }
  }

  return {
    user,
    isAuthenticated,
    loading,
    mustChangePassword,
    userId,
    username,
    userEmail,
    login,
    register,
    logout,
    checkAuth,
    fetchUser,
    updateProfile,
    init
  }
})
