<template>
  <div class="loading-container">
    <div class="loading-circle"></div>
    <h2 class="loading-title">운세 생성 중...</h2>
    <p class="loading-subtitle" id="loadingText">{{ currentText }}</p>
    <p v-if="errorMessage" class="loading-error show">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFortuneStore } from '@/stores/fortune'
import apiClient from '@/config/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const fortuneStore = useFortuneStore()

const loadingTexts = [
  '우주의 기운을 모으고 있습니다',
  '별자리를 분석하고 있습니다',
  '사주팔자를 계산하고 있습니다',
  '행운의 색상을 찾고 있습니다',
  '오늘의 운세를 정리하고 있습니다'
]

const currentText = ref(loadingTexts[0])
const errorMessage = ref('')
let textIndex = 0
let textInterval = null

onMounted(() => {
  // 로딩 텍스트 변경 애니메이션
  textInterval = setInterval(() => {
    textIndex = (textIndex + 1) % loadingTexts.length
    currentText.value = loadingTexts[textIndex]
  }, 2000)

  // 운세 계산 API 호출
  calculateFortune()
})

onUnmounted(() => {
  if (textInterval) clearInterval(textInterval)
})

async function calculateFortune() {
  // 로그인 사용자는 /api/fortune/generate/ 호출
  // 비로그인 사용자는 /api/fortune/calculate/ 호출

  try {
    let response

    if (authStore.isAuthenticated) {
      // 로그인 사용자: generate API (사용자 정보 자동 사용)
      console.log('[FortuneLoading] 로그인 사용자 - generate API 호출')
      response = await apiClient.post('/api/fortune/generate/')
    } else {
      // 비로그인 사용자: query 파라미터에서 받은 폼 데이터 사용
      const birthDate = route.query.birth_date
      const gender = route.query.gender
      const mbti = route.query.mbti
      const calendarType = route.query.calendar_type
      const birthTime = route.query.birth_time
      const chineseName = route.query.chinese_name

      // 필수 값 검증
      if (!birthDate || !gender) {
        console.error('[FortuneLoading] 필수 값 누락:', { birthDate, gender })
        showError('생년월일과 성별은 필수 입력 항목입니다.')
        return
      }

      // 생년월일 형식 변환
      let formattedDate = birthDate
      if (birthDate) {
        // YYYYMMDD 형식인 경우 YYYY-MM-DD로 변환
        if (birthDate.length === 8 && !birthDate.includes('-')) {
          formattedDate = birthDate.slice(0, 4) + '-' + birthDate.slice(4, 6) + '-' + birthDate.slice(6, 8)
        }
      }

      // 요청 데이터 구성
      const requestData = {
        birth_date: formattedDate,
        gender: gender,
        calendar_type: calendarType || 'solar'
      }

      // 선택 항목들은 값이 있는 경우에만 추가
      if (mbti && mbti.trim()) {
        requestData.mbti = mbti.trim()
      }
      if (birthTime && birthTime.trim()) {
        requestData.birth_time = birthTime.trim()
      }
      if (chineseName && chineseName.trim()) {
        requestData.chinese_name = chineseName.trim()
      }

      console.log('[FortuneLoading] 비로그인 사용자 - calculate API 호출:', requestData)
      response = await apiClient.post('/api/fortune/calculate/', requestData)
    }

    const data = response.data
    console.log('[FortuneLoading] Response:', data)

    if (data.success && data.fortune) {
      // Fortune Store에 저장 (Django 세션과 동기화)
      const today = new Date().toISOString().split('T')[0]
      fortuneStore.fortuneData = data.fortune
      fortuneStore.fortuneDate = today

      console.log('[FortuneLoading] Fortune Store에 저장 완료:', today)

      // 계산 완료 - 원래 가려던 페이지 또는 결과 페이지로 이동
      if (textInterval) clearInterval(textInterval)
      currentText.value = '완료! 결과 페이지로 이동합니다...'

      // redirect 쿼리가 있으면 해당 페이지로, 없으면 fortune/today로
      const redirectPath = route.query.redirect || '/fortune/today'
      setTimeout(() => {
        router.replace(redirectPath)
      }, 500)
    } else {
      // 에러 발생
      let errorMsg = data.error || '운세 계산 중 오류가 발생했습니다.'
      if (data.details) {
        console.error('Validation errors:', data.details)
      }
      showError(errorMsg)
    }
  } catch (error) {
    console.error('Fortune calculation error:', error)
    showError(error.response?.data?.error || '서버와 통신 중 오류가 발생했습니다.')
  }
}

function showError(message) {
  if (textInterval) clearInterval(textInterval)
  errorMessage.value = message

  // 3초 후 입력 페이지로 리다이렉트 (replace로 히스토리 대체)
  setTimeout(() => {
    router.replace('/fortune/calculate')
  }, 3000)
}
</script>

<style scoped>
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-darker);
  z-index: 9999;
}

.loading-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 5px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--primary);
  animation: spin 1s linear infinite;
  margin-bottom: 30px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin-bottom: 10px;
  letter-spacing: -0.5px;
}

.loading-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
  transition: opacity 0.3s;
}

.loading-error {
  color: #ff6b6b;
  margin-top: 20px;
  display: none;
}

.loading-error.show {
  display: block;
}
</style>
