<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-6 col-md-8 col-11 mx-auto px-3 px-md-4">
        <div class="glass-card p-4 p-md-5">
          <!-- Step 1: 첫 번째 확인 -->
          <div v-if="step === 1">
            <h2 class="text-center mb-4 text-white">
              <i class="fas fa-user-times me-2 text-danger"></i>회원 탈퇴
            </h2>

            <div class="alert alert-warning mb-4">
              <i class="fas fa-exclamation-triangle me-2"></i>
              <strong>주의!</strong> 회원 탈퇴 시 모든 데이터가 삭제되며 복구할 수 없습니다.
            </div>

            <div class="mb-4">
              <h5 class="text-white mb-3">탈퇴 시 삭제되는 정보</h5>
              <ul class="text-white-50">
                <li>회원 정보 (아이디, 이메일, 생년월일 등)</li>
                <li>운세 기록 및 저장된 운세 데이터</li>
                <li>등록한 아이템 정보</li>
                <li>OOTD 및 메뉴 추천 기록</li>
              </ul>
            </div>

            <div class="d-grid gap-2">
              <button class="btn btn-danger btn-lg rounded-pill" @click="goToStep2">
                <i class="fas fa-arrow-right me-2"></i>탈퇴 진행하기
              </button>
              <router-link to="/profile" class="btn btn-warning btn-lg rounded-pill">
                <i class="fas fa-arrow-left me-2"></i>취소하고 돌아가기
              </router-link>
            </div>
          </div>

          <!-- Step 2: 최종 확인 -->
          <div v-else-if="step === 2">
            <h2 class="text-center mb-4 text-white">
              <i class="fas fa-exclamation-circle me-2 text-danger"></i>최종 확인
            </h2>

            <div class="alert alert-danger mb-4" justify-content-center>
              <i class="fas fa-exclamation-triangle me-2"></i>
              <strong>정말로 탈퇴하시겠습니까?</strong><br>
              이 작업은 되돌릴 수 없습니다.
            </div>

            <div class="mb-4">
              <label class="form-label text-white">탈퇴 확인을 위해 아이디를 입력해주세요</label>
              <input
                type="text"
                v-model="confirmUsername"
                class="form-control"
                :placeholder="authStore.user?.username"
              >
              <small class="text-white-50">
                본인 확인을 위해 현재 로그인된 아이디를 정확히 입력해주세요.
              </small>
            </div>

            <div class="form-check mb-4">
              <input
                type="checkbox"
                class="form-check-input"
                id="confirmCheck"
                v-model="confirmChecked"
              >
              <label class="form-check-label text-white" for="confirmCheck">
                위 내용을 모두 확인하였으며, 회원 탈퇴에 동의합니다.
              </label>
            </div>

            <div class="d-grid gap-2">
              <button
                class="btn btn-danger btn-lg rounded-pill"
                @click="handleDeleteAccount"
                :disabled="!canDelete || isDeleting"
              >
                <span v-if="isDeleting">
                  <i class="fas fa-spinner fa-spin me-2"></i>처리 중...
                </span>
                <span v-else>
                  <i class="fas fa-user-times me-2"></i>회원 탈퇴 완료하기
                </span>
              </button>
              <button class="btn btn-outline-light" @click="step = 1">
                <i class="fas fa-arrow-left me-2"></i>이전으로
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const { showToast } = useToast()

const step = ref(1)
const confirmUsername = ref('')
const confirmChecked = ref(false)
const isDeleting = ref(false)

const canDelete = computed(() => {
  return confirmUsername.value === authStore.user?.username && confirmChecked.value
})

const goToStep2 = () => {
  step.value = 2
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

const handleDeleteAccount = async () => {
  if (!canDelete.value) return

  isDeleting.value = true

  try {
    await api.delete('/api/auth/me/')
    showToast('회원 탈퇴가 완료되었습니다. 그동안 이용해주셔서 감사합니다.', 'success')
    await authStore.logout()
    router.push('/')
  } catch (error) {
    console.error('회원 탈퇴 실패:', error)
    showToast('회원 탈퇴에 실패했습니다. 다시 시도해주세요.', 'error')
  } finally {
    isDeleting.value = false
  }
}
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.form-control {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.form-control:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(220, 53, 69, 0.5);
  color: white;
  box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
}

.form-control::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.table-borderless th,
.table-borderless td {
  padding: 0.5rem 0;
  border: none;
}

.form-check-input {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.form-check-input:checked {
  background-color: #dc3545;
  border-color: #dc3545;
}

.alert-warning {
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid rgba(255, 193, 7, 0.3);
  color: #ffc107;
}

.alert-danger {
  background: rgba(220, 53, 69, 0.2);
  border: 1px solid rgba(220, 53, 69, 0.3);
  color: #ff6b7a;
}
</style>
