<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-5 col-12 mx-auto px-1 px-md-3">
        <div class="glass-card shadow-lg responsive-padding">
          <h2 class="text-center mb-4 text-white">
            <i class="fas fa-lock text-primary"></i> 비밀번호 변경
          </h2>

          <div v-if="mustChange" class="alert alert-warning mb-4">
            <i class="fas fa-exclamation-triangle me-2"></i>
            임시 비밀번호로 로그인하셨습니다. 보안을 위해 비밀번호를 변경해주세요.
          </div>

          <form @submit.prevent="handleChangePassword">
            <div class="mb-3">
              <label class="form-label text-white">현재 비밀번호</label>
              <div class="input-group">
                <span class="input-group-text bg-transparent text-white border-secondary">
                  <i class="fas fa-key"></i>
                </span>
                <input
                  type="password"
                  v-model="form.old_password"
                  class="form-control bg-transparent text-white border-secondary"
                  placeholder="현재 비밀번호"
                  required
                >
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label text-white">새 비밀번호</label>
              <div class="input-group">
                <span class="input-group-text bg-transparent text-white border-secondary">
                  <i class="fas fa-lock"></i>
                </span>
                <input
                  type="password"
                  v-model="form.new_password"
                  class="form-control bg-transparent text-white border-secondary"
                  placeholder="8자 이상 입력하세요"
                  required
                  minlength="8"
                >
              </div>
            </div>

            <div class="mb-4">
              <label class="form-label text-white">새 비밀번호 확인</label>
              <div class="input-group">
                <span class="input-group-text bg-transparent text-white border-secondary">
                  <i class="fas fa-check"></i>
                </span>
                <input
                  type="password"
                  v-model="form.new_password2"
                  class="form-control bg-transparent text-white border-secondary"
                  placeholder="새 비밀번호를 한 번 더 입력하세요"
                  required
                  minlength="8"
                >
              </div>
            </div>

            <div class="d-grid gap-2">
              <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                비밀번호 변경하기
              </button>
              <router-link to="/profile" class="btn btn-outline-light" v-if="!mustChange">
                취소
              </router-link>
            </div>
          </form>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { showToast } = useToast()

// 임시 비밀번호 변경 필수 여부
const mustChange = computed(() => route.query.must_change === 'true')

const form = ref({
  old_password: '',
  new_password: '',
  new_password2: ''
})

const loading = ref(false)

const handleChangePassword = async () => {
  if (form.value.new_password !== form.value.new_password2) {
    showToast('새 비밀번호가 일치하지 않습니다.', 'error')
    return
  }

  if (form.value.new_password.length < 8) {
    showToast('비밀번호는 8자 이상이어야 합니다.', 'error')
    return
  }

  loading.value = true

  try {
    const response = await api.post('/api/auth/password/change/', {
      old_password: form.value.old_password,
      new_password: form.value.new_password,
      new_password2: form.value.new_password2
    })

    if (response.data.success) {
      // 비밀번호 변경 플래그 해제
      if (authStore.mustChangePassword) {
        authStore.mustChangePassword = false
        localStorage.setItem('must_change_password', 'false')
      }

      showToast('비밀번호가 변경되었습니다.', 'success')

      // 강제 변경이었으면 홈으로, 아니면 프로필로
      if (mustChange.value) {
        router.push('/')
      } else {
        router.push('/profile')
      }
    }
  } catch (error) {
    const errors = error.response?.data?.errors
    if (errors) {
      if (errors.old_password) {
        showToast('현재 비밀번호가 올바르지 않습니다.', 'error')
      } else if (errors.new_password) {
        showToast(errors.new_password[0], 'error')
      } else {
        showToast('비밀번호 변경에 실패했습니다.', 'error')
      }
    } else {
      showToast(error.response?.data?.error || '비밀번호 변경에 실패했습니다.', 'error')
    }
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
