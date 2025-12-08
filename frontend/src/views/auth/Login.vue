<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-5 col-12 mx-auto px-1 px-md-3">
        <div class="glass-card shadow-lg">
          <div class="card-body responsive-padding">
            <h2 class="text-center mb-4 text-white">
              <i class="fas fa-sign-in-alt text-primary"></i> 로그인
            </h2>

            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label class="form-label text-white">아이디</label>
                <div class="input-group">
                  <span class="input-group-text bg-transparent text-white border-secondary"><i class="fas fa-user"></i></span>
                  <input
                    type="text"
                    v-model="loginForm.username"
                    @input="convertKoreanToEnglish"
                    class="form-control text-white bg-dark border-secondary"
                    required
                    autofocus
                    style="ime-mode: disabled;"
                  >
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label text-white">비밀번호</label>
                <div class="input-group">
                  <span class="input-group-text bg-transparent text-white border-secondary"><i class="fas fa-lock"></i></span>
                  <input
                    type="password"
                    v-model="loginForm.password"
                    class="form-control text-white bg-dark border-secondary"
                    required
                  >
                </div>
              </div>

              <div class="form-check mb-4">
                <input
                  class="form-check-input"
                  type="checkbox"
                  v-model="loginForm.remember_me"
                  id="remember"
                >
                <label class="form-check-label text-white" for="remember">
                  로그인 상태 유지
                </label>
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg">
                  <i class="fas fa-sign-in-alt"></i> 로그인
                </button>
              </div>
            </form>

            <hr class="my-4 border-secondary">

            <div class="text-center">
              <p class="mb-2 text-white">아직 회원이 아니신가요?</p>
              <router-link to="/register" class="btn btn-outline-light">
                회원가입하기
              </router-link>
            </div>

            <div class="text-center mt-3">
              <router-link to="/find-username" class="text-decoration-none text-white-50 small me-3">
                아이디 찾기
              </router-link>
              <router-link to="/find-password" class="text-decoration-none text-white-50 small">
                비밀번호 찾기
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFortuneStore } from '@/stores/fortune'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const router = useRouter()
const authStore = useAuthStore()
const fortuneStore = useFortuneStore()
const { showToast } = useToast()

const loginForm = ref({
  username: '',
  password: '',
  remember_me: false
})

const k2e = {
  'ㅂ':'q','ㅈ':'w','ㄷ':'e','ㄱ':'r','ㅅ':'t',
  'ㅛ':'y','ㅕ':'u','ㅑ':'i','ㅐ':'o','ㅔ':'p',
  'ㅁ':'a','ㄴ':'s','ㅇ':'d','ㄹ':'f','ㅎ':'g',
  'ㅗ':'h','ㅓ':'j','ㅏ':'k','ㅣ':'l',
  'ㅋ':'z','ㅌ':'x','ㅊ':'c','ㅍ':'v','ㅠ':'b','ㅜ':'n','ㅡ':'m',
  'ㅃ':'Q','ㅉ':'W','ㄸ':'E','ㄲ':'R','ㅆ':'T',
  'ㅒ':'O','ㅖ':'P'
}

const convertKoreanToEnglish = (event) => {
  const value = event.target.value

  // 한글이 포함되어 있는지 확인
  if (!/[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/.test(value)) {
    // 한글이 없으면 영문/숫자/이메일 외 문자만 제거
    const cleanValue = value.replace(/[^A-Za-z0-9@._-]/g, '')
    if (value !== cleanValue) {
      loginForm.value.username = cleanValue
    }
    return
  }

  // 한글이 있으면 변환 로직 실행
  requestAnimationFrame(() => {
    let newValue = ''
    for (let i = 0; i < value.length; i++) {
      const char = value[i]
      if (k2e[char]) {
        newValue += k2e[char]
      } else {
        newValue += char
      }
    }

    newValue = newValue.replace(/[^A-Za-z0-9@._-]/g, '')

    if (loginForm.value.username !== newValue) {
      loginForm.value.username = newValue
    }
  })
}

const handleLogin = async () => {
  try {
    console.log('[Login] 로그인 시도')
    const result = await authStore.login(loginForm.value.username, loginForm.value.password)
    console.log('[Login] 로그인 성공')

    // 임시 비밀번호로 로그인한 경우 비밀번호 변경 페이지로 이동
    if (result?.mustChangePassword) {
      showToast('임시 비밀번호로 로그인되었습니다. 비밀번호를 변경해주세요.', 'warning')
      router.push({ name: 'change-password', query: { must_change: 'true' } })
      return
    }

    // Django 세션의 운세 데이터와 동기화
    // Django: 로그인 후 request.session.get('fortune_data_v2') 확인과 동일
    // 운세 확인은 실패해도 로그인 성공 토스트는 표시해야 함
    try {
      console.log('[Login] 운세 데이터 확인 중...')
      const hasFortune = await fortuneStore.checkTodayFortune()
      console.log('[Login] 운세 확인 결과:', hasFortune)
      console.log('[Login] fortuneData:', fortuneStore.fortuneData)
      console.log('[Login] fortuneDate:', fortuneStore.fortuneDate)
    } catch (fortuneError) {
      console.error('[Login] 운세 확인 실패 (무시):', fortuneError)
    }

    // Django: messages.success(request, f'{user.first_name}님, 환영합니다!')
    const firstName = authStore.user?.first_name || authStore.username
    showToast(`${firstName}님, 환영합니다!`, 'success')
    router.push('/')
  } catch (error) {
    console.error('[Login] 로그인 실패:', error)
    // Django: messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    showToast('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
  }
}
</script>

<style scoped>
/* Responsive Padding */
.responsive-padding {
  padding: 3rem !important; /* Desktop default (p-5 equivalent) */
}

@media (max-width: 768px) {
  .responsive-padding {
    padding: 3% !important; /* Minimal padding */
  }
}
</style>
