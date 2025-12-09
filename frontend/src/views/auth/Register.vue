<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-6 col-md-8 col-11 mx-auto px-3 px-md-4">
        <div class="glass-card p-4 p-md-5">
          <h2 class="text-center mb-4 text-white">
            <i class="fas fa-user-plus me-2"></i>회원가입
          </h2>

          <form @submit.prevent="handleRegister" novalidate>
            <!-- 필수 정보 -->
            <h5 class="mb-3 text-white border-bottom border-light border-opacity-25 pb-2">필수 정보</h5>

            <div class="mb-3">
              <label class="form-label">아이디 <span class="text-warning">*</span></label>
              <div class="d-flex gap-2">
                <input
                  type="text"
                  v-model="form.username"
                  class="form-control"
                  required
                  placeholder="아이디를 입력하세요"
                  :class="{ 'is-valid': usernameChecked && usernameAvailable, 'is-invalid': usernameChecked && !usernameAvailable }"
                >
                <button type="button" class="btn btn-outline-light btn-sm flex-shrink-0" @click="checkUsername" :disabled="!form.username">
                  중복확인
                </button>
              </div>
              <small v-if="usernameChecked" :class="usernameAvailable ? 'text-success' : 'text-danger'">
                {{ usernameMessage }}
              </small>
            </div>

            <div class="row mb-3">
              <div class="col-md-6 mb-3 mb-md-0">
                <label class="form-label">이름 <span class="text-warning">*</span></label>
                <input
                  type="text"
                  v-model="form.first_name"
                  class="form-control"
                  required
                  placeholder="실명을 입력하세요"
                >
              </div>
              <div class="col-md-6">
                <label class="form-label">성별 <span class="text-warning">*</span></label>
                <select v-model="form.gender" class="form-select" required>
                  <option value="">선택하세요</option>
                  <option value="M">남성</option>
                  <option value="F">여성</option>
                </select>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-3">
                <label class="form-label">생년월일 구분 <span class="text-warning">*</span></label>
                <select v-model="form.calendar_type" class="form-select" required>
                  <option value="solar">양력</option>
                  <option value="lunar">음력</option>
                </select>
              </div>
              <div class="col-md-9">
                <label class="form-label">생년월일 <span class="text-warning">*</span></label>
                <div class="row g-2">
                  <div class="col-4">
                    <select v-model="selectedYear" class="form-select" @change="updateBirthDate" required>
                      <option value="" disabled>년도</option>
                      <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}년</option>
                    </select>
                  </div>
                  <div class="col-4">
                    <select v-model="selectedMonth" class="form-select" @change="updateBirthDate" required>
                      <option value="" disabled>월</option>
                      <option v-for="month in 12" :key="month" :value="month">{{ month }}월</option>
                    </select>
                  </div>
                  <div class="col-4">
                    <select v-model="selectedDay" class="form-select" @change="updateBirthDate" required>
                      <option value="" disabled>일</option>
                      <option v-for="day in daysInMonth" :key="day" :value="day">{{ day }}일</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">이메일 <span class="text-warning">*</span></label>
              <div class="d-flex gap-2">
                <input
                  type="email"
                  v-model="form.email"
                  class="form-control"
                  required
                  placeholder="example@email.com"
                  :class="{ 'is-valid': emailChecked && emailAvailable, 'is-invalid': emailChecked && !emailAvailable }"
                >
                <button type="button" class="btn btn-outline-light btn-sm flex-shrink-0" @click="checkEmail" :disabled="!form.email">
                  중복확인
                </button>
              </div>
              <small v-if="emailChecked" :class="emailAvailable ? 'text-success' : 'text-danger'">
                {{ emailMessage }}
              </small>
            </div>

            <div class="mb-3">
              <label class="form-label">비밀번호 <span class="text-warning">*</span></label>
              <input
                type="password"
                v-model="form.password"
                class="form-control"
                required
                placeholder="비밀번호를 입력하세요"
              >
              <small class="form-text">
                <ul class="mb-0 ps-3 mt-1">
                  <li>8자 이상 입력해주세요</li>
                  <li>숫자로만 이루어진 비밀번호는 사용할 수 없습니다</li>
                  <li>너무 흔한 비밀번호는 사용할 수 없습니다</li>
                </ul>
              </small>
            </div>

            <div class="mb-3">
              <label class="form-label">비밀번호 확인 <span class="text-warning">*</span></label>
              <input
                type="password"
                v-model="form.password2"
                class="form-control"
                required
                placeholder="비밀번호를 다시 입력하세요"
              >
            </div>

            <div class="my-4 border-top border-light border-opacity-25"></div>

            <!-- 선택 정보 -->
            <h5 class="mb-3 text-white">선택 정보</h5>
            <p class="text-white opacity-75 small mb-3">더 정확한 운세를 위한 추가 정보입니다</p>

            <div class="mb-3">
              <label class="form-label">태어난 시각</label>
              <input
                type="time"
                v-model="form.birth_time"
                class="form-control"
              >
              <small class="form-text">시주를 포함한 정확한 사주 계산에 사용됩니다</small>
            </div>

            <div class="mb-3">
              <label class="form-label">MBTI</label>
              <select v-model="form.mbti" class="form-select">
                <option value="">선택하세요</option>
                <option value="ISTJ">ISTJ</option>
                <option value="ISTP">ISTP</option>
                <option value="ISFJ">ISFJ</option>
                <option value="ISFP">ISFP</option>
                <option value="INTJ">INTJ</option>
                <option value="INTP">INTP</option>
                <option value="INFJ">INFJ</option>
                <option value="INFP">INFP</option>
                <option value="ESTJ">ESTJ</option>
                <option value="ESTP">ESTP</option>
                <option value="ESFJ">ESFJ</option>
                <option value="ESFP">ESFP</option>
                <option value="ENTJ">ENTJ</option>
                <option value="ENTP">ENTP</option>
                <option value="ENFJ">ENFJ</option>
                <option value="ENFP">ENFP</option>
              </select>
            </div>

            <div class="mb-4">
              <label class="form-label">퍼스널컬러</label>
              <select v-model="form.personal_color" class="form-select">
                <option value="">선택하세요</option>
                <option value="spring_warm">봄 웜톤</option>
                <option value="summer_cool">여름 쿨톤</option>
                <option value="autumn_warm">가을 웜톤</option>
                <option value="winter_cool">겨울 쿨톤</option>
              </select>
              <small class="form-text">색상 추천에 반영됩니다</small>
            </div>

            <div class="d-grid gap-2 mt-4">
              <button type="submit" class="btn btn-gradient btn-lg rounded-pill">
                <i class="fas fa-user-plus me-2"></i>회원가입
              </button>
            </div>
          </form>

          <div class="text-center mt-4">
            <p class="text-white">
              이미 계정이 있으신가요?
              <router-link to="/login" class="text-primary-light text-decoration-none">
                로그인
              </router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const { showToast } = useToast()

