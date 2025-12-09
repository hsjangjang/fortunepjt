<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-6 col-12 mx-auto px-1 px-md-3">
          <div class="glass-card responsive-padding">
            <h2 class="text-center mb-4 text-white">
              <i class="fas fa-calculator text-primary-light me-2"></i> 운세 계산
            </h2>

            <div v-if="!authStore.isAuthenticated" class="text-center mb-4">
              <button type="button" class="btn btn-outline-light btn-sm rounded-pill px-3" @click="resetFortune">
                <i class="fas fa-redo me-1"></i> 다시 계산하기
              </button>
            </div>

            <form @submit.prevent="handleSubmit" v-if="!authStore.isAuthenticated" novalidate>
              <h5 class="mb-3 text-white border-bottom border-light border-opacity-25 pb-2">필수 정보</h5>

              <div class="row mb-3">
                <div class="col-md-4">
                  <label class="form-label">생년월일 구분 <span class="text-warning">*</span></label>
                  <select v-model="fortuneForm.calendar_type" class="form-select" required>
                    <option value="solar">양력</option>
                    <option value="lunar">음력</option>
                  </select>
                </div>
                <div class="col-md-8">
                  <label class="form-label">생년월일 <span class="text-warning">*</span></label>
                  <!-- Mobile Native Date Picker -->
                  <div class="d-md-none">
                    <input
                      type="date"
                      v-model="fortuneForm.birth_date"
                      @blur="validateBirthDate"
                      class="form-control"
                      min="1900-01-01"
                      :max="maxDate"
                      required
                    >
                  </div>
                  <!-- Desktop Custom Dropdowns -->
                  <div class="d-none d-md-flex gap-2">
                    <select v-model="selectedYear" class="form-select" @change="updateBirthDate">
                      <option value="" disabled>년도</option>
                      <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}년</option>
                    </select>
                    <select v-model="selectedMonth" class="form-select" @change="updateBirthDate">
                      <option value="" disabled>월</option>
                      <option v-for="month in 12" :key="month" :value="month">{{ month }}월</option>
                    </select>
                    <select v-model="selectedDay" class="form-select" @change="updateBirthDate">
                      <option value="" disabled>일</option>
                      <option v-for="day in daysInMonth" :key="day" :value="day">{{ day }}일</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <small class="form-text">음력 생일인 경우 음력을 선택하세요</small>
              </div>

              <div class="mb-3">
                <label class="form-label">성별 <span class="text-warning">*</span></label>
                <select v-model="fortuneForm.gender" class="form-select" required>
                  <option value="">선택하세요</option>
                  <option value="M">남성</option>
                  <option value="F">여성</option>
                </select>
              </div>

              <div class="my-4 border-top border-light border-opacity-25"></div>

              <h5 class="mb-3 text-white">선택 정보</h5>
              <p class="text-white opacity-visible small mb-3">더 정확한 운세를 위한 추가 정보입니다</p>

              <div class="mb-3">
                <label class="form-label">태어난 시각</label>
                <input
                  type="time"
                  v-model="fortuneForm.birth_time"
                  class="form-control"
                  @click="showTimePicker"
                >
                <small class="form-text">시주를 포함한 정확한 사주 계산에 사용됩니다</small>
              </div>

              <div class="mb-3">
                <label class="form-label">한자 이름</label>
                <input
                  type="text"
                  v-model="fortuneForm.chinese_name"
                  class="form-control"
                  placeholder="예: 金哲秀"
                >
                <small class="form-text">이름의 한자 획수를 통한 운세 보정</small>
              </div>

              <div class="mb-3">
                <label class="form-label">MBTI</label>
                <select v-model="fortuneForm.mbti" class="form-select">
                  <option value="">선택하세요</option>
                  <option value="ISTJ">ISTJ</option>
                  <option value="ISTP">ISTP</option>
                  <option value="ISFJ">ISFJ</option>
                  <option value="ISFP">ISFP</option>
                  <option value="INTJ">INTJ</option>
                  <option value="INTP">INTP</option>
                  <option value="INFJ">INFJ</option>
                  <option value="INFP">INFP</option>
                  <option value="ESTP">ESTP</option>
                  <option value="ESTJ">ESTJ</option>
                  <option value="ESFP">ESFP</option>
                  <option value="ESFJ">ESFJ</option>
                  <option value="ENTP">ENTP</option>
                  <option value="ENTJ">ENTJ</option>
                  <option value="ENFP">ENFP</option>
                  <option value="ENFJ">ENFJ</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">퍼스널컬러</label>
                <select v-model="fortuneForm.personal_color" class="form-select">
                  <option value="">선택하세요</option>
                  <option value="spring_warm">봄 웜톤</option>
                  <option value="summer_cool">여름 쿨톤</option>
                  <option value="autumn_warm">가을 웜톤</option>
                  <option value="winter_cool">겨울 쿨톤</option>
                </select>
                <small class="form-text">색상 추천에 반영됩니다</small>
              </div>

              <div class="d-grid gap-2 mt-5">
                <button type="submit" class="btn btn-gradient btn-lg rounded-pill fw-bold">
                  <i class="fas fa-star me-2"></i> 운세 확인하기
                </button>
              </div>
            </form>

            <div v-if="!authStore.isAuthenticated" class="text-center mt-4">
              <p class="text-white opacity-visible mb-3">
                회원가입하면 매일 자동으로 운세를 확인할 수 있습니다
              </p>
              <router-link to="/register" class="btn btn-outline-light rounded-pill px-4">
                회원가입하기
              </router-link>
            </div>
          </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFortuneStore } from '@/stores/fortune'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const router = useRouter()
