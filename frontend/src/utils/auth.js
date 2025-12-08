// 인증 관련 유틸리티 함수

export const isAuthenticated = () => {
  // 세션 기반 인증 체크
  return document.cookie.includes('sessionid')
}

export const getUser = () => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

export const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user))
}

export const clearAuth = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export const login = async (username, password) => {
  // 로그인 로직은 auth store에서 처리
}

export const logout = async () => {
  // 로그아웃 로직은 auth store에서 처리
}
