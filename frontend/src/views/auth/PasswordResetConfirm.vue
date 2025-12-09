<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-5 col-12 mx-auto px-1 px-md-3">
        <div class="glass-card shadow-lg responsive-padding">
            <h2 class="text-center mb-4 text-white">
              <i class="fas fa-lock text-primary"></i> 비밀번호 재설정
            </h2>

            <p class="text-white-50 text-center mb-4">
              새로운 비밀번호를 입력해주세요.
            </p>

            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label class="form-label text-white">새 비밀번호</label>
                <div class="input-group">
                  <span class="input-group-text bg-transparent text-white border-secondary">
                    <i class="fas fa-lock"></i>
                  </span>
                  <input
                    v-model="formData.new_password1"
                    type="password"
                    class="form-control text-white bg-dark border-secondary"
                    required
                  >
                </div>
                <small class="text-white-50">8자 이상, 영문/숫자/특수문자 포함</small>
              </div>

              <div class="mb-4">
                <label class="form-label text-white">새 비밀번호 확인</label>
                <div class="input-group">
                  <span class="input-group-text bg-transparent text-white border-secondary">
                    <i class="fas fa-lock"></i>
                  </span>
                  <input
                    v-model="formData.new_password2"
                    type="password"
                    class="form-control text-white bg-dark border-secondary"
                    required
                  >
                </div>
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg">
                  <i class="fas fa-save"></i> 비밀번호 변경
                </button>
              </div>
            </form>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'

const router = useRouter()

const formData = ref({
  new_password1: '',
  new_password2: ''
})

const handleSubmit = async () => {
  if (formData.value.new_password1 !== formData.value.new_password2) {
    alert('비밀번호가 일치하지 않습니다.')
    return
  }

  if (formData.value.new_password1.length < 8) {
    alert('비밀번호는 8자 이상이어야 합니다.')
    return
  }

  try {
    const response = await api.post('/api/users/password-reset-confirm/', formData.value)

    if (response.data.success) {
      alert('비밀번호가 성공적으로 변경되었습니다.')
      router.push('/login')
    } else {
      alert(response.data.message || '비밀번호 변경에 실패했습니다.')
    }
  } catch (error) {
    console.error('비밀번호 변경 실패:', error)
    alert('비밀번호 변경 중 오류가 발생했습니다.')
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
