<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-5 mx-auto">
        <div class="glass-card shadow-lg">
          <div class="card-body p-5">
            <h2 class="text-center mb-4 text-white">
              <i class="fas fa-key text-primary"></i> 비밀번호 찾기
            </h2>

            <!-- 전송 완료 -->
            <div v-if="sent" class="text-center mb-4">
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

            <!-- 입력 폼 -->
            <form v-else @submit.prevent="handleFindPassword">
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
                <small class="text-white-50">이메일로 임시 비밀번호를 보내드립니다.</small>
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
                  <span v-if="loading">
                    <i class="fas fa-spinner fa-spin"></i> 전송 중...
                  </span>
                  <span v-else>
                    <i class="fas fa-paper-plane"></i> 임시 비밀번호 받기
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
import { ref } from 'vue'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const { showToast } = useToast()

const form = ref({
  username: '',
  email: ''
})

const loading = ref(false)
const sent = ref(false)
const message = ref('')

const handleFindPassword = async () => {
  loading.value = true

  try {
    const response = await api.post('/api/auth/find-password/', {
      username: form.value.username,
      email: form.value.email
    })

    if (response.data.success) {
      sent.value = true
      message.value = response.data.message
      showToast('임시 비밀번호를 전송했습니다!', 'success')
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || '아이디와 이메일이 일치하는 계정이 없습니다.'
    showToast(errorMsg, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Django style.css를 사용하므로 추가 스타일 불필요 */
</style>