const form = ref({
  username: '',
  last_name: '',
  first_name: '',
  birth_date: '',
  calendar_type: 'solar',
  gender: '',
  email: '',
  password: '',
  password2: '',
  birth_time: '',
  mbti: '',
  personal_color: ''
})

// 아이디 중복확인
const usernameChecked = ref(false)
const usernameAvailable = ref(false)
const usernameMessage = ref('')

// 이메일 중복확인
const emailChecked = ref(false)
const emailAvailable = ref(false)
const emailMessage = ref('')

// 아이디 변경시 중복확인 초기화
watch(() => form.value.username, () => {
  usernameChecked.value = false
  usernameAvailable.value = false
})

// 이메일 변경시 중복확인 초기화
watch(() => form.value.email, () => {
  emailChecked.value = false
  emailAvailable.value = false
})

const checkUsername = async () => {
  if (!form.value.username) return
  try {
    const response = await api.get('/api/auth/check-username/', {
      params: { username: form.value.username }
    })
    usernameChecked.value = true
    usernameAvailable.value = response.data.available
    usernameMessage.value = response.data.message
  } catch (error) {
    usernameChecked.value = true
    usernameAvailable.value = false
    usernameMessage.value = '중복 확인 중 오류가 발생했습니다.'
  }
}

const checkEmail = async () => {
  if (!form.value.email) return
  try {
    const response = await api.get('/api/auth/check-email/', {
      params: { email: form.value.email }
    })
    emailChecked.value = true
    emailAvailable.value = response.data.available
    emailMessage.value = response.data.message
  } catch (error) {
    emailChecked.value = true
    emailAvailable.value = false
    emailMessage.value = '중복 확인 중 오류가 발생했습니다.'
  }
}

// 생년월일 선택
const selectedYear = ref('')
const selectedMonth = ref('')
const selectedDay = ref('')

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let year = currentYear; year >= 1900; year--) {
    years.push(year)
  }
  return years
})

const daysInMonth = computed(() => {
  if (!selectedYear.value || !selectedMonth.value) return 31
  const year = parseInt(selectedYear.value)
  const month = parseInt(selectedMonth.value)
  return new Date(year, month, 0).getDate()
})

const updateBirthDate = () => {
  if (selectedYear.value && selectedMonth.value && selectedDay.value) {
    const year = selectedYear.value
    const month = String(selectedMonth.value).padStart(2, '0')
    const day = String(selectedDay.value).padStart(2, '0')
    form.value.birth_date = `${year}-${month}-${day}`
  }
}

const handleRegister = async () => {
  if (form.value.password !== form.value.password2) {
    showToast('비밀번호가 일치하지 않습니다.', 'error')
    return
  }

  try {
    await authStore.register(form.value)
    showToast('회원가입이 완료되었습니다. 로그인 후 모든 서비스를 이용하실 수 있습니다.', 'success')
    router.push('/login')
  } catch (error) {
    console.error('Registration failed:', error)
    showToast(error.message || '회원가입에 실패했습니다. 다시 시도해주세요.', 'error')
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

.form-control,
.form-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.form-control:focus,
.form-select:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(102, 126, 234, 0.5);
  color: white;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.form-control::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-label {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 500;
}

.form-text {
  color: rgba(255, 255, 255, 0.7);
}

/* Select option 스타일 */
.form-select option {
  background: #1a1a2e;
  color: white;
}
</style>
