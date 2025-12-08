<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-5 mx-auto">
        <div class="glass-card shadow-lg">
          <div class="card-body p-5">
            <h2 class="text-center mb-4 text-white">
              <i class="fas fa-key text-primary"></i> 비밀번호 찾기
            </h2>

            <p class="text-white-50 text-center mb-4">
              가입 시 등록한 아이디와 이메일을 입력해주세요.<br>
              정보가 일치하면 비밀번호를 재설정할 수 있습니다.
            </p>

            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label class="form-label text-white">아이디</label>
                <div class="input-group">
                  <span class="input-group-text bg-transparent text-white border-secondary">
                    <i class="fas fa-user"></i>
                  </span>
                  <input
                    v-model="formData.username"
                    type="text"
                    class="form-control text-white bg-dark border-secondary"
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
                    v-model="formData.email"
                    type="email"
                    class="form-control text-white bg-dark border-secondary"
                    required
                  >
                </div>
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg">
                  <i class="fas fa-check-circle"></i> 확인
                </button>
              </div>
            </form>

            <hr class="my-4 border-secondary">

            <div class="text-center">
              <router-link to="/login" class="btn btn-outline-light">
                로그인으로 돌아가기
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
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'

const router = useRouter()

const formData = ref({
  username: '',
  email: ''
})

const handleSubmit = async () => {
  try {
    const response = await api.post('/api/users/password-reset/', formData.value)

    if (response.data.success) {
      alert('정보가 확인되었습니다. 비밀번호를 재설정해주세요.')
      router.push('/password-reset-confirm')
    } else {
      alert(response.data.message || '일치하는 정보가 없습니다.')
    }
  } catch (error) {
    console.error('비밀번호 찾기 실패:', error)
    alert('아이디 또는 이메일을 확인해주세요.')
  }
}
</script>
