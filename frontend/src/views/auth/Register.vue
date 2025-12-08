<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-6 mx-auto">
        <div class="glass-card shadow-lg">
          <div class="card-body p-5">
            <h2 class="text-center mb-4 text-white">
              <i class="fas fa-user-plus text-primary"></i> 회원가입
            </h2>

            <form @submit.prevent="handleRegister">
              <h5 class="mb-3 text-white border-bottom border-secondary pb-2">계정 정보</h5>

              <div class="mb-3">
                <label class="form-label text-white">아이디 <span class="text-danger">*</span></label>
                <div class="d-flex gap-2 align-items-center">
                  <input
                    type="text"
                    :value="registerForm.username"
                    @input="handleUsernameInput"
                    @compositionend="handleCompositionEnd"
                    :class="['form-control', 'text-white', 'bg-dark', 'border-secondary', 'flex-grow-1', usernameStatus.class]"
                    required
                  >
                  <button type="button" class="btn btn-outline-light btn-check-duplicate flex-shrink-0" @click="checkUsername">중복확인</button>
                </div>
                <small :class="usernameStatus.textClass">{{ usernameStatus.message }}</small>
              </div>

              <div class="mb-3">
                <label class="form-label text-white">이메일</label>
                <div class="d-flex gap-2 align-items-center">
                  <input
                    type="email"
                    v-model="registerForm.email"
                    @input="resetEmailCheck"
                    :class="['form-control', 'text-white', 'bg-dark', 'border-secondary', 'flex-grow-1', emailStatus.class]"
                    placeholder="example@email.com"
                  >
                  <button type="button" class="btn btn-outline-light btn-check-duplicate flex-shrink-0" @click="checkEmail">중복확인</button>
                </div>
                <small :class="emailStatus.textClass" v-html="emailStatus.message"></small>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label text-white">비밀번호 <span class="text-danger">*</span></label>
                  <input
                    type="password"
                    v-model="registerForm.password"
                    class="form-control text-white bg-dark border-secondary"
                    required
                  >
                  <small class="text-white-50">8자 이상, 영문/숫자/특수문자 포함</small>
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label text-white">비밀번호 확인 <span class="text-danger">*</span></label>
                  <input
                    type="password"
                    v-model="registerForm.password2"
                    class="form-control text-white bg-dark border-secondary"
                    required
                  >
                </div>
              </div>

              <h5 class="mb-3 mt-4 text-white border-bottom border-secondary pb-2">기본 정보</h5>

              <div class="row">
                <div class="col-md-3 mb-3">
                  <label class="form-label text-white">성 <span class="text-danger">*</span></label>
                  <input
                    type="text"
                    v-model="registerForm.last_name"
                    class="form-control text-white bg-dark border-secondary"
                    placeholder="예: 홍"
                    required
                  >
                </div>
                <div class="col-md-3 mb-3">
                  <label class="form-label text-white">이름 <span class="text-danger">*</span></label>
                  <input
                    type="text"
                    v-model="registerForm.first_name"
                    class="form-control text-white bg-dark border-secondary"
                    placeholder="예: 길동"
                    required
                  >
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label text-white">생년월일 <span class="text-danger">*</span></label>
                  <input
                    type="date"
                    v-model="registerForm.birth_date"
                    @blur="validateBirthDate"
                    class="form-control text-white bg-dark border-secondary"
                    min="1900-01-01"
                    :max="maxDate"
                    required
                  >
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label text-white">생년월일 구분 <span class="text-danger">*</span></label>
                <select v-model="registerForm.calendar_type" class="form-select text-white bg-dark border-secondary" required>
                  <option value="solar">양력</option>
                  <option value="lunar">음력</option>
                </select>
                <small class="text-white-50">음력 생일인 경우 음력을 선택하세요</small>
              </div>

              <div class="mb-3">
                <label class="form-label text-white">성별 <span class="text-danger">*</span></label>
                <select v-model="registerForm.gender" class="form-select text-white bg-dark border-secondary" required>
                  <option value="">선택하세요</option>
                  <option value="M">남자</option>
                  <option value="F">여자</option>
                </select>
              </div>

              <h5 class="mb-3 mt-4 text-white border-bottom border-secondary pb-2">추가 정보 (선택)</h5>

              <div class="mb-3">
                <label class="form-label text-white">태어난 시각</label>
                <div class="input-group">
                  <select v-model="registerForm.birth_hour" class="form-select text-white bg-dark border-secondary">
                    <option value="">시</option>
                    <option v-for="h in 24" :key="h" :value="String(h-1).padStart(2, '0')">{{ String(h-1).padStart(2, '0') }}시</option>
                  </select>
                  <select v-model="registerForm.birth_minute" class="form-select text-white bg-dark border-secondary">
                    <option value="">분</option>
                    <option v-for="m in 60" :key="m" :value="String(m-1).padStart(2, '0')">{{ String(m-1).padStart(2, '0') }}분</option>
                  </select>
                </div>
                <small class="text-white-50">더 정확한 사주 계산에 사용됩니다</small>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label text-white">MBTI</label>
                  <select v-model="registerForm.mbti" class="form-select text-white bg-dark border-secondary">
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
                  <small class="text-white-50">맞춤형 말투 제공</small>
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label text-white">퍼스널컬러</label>
                  <select v-model="registerForm.personal_color" class="form-select text-white bg-dark border-secondary">
                    <option value="">선택하세요</option>
                    <option value="spring_warm">봄 웜톤</option>
                    <option value="summer_cool">여름 쿨톤</option>
                    <option value="autumn_warm">가을 웜톤</option>
                    <option value="winter_cool">겨울 쿨톤</option>
                  </select>
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label text-white">한자 이름</label>
                <input
                  type="text"
                  v-model="registerForm.chinese_name"
                  class="form-control text-white bg-dark border-secondary"
                  placeholder="예: 金哲秀"
                >
                <small class="text-white-50">작명 원리를 통한 운세 보정</small>
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg">
                  <i class="fas fa-user-plus"></i> 회원가입
                </button>
              </div>
            </form>

            <hr class="my-4 border-secondary">

            <div class="text-center">
              <p class="text-white mb-2">이미 회원이신가요?</p>
              <router-link to="/login" class="btn btn-outline-light">
                로그인하기
              </router-link>
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
import apiClient from '@/config/api'

