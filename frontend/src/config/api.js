import axios from 'axios'

// API Base URL 설정
// 개발: 빈 문자열 (Vite proxy 사용)
// 배포: CloudFront HTTPS URL 사용
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? 'https://d1rjzb95p17prq.cloudfront.net' : '')

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // JWT 토큰 사용 시 쿠키 불필요
})

// 토큰 갱신 중복 방지 플래그
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// 요청 인터셉터 - 토큰 자동 추가
apiClient.interceptors.request.use(
  (config) => {
    // 세션 인증 사용 (Django)
    // JWT 사용 시 여기서 토큰 추가
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // CSRF 토큰 (세션 인증 사용 시)
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터 - 에러 처리 및 토큰 자동 갱신
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response) {
      // 401 Unauthorized - 토큰 갱신 시도
      if (error.response.status === 401 && !originalRequest._retry) {
        // 로그인/갱신 요청에서는 갱신 시도하지 않음
        const isAuthRequest = originalRequest.url?.includes('/api/auth/login') ||
                              originalRequest.url?.includes('/api/auth/refresh')
        if (isAuthRequest) {
          return Promise.reject(error)
        }

        // 이미 갱신 중이면 큐에 추가
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject })
          }).then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return apiClient(originalRequest)
          }).catch(err => {
            return Promise.reject(err)
          })
        }

        originalRequest._retry = true
        isRefreshing = true

        const refreshToken = localStorage.getItem('refresh_token')

        if (!refreshToken) {
          // refresh token이 없으면 로그아웃
          isRefreshing = false
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          return Promise.reject(error)
        }

        try {
          // 토큰 갱신 요청
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh/`, {
            refresh: refreshToken
          })

          const newAccessToken = response.data.access
          localStorage.setItem('access_token', newAccessToken)

          // 대기 중인 요청들 처리
          processQueue(null, newAccessToken)

          // 원래 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          // 갱신 실패 - 로그아웃
          processQueue(refreshError, null)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      // 403 Forbidden
      if (error.response.status === 403) {
        console.error('접근 권한이 없습니다')
      }

      // 500 Server Error
      if (error.response.status >= 500) {
        console.error('서버 오류가 발생했습니다')
      }
    }

    return Promise.reject(error)
  }
)

// CSRF 토큰 가져오기
function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export default apiClient
export { API_BASE_URL }
