import axios from 'axios'

// API Base URL 설정
// 개발: 빈 문자열 (Vite proxy 사용)
// 배포: CloudFront HTTPS URL 사용
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? 'https://d1rjzb95p17prq.cloudfront.net' : '')

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // JWT 토큰 사용 시 쿠키 불필요
})

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

// 응답 인터셉터 - 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // 401 Unauthorized - 로그인 필요
      // 단, 로그인 API 요청에서는 리다이렉트하지 않음 (에러 메시지 표시 필요)
      if (error.response.status === 401) {
        const isLoginRequest = error.config.url?.includes('/api/auth/login')
        if (!isLoginRequest) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
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
