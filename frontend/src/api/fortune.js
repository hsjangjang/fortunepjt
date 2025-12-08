import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// CSRF 토큰 가져오기
function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// 요청 인터셉터 - CSRF 토큰 추가
apiClient.interceptors.request.use(
  config => {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

export const fortuneAPI = {
  // 운세 계산
  calculate(data) {
    return apiClient.post('/fortune/api/calculate/', data)
  },

  // 오늘의 운세 조회
  getToday() {
    return apiClient.get('/fortune/api/today/')
  },

  // 운세 초기화
  reset() {
    return apiClient.post('/fortune/api/reset/')
  },

  // 아이템 체크
  getItemCheck() {
    return apiClient.get('/fortune/api/item-check/')
  }
}

export default apiClient