const authStore = useAuthStore()
const fortuneStore = useFortuneStore()
const { showToast } = useToast()

const maxDate = computed(() => new Date().toISOString().split('T')[0])

// Django: CalculateFortuneView.get() 로직 (line 310-319)
// 로그인 사용자가 접근하면 운세 확인 후 리다이렉트
onMounted(async () => {
  if (authStore.isAuthenticated) {
    // 로그인 사용자: 운세 체크
    await fortuneStore.checkTodayFortune()

    if (fortuneStore.hasTodayFortune) {
      // 오늘 운세 있음 → /fortune/today로 리다이렉트 (Django line 316)
      router.replace({ name: 'fortune-today' })
    } else {
      // 운세 없음 → /fortune/loading으로 리다이렉트 (Django line 319)
      router.replace({ name: 'fortune-loading' })
    }
  }
  // 비로그인 사용자는 폼 표시 (Django line 322)
})

const fortuneForm = ref({
  calendar_type: 'solar',
  birth_date: '',
  gender: '',
  birth_time: '',
  chinese_name: '',
  mbti: '',
  personal_color: ''
})

// Desktop Date Picker Logic
const selectedYear = ref('')
const selectedMonth = ref('')
const selectedDay = ref('')

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let y = currentYear; y >= 1900; y--) {
    years.push(y)
  }
  return years
})

const daysInMonth = computed(() => {
  if (!selectedYear.value || !selectedMonth.value) return 31
  return new Date(selectedYear.value, selectedMonth.value, 0).getDate()
})

const updateBirthDate = () => {
  if (selectedYear.value && selectedMonth.value && selectedDay.value) {
    const y = selectedYear.value
    const m = String(selectedMonth.value).padStart(2, '0')
    const d = String(selectedDay.value).padStart(2, '0')
    fortuneForm.value.birth_date = `${y}-${m}-${d}`
    validateBirthDate()
  }
}

const showTimePicker = (event) => {
  if (event.target.showPicker) {
    event.target.showPicker()
  }
}

const validateBirthDate = () => {
  const selectedDate = new Date(fortuneForm.value.birth_date)
  const today = new Date()
  const minDate = new Date('1900-01-01')

  if (selectedDate > today) {
    showToast('미래 날짜는 선택할 수 없습니다.', 'error')
    fortuneForm.value.birth_date = ''
  } else if (selectedDate < minDate) {
    showToast('1900년 이후 날짜를 선택해주세요.', 'error')
    fortuneForm.value.birth_date = ''
  }
}

const resetFortune = () => {
  fortuneForm.value = {
    calendar_type: 'solar',
    birth_date: '',
    gender: '',
    birth_time: '',
    chinese_name: '',
    mbti: '',
    personal_color: ''
  }
  showToast('운세가 초기화되었습니다. 새로운 정보를 입력해주세요.', 'success')
}

const handleSubmit = () => {
  // 필수 항목 검증
  if (!fortuneForm.value.birth_date) {
    showToast('생년월일을 입력해주세요.', 'error')
    return
  }
  if (!fortuneForm.value.gender) {
    showToast('성별을 선택해주세요.', 'error')
    return
  }

  // 쿼리 파라미터 구성 (빈 값은 제외)
  const query = {
    birth_date: fortuneForm.value.birth_date,
    gender: fortuneForm.value.gender,
    calendar_type: fortuneForm.value.calendar_type
  }

  // 선택 항목은 값이 있을 때만 추가
  if (fortuneForm.value.birth_time) {
    query.birth_time = fortuneForm.value.birth_time
  }
  if (fortuneForm.value.chinese_name) {
    query.chinese_name = fortuneForm.value.chinese_name
  }
  if (fortuneForm.value.mbti) {
    query.mbti = fortuneForm.value.mbti
  }
  if (fortuneForm.value.personal_color) {
    query.personal_color = fortuneForm.value.personal_color
  }

  router.push({
    path: '/fortune/loading',
    query
  })
}
</script>

<style scoped>
/* FortuneCalculate 페이지 전용 스타일 */
.form-control, .form-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(5px);
}

.form-control:focus, .form-select:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: var(--primary);
  color: white;
  box-shadow: 0 0 0 0.25rem rgba(124, 58, 237, 0.25);
}

.form-control::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.form-label {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 500;
}

.form-text {
  color: rgba(255, 255, 255, 0.7) !important;
}

option {
  background: #1e1b4b;
  color: white;
}

::-webkit-calendar-picker-indicator {
  filter: invert(1);
  opacity: 0.8;
  cursor: pointer;
}
@media (max-width: 768px) {
  .responsive-padding {
    padding: 3% !important;
  }
  
  .glass-card {
    border-radius: 12px;
  }
}
</style>