const router = useRouter()
const authStore = useAuthStore()
const { showToast } = useToast()

const maxDate = computed(() => new Date().toISOString().split('T')[0])

// 중복 체크 상태
const usernameStatus = ref({
  message: '영문, 숫자 조합 4-20자',
  class: '',
  textClass: 'text-white-50',
  checked: false
})

const emailStatus = ref({
  message: '<i class="fas fa-exclamation-triangle"></i> 비밀번호 분실 시 입력하신 이메일로 인증이 진행됩니다',
  class: '',
  textClass: 'text-warning',
  checked: false
})

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  password2: '',
  last_name: '',  // 성
  first_name: '',  // 이름
  birth_date: '',
  calendar_type: 'solar',
  gender: '',
  birth_hour: '',
  birth_minute: '',
  mbti: '',
  personal_color: '',
  chinese_name: ''
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

// 한글 자모를 영문으로 변환
const convertToEnglish = (str) => {
  let result = ''
  for (const char of str) {
    result += k2e[char] || char
  }
  return result.replace(/[^A-Za-z0-9]/g, '')
}

// 일반 입력 처리 (영문 입력 시)
const handleUsernameInput = (event) => {
  const value = event.target.value

  // 중복확인 상태 리셋
  usernameStatus.value = {
    message: '영문, 숫자 조합 4-20자',
    class: '',
    textClass: 'text-white-50',
    checked: false
  }

  // 한글이 없으면 바로 처리
  if (!/[ㄱ-ㅎㅏ-ㅣ가-힣]/.test(value)) {
    registerForm.value.username = value.replace(/[^A-Za-z0-9]/g, '')
  }
}

// 한글 조합 완료 시 변환 (compositionend)
const handleCompositionEnd = (event) => {
  const value = event.target.value
  const converted = convertToEnglish(value)

  // 중복확인 상태 리셋
  usernameStatus.value = {
    message: '영문, 숫자 조합 4-20자',
    class: '',
    textClass: 'text-white-50',
    checked: false
  }

  registerForm.value.username = converted
  event.target.value = converted
}

// 이메일 입력 시 상태 리셋
const resetEmailCheck = () => {
  emailStatus.value = {
    message: '<i class="fas fa-exclamation-triangle"></i> 비밀번호 분실 시 입력하신 이메일로 인증이 진행됩니다',
    class: '',
    textClass: 'text-warning',
    checked: false
  }
}

// 아이디 중복 체크 (버튼 클릭)
const checkUsername = async () => {
  console.log('checkUsername 함수 호출됨')
  const username = registerForm.value.username
  console.log('username:', username)

  if (!username || username.length < 4) {
    console.log('유효성 검사 실패: 4자 미만')
    showToast('아이디는 4자 이상이어야 합니다.', 'error')
    return
  }

  try {
    console.log('API 호출 시작')
    const response = await apiClient.get(`/api/auth/check-username/?username=${encodeURIComponent(username)}`)
    console.log('API 응답:', response)
    if (response.data.available) {
      usernameStatus.value = {
        message: '✓ 사용 가능한 아이디입니다',
        class: 'is-valid',
        textClass: 'text-success',
        checked: true
      }
    } else {
      usernameStatus.value = {
        message: '✗ 이미 사용중인 아이디입니다',
        class: 'is-invalid',
        textClass: 'text-danger',
        checked: false
      }
    }
  } catch {
    showToast('중복 확인 중 오류가 발생했습니다.', 'error')
  }
}

// 이메일 중복 체크 (버튼 클릭)
const checkEmail = async () => {
  const email = registerForm.value.email

  if (!email) {
    showToast('이메일을 입력해주세요.', 'error')
    return
  }

  // 이메일 형식 검증
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    emailStatus.value = {
      message: '✗ 올바른 이메일 형식이 아닙니다',
      class: 'is-invalid',
      textClass: 'text-danger',
      checked: false
    }
    return
  }

  try {
    const response = await apiClient.get(`/api/auth/check-email/?email=${encodeURIComponent(email)}`)
    if (response.data.available) {
      emailStatus.value = {
        message: '✓ 사용 가능한 이메일입니다',
        class: 'is-valid',
        textClass: 'text-success',
        checked: true
      }
    } else {
      emailStatus.value = {
        message: '✗ 이미 사용중인 이메일입니다',
        class: 'is-invalid',
        textClass: 'text-danger',
        checked: false
      }
    }
  } catch {
    showToast('중복 확인 중 오류가 발생했습니다.', 'error')
  }
}

const validateBirthDate = () => {
  const selectedDate = new Date(registerForm.value.birth_date)
  const today = new Date()
  const minDate = new Date('1900-01-01')

  if (selectedDate > today) {
    showToast('미래 날짜는 선택할 수 없습니다.', 'error')
    registerForm.value.birth_date = ''
  } else if (selectedDate < minDate) {
    showToast('1900년 이후 날짜를 선택해주세요.', 'error')
    registerForm.value.birth_date = ''
  }
}

const handleRegister = async () => {
  // 아이디 중복 체크 확인
  if (!usernameStatus.value.checked) {
    showToast('아이디 중복확인을 해주세요.', 'error')
    return
  }

  // 이메일 중복 체크 확인 (입력한 경우만)
  if (registerForm.value.email && !emailStatus.value.checked) {
    showToast('이메일 중복확인을 해주세요.', 'error')
    return
  }

  if (registerForm.value.password !== registerForm.value.password2) {
    showToast('비밀번호가 일치하지 않습니다.', 'error')
    return
  }

  try {
    // 회원가입 데이터 준비 (빈 문자열을 null로 변환)
    const registerData = {
      ...registerForm.value,
      birth_hour: registerForm.value.birth_hour ? parseInt(registerForm.value.birth_hour) : null,
      birth_minute: registerForm.value.birth_minute ? parseInt(registerForm.value.birth_minute) : null,
      email: registerForm.value.email || ''
    }

    await authStore.register(registerData)
    showToast('회원가입이 완료되었습니다.', 'success')
    router.push('/login')
  } catch (error) {
    showToast(error.message || '회원가입에 실패했습니다.', 'error')
  }
}
</script>

<style scoped>
.btn-check-duplicate {
  white-space: nowrap;
  min-width: 80px;
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-check-duplicate:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}
</style>
