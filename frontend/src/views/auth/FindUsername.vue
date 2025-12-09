<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-5 col-12 mx-auto px-1 px-md-3">
        <div class="glass-card shadow-lg responsive-padding">
          <h2 class="text-center mb-4 text-white">
            <i class="fas fa-search text-primary"></i> 아이디 찾기
          </h2>

          <!-- 전송 완료 -->
          <div v-if="sent" class="text-center mb-4">
            <div class="alert alert-success">
              <i class="fas fa-check-circle me-2"></i>
              <p class="mb-0">{{ message }}</p>
            </div>
            <div class="d-grid gap-2 mt-4">
              <router-link to="/login" class="btn btn-primary btn-lg">
                <i class="fas fa-sign-in-alt"></i> 로그인하기
              </router-link>
            </div>
          </div>

          <!-- 입력 폼 -->
          <form v-else @submit.prevent="handleFindUsername">
            <div class="mb-4">
              <label class="form-label text-white">이메일</label>
              <div class="input-group">
                <span class="input-group-text bg-transparent text-white border-secondary">
                  <i class="fas fa-envelope"></i>
                </span>
                <input
                  type="email"
                  v-model="form.email"
                  class="form-control bg-transparent text-white border-secondary"
                  placeholder="가입 시 등록한 이메일"
                  required
                >
              </div>
            </div>

            <div class="d-grid gap-2">
              <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                아이디 찾기
              </button>
            </div>

            <div class="text-center mt-3">
              <router-link to="/find-password" class="text-white-50 text-decoration-none small">
                비밀번호 찾기
              </router-link>
            </div>
          </form>
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
  email: ''
})

const loading = ref(false)
const sent = ref(false)
const message = ref('')

const handleFindUsername = async () => {
  loading.value = true

  try {
    const response = await api.post('/api/auth/find-username/', {
      email: form.value.email
    })

    if (response.data.success) {
      sent.value = true
      message.value = response.data.message
      showToast('이메일을 전송했습니다!', 'success')
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || '해당 이메일로 가입된 계정이 없습니다.'
    showToast(errorMsg, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
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
