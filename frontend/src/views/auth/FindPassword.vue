<template>
  <DefaultLayout>
    <div class="row">

      <div class="col-lg-5 col-12 mx-auto px-1 px-md-3">
        <div class="glass-card shadow-lg">
          <div class="card-body responsive-padding">
            <h2 class="text-center mb-4 text-white">
              <i class="fas fa-key text-primary"></i> 비밀번호 찾기
            </h2>

            <!-- 최종 완료 -->
            <div v-if="step === 3" class="text-center mb-4">
              <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                <p class="mb-2">{{ message }}</p>
                <p class="small mb-0">임시 비밀번호로 로그인 후 비밀번호를 변경해주세요.</p>
              </div>
              <div class="d-grid gap-2 mt-4">
                <router-link to="/login" class="btn btn-primary btn-lg">
                  <i class="fas fa-sign-in-alt"></i> 로그인하기
                </router-link>
              </div>
            </div>

            <!-- Step 1: 아이디/이메일 입력 -->
            <form v-else-if="step === 1" @submit.prevent="sendVerificationCode">
              <div class="mb-3">
                <label class="form-label text-white">아이디</label>
                <div class="input-group">
                  <span class="input-group-text bg-transparent text-white border-secondary">
                    <i class="fas fa-user"></i>
                  </span>
                  <input
                    type="text"
                    v-model="form.username"
                    class="form-control text-white bg-dark border-secondary"
                    placeholder="아이디를 입력하세요"
                    required
                    autofocus
                  >
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label text-white">이메일</label>
                <div class="input-group">
                  <span class="input-group-text bg-transparent text-white border-secondary">
                    <i class="fas fa-envelope"></i>
                  </span>
                  <input
                    type="email"
                    v-model="form.email"
                    class="form-control text-white bg-dark border-secondary"
                    placeholder="가입 시 입력한 이메일"
                    required
                  >
                </div>
                <small class="text-white-50">이메일로 인증코드를 보내드립니다.</small>
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
                  <span v-if="loading">
                    <i class="fas fa-spinner fa-spin"></i> 전송 중...
                  </span>
                  <span v-else>
                    <i class="fas fa-paper-plane"></i> 인증코드 받기
                  </span>
                </button>
              </div>
            </form>

            <!-- Step 2: 인증코드 입력 -->
            <form v-else-if="step === 2" @submit.prevent="verifyCodeAndReset">
              <div class="alert alert-info mb-4">
                <i class="fas fa-info-circle me-2"></i>
                <span>{{ maskedEmail }}로 인증코드를 전송했습니다.</span>
              </div>

              <div class="mb-4">
                <label class="form-label text-white">인증코드 (6자리)</label>
                <div class="input-group">
                  <span class="input-group-text bg-transparent text-white border-secondary">
                    <i class="fas fa-shield-alt"></i>
                  </span>
                  <input
                    type="text"
                    v-model="form.code"
                    class="form-control text-white bg-dark border-secondary text-center fs-4 letter-spacing-wide"
                    placeholder="000000"
                    maxlength="6"
                    required
                    autofocus
                    @input="onCodeInput"
                  >
                </div>
                <small class="text-white-50">인증코드는 5분간 유효합니다.</small>
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg" :disabled="loading || form.code.length !== 6">
                  <span v-if="loading">
                    <i class="fas fa-spinner fa-spin"></i> 확인 중...
                  </span>
                  <span v-else>
                    <i class="fas fa-check"></i> 인증 확인
                  </span>
                </button>
                <button type="button" class="btn btn-outline-light" @click="resendCode" :disabled="resendCooldown > 0">
                  <span v-if="resendCooldown > 0">
                    <i class="fas fa-clock"></i> {{ resendCooldown }}초 후 재전송 가능
                  </span>
                  <span v-else>
                    <i class="fas fa-redo"></i> 인증코드 재전송
                  </span>
                </button>
              </div>
            </form>

            <hr class="my-4 border-secondary">

            <div class="text-center">
              <router-link to="/login" class="text-decoration-none text-white-50 me-3">
                <i class="fas fa-sign-in-alt"></i> 로그인
              </router-link>
              <router-link to="/find-username" class="text-decoration-none text-white-50">
                <i class="fas fa-search"></i> 아이디 찾기
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const { showToast } = useToast()

const form = ref({
  username: '',
  email: '',
  code: ''
})

const step = ref(1)
const loading = ref(false)
const message = ref('')
const maskedEmail = ref('')
const resendCooldown = ref(0)

let cooldownTimer = null

// 인증코드 입력 시 숫자만 허용
const onCodeInput = (e) => {
  form.value.code = e.target.value.replace(/[^0-9]/g, '').slice(0, 6)
}

// Step 1: 인증코드 발송
const sendVerificationCode = async () => {
  loading.value = true

  try {
    const response = await api.post('/api/auth/password-reset/send-code/', {
      username: form.value.username,
      email: form.value.email
    })

    if (response.data.success) {
      step.value = 2
      maskedEmail.value = response.data.masked_email
      showToast('인증코드를 전송했습니다!', 'success')
      startResendCooldown()
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || '아이디와 이메일이 일치하는 계정이 없습니다.'
    showToast(errorMsg, 'error')
  } finally {
    loading.value = false
  }
}

// Step 2: 인증코드 확인 및 임시 비밀번호 발송
const verifyCodeAndReset = async () => {
  loading.value = true

  try {
    const response = await api.post('/api/auth/password-reset/verify/', {
      username: form.value.username,
      email: form.value.email,
      code: form.value.code
    })

    if (response.data.success) {
      step.value = 3
      message.value = response.data.message
      showToast('임시 비밀번호를 전송했습니다!', 'success')
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || '인증에 실패했습니다.'
    showToast(errorMsg, 'error')
  } finally {
    loading.value = false
  }
}

// 인증코드 재전송
const resendCode = async () => {
  await sendVerificationCode()
}

// 재전송 쿨다운 시작
const startResendCooldown = () => {
  resendCooldown.value = 60
  if (cooldownTimer) clearInterval(cooldownTimer)

  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(cooldownTimer)
    }
  }, 1000)
}

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})
</script>

<style scoped>
.letter-spacing-wide {
  letter-spacing: 0.5em;
}

/* Responsive Padding */
.responsive-padding {
  padding: 3rem !important;
}

@media (max-width: 768px) {
  .responsive-padding {
    padding: 3% !important;
  }
}
</style>