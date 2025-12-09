<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-8 col-12 px-1 px-md-3">
        <div class="glass-card responsive-padding shadow-lg">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="text-white mb-0">
              <i class="fas fa-user-circle text-primary me-2"></i> 내 프로필
            </h2>
            <button
              v-if="!isEditing"
              @click="editProfile"
              class="btn btn-outline-light rounded-pill px-4"
            >
              <i class="fas fa-edit me-2"></i> 수정
            </button>
          </div>

          <!-- 프로필 정보 표시 (읽기 모드) -->
            <!-- 프로필 수정 폼 -->
            <form v-if="isEditing" @submit.prevent="handleProfileUpdate" style="display: block;">
              <div class="row">
                <div class="col-md-6">
                  <h5>기본 정보</h5>
                  <div class="mb-3">
                    <label class="form-label">이름</label>
                    <div class="d-flex gap-2">
                      <input
                        type="text"
                        v-model="profileForm.last_name"
                        class="form-control glass-input"
                        placeholder="성"
                        style="flex: 1;"
                      >
                      <input
                        type="text"
                        v-model="profileForm.first_name"
                        class="form-control glass-input"
                        placeholder="이름"
                        style="flex: 2;"
                      >
                    </div>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">이메일</label>
                    <input
                      type="email"
                      v-model="profileForm.email"
                      class="form-control glass-input"
                    >
                  </div>
                  <div class="mb-3">
                    <label class="form-label">생년월일</label>
                    <input
                      type="date"
                      v-model="profileForm.birth_date"
                      class="form-control glass-input"
                      required
                    >
                  </div>
                  <div class="mb-3">
                    <label class="form-label">성별</label>
                    <select v-model="profileForm.gender" class="form-select glass-input" required>
                      <option value="M">남자</option>
                      <option value="F">여자</option>
                    </select>
                  </div>
                </div>

                <div class="col-md-6">
                  <h5>추가 정보</h5>
                  <div class="mb-3">
                    <label class="form-label">MBTI</label>
                    <select v-model="profileForm.mbti" class="form-select glass-input">
                      <option value="">선택안함</option>
                      <option v-for="mbti in mbtiChoices" :key="mbti" :value="mbti">{{ mbti }}</option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">퍼스널컬러</label>
                    <select v-model="profileForm.personal_color" class="form-select glass-input">
                      <option value="">선택안함</option>
                      <option value="spring_warm">봄 웜톤</option>
                      <option value="summer_cool">여름 쿨톤</option>
                      <option value="autumn_warm">가을 웜톤</option>
                      <option value="winter_cool">겨울 쿨톤</option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">태어난 시간 (선택)</label>
                    <div class="d-flex gap-2">
                      <select v-model="profileForm.birth_hour" class="form-select glass-input">
                        <option value="">시</option>
                        <option v-for="h in 24" :key="h-1" :value="h-1">{{ String(h-1).padStart(2, '0') }}시</option>
                      </select>
                      <select v-model="profileForm.birth_minute" class="form-select glass-input">
                        <option value="">분</option>
                        <option v-for="m in 60" :key="m-1" :value="m-1">{{ String(m-1).padStart(2, '0') }}분</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <hr class="my-4">

              <div class="text-center">
                <button type="submit" class="btn btn-primary me-2">
                  <i class="fas fa-save"></i> 저장하기
                </button>
                <button type="button" class="btn btn-secondary" @click="cancelEdit">
                  <i class="fas fa-times"></i> 취소
                </button>
              </div>
            </form>

            <!-- 프로필 보기 -->
            <div v-else id="profile-view">
              <div class="row">
                <div class="col-md-6">
                  <h5>기본 정보</h5>
                  <table class="table table-borderless">
                    <tbody>
                      <tr>
                        <th width="40%">이름:</th>
                        <td>{{ fullName || '미입력' }}</td>
                      </tr>
                      <tr>
                        <th>아이디:</th>
                        <td>{{ authStore.user?.username }}</td>
                      </tr>
                      <tr>
                        <th>이메일:</th>
                        <td>{{ authStore.user?.email || '미입력' }}</td>
                      </tr>
                      <tr>
                        <th>생년월일:</th>
                        <td>{{ formatBirthDate(authStore.user?.birth_date) }}</td>
                      </tr>
                      <tr>
                        <th>성별:</th>
                        <td>{{ formatGender(authStore.user?.gender) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div class="col-md-6">
                  <h5>추가 정보</h5>
                  <table class="table table-borderless">
                    <tbody>
                      <tr>
                        <th width="40%">별자리:</th>
                        <td>{{ authStore.user?.zodiac_sign || '계산중' }}</td>
                      </tr>
                      <tr>
                        <th>띠:</th>
                        <td>{{ authStore.user?.chinese_zodiac || '계산중' }}</td>
                      </tr>
                      <tr>
                        <th>MBTI:</th>
                        <td>{{ authStore.user?.mbti || '미입력' }}</td>
                      </tr>
                      <tr>
                        <th>퍼스널컬러:</th>
                        <td>{{ getPersonalColorDisplay(authStore.user?.personal_color) }}</td>
                      </tr>
                      <tr>
                        <th>태어난 시간:</th>
                        <td>{{ formatBirthTime(authStore.user?.birth_time) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <hr class="my-4">

              <div class="text-center">
                <router-link to="/fortune/today" class="btn btn-primary me-2">
                  <i class="fas fa-star"></i> 오늘의 운세 보기
                </router-link>
                <button class="btn btn-outline-secondary" @click="editProfile">
                  <i class="fas fa-edit"></i> 프로필 수정
                </button>
              </div>
            </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'

const authStore = useAuthStore()
const { showToast } = useToast()

// 풀네임 (성 + 이름)
const fullName = computed(() => {
  const user = authStore.user
  if (!user) return ''
  const lastName = user.last_name || ''
  const firstName = user.first_name || ''
  return (lastName + firstName).trim()
})

const isEditing = ref(false)
const profileForm = ref({
  last_name: '',
  first_name: '',
  email: '',
  birth_date: '',
  gender: '',
  mbti: '',
  personal_color: '',
  birth_hour: '',
  birth_minute: ''
})

const mbtiChoices = [
  'ISTJ', 'ISTP', 'ISFJ', 'ISFP',
  'INTJ', 'INTP', 'INFJ', 'INFP',
  'ESTP', 'ESTJ', 'ESFP', 'ESFJ',
  'ENTP', 'ENTJ', 'ENFP', 'ENFJ'
]

// 날짜 포맷팅 함수 (YYYY년 MM월 DD일)
const formatBirthDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}년 ${month}월 ${day}일`
}

// 태어난 시간 포맷팅 함수 (오전/오후 HH:MM 형식)
const formatBirthTime = (birthTime) => {
  if (!birthTime) return '미입력'

  // "HH:MM:SS" 또는 "HH:MM" 형식에서 시/분 추출
  const parts = birthTime.split(':')
  if (parts.length < 2) return birthTime

  const hour = parseInt(parts[0], 10)
  const minute = parts[1]

  const period = hour < 12 ? '오전' : '오후'
  const displayHour = hour === 0 ? 12 : (hour > 12 ? hour - 12 : hour)

  return `${period} ${String(displayHour).padStart(2, '0')}:${minute}`
}

// 성별 포맷팅
const formatGender = (gender) => {
  if (gender === 'M') return '남자'
  if (gender === 'F') return '여자'
  return '미입력'
}

// 퍼스널컬러 표시
const getPersonalColorDisplay = (value) => {
  const colorMap = {
    'spring_warm': '봄 웜톤',
    'summer_cool': '여름 쿨톤',
    'autumn_warm': '가을 웜톤',
    'winter_cool': '겨울 쿨톤'
  }
  return colorMap[value] || '미입력'
}

// 프로필 수정 모드로 전환
const editProfile = () => {
  // 기존 birth_time 파싱 (HH:MM:SS 또는 HH:MM 형식)
  let birthHour = ''
  let birthMinute = ''
  if (authStore.user?.birth_time) {
    const parts = authStore.user.birth_time.split(':')
    if (parts.length >= 2) {
      birthHour = parseInt(parts[0], 10)
      birthMinute = parseInt(parts[1], 10)
    }
  }

  // 현재 사용자 정보로 폼 초기화
  profileForm.value = {
    last_name: authStore.user?.last_name || '',
    first_name: authStore.user?.first_name || '',
    email: authStore.user?.email || '',
    birth_date: authStore.user?.birth_date || '',
    gender: authStore.user?.gender || '',
    mbti: authStore.user?.mbti || '',
    personal_color: authStore.user?.personal_color || '',
    birth_hour: birthHour,
    birth_minute: birthMinute
  }
  isEditing.value = true
}

// 수정 취소
const cancelEdit = () => {
  isEditing.value = false
}

// 변경사항 확인 함수
const hasChanges = () => {
  const user = authStore.user
  if (!user) return false

  // 기존 birth_time 파싱
  let originalHour = ''
  let originalMinute = ''
  if (user.birth_time) {
    const parts = user.birth_time.split(':')
    if (parts.length >= 2) {
      originalHour = parseInt(parts[0], 10)
      originalMinute = parseInt(parts[1], 10)
    }
  }

  // 각 필드 비교
  if ((profileForm.value.last_name || '') !== (user.last_name || '')) return true
  if ((profileForm.value.first_name || '') !== (user.first_name || '')) return true
  if ((profileForm.value.email || '') !== (user.email || '')) return true
  if ((profileForm.value.birth_date || '') !== (user.birth_date || '')) return true
  if ((profileForm.value.gender || '') !== (user.gender || '')) return true
  if ((profileForm.value.mbti || '') !== (user.mbti || '')) return true
  if ((profileForm.value.personal_color || '') !== (user.personal_color || '')) return true
  if (profileForm.value.birth_hour !== originalHour) return true
  if (profileForm.value.birth_minute !== originalMinute) return true

  return false
}

// 프로필 업데이트
const handleProfileUpdate = async () => {
  // 변경사항이 없으면 그냥 수정 모드 종료
  if (!hasChanges()) {
    isEditing.value = false
    return
  }

  // 시만 선택하고 분을 선택하지 않은 경우 분을 0으로 설정
  const formData = { ...profileForm.value }
  if (formData.birth_hour !== '' && formData.birth_minute === '') {
    formData.birth_minute = 0
  }

  try {
    const result = await authStore.updateProfile(formData)
    if (result?.success) {
      isEditing.value = false
      showToast('프로필이 업데이트되었습니다.', 'success')
    } else {
      // 에러 메시지 처리
      let errorMsg = '프로필 업데이트에 실패했습니다.'
      if (result?.error) {
        if (typeof result.error === 'string') {
          errorMsg = result.error
        } else if (typeof result.error === 'object') {
          // 객체인 경우 첫 번째 에러 메시지 추출
          const firstKey = Object.keys(result.error)[0]
          if (firstKey) {
            const msgs = result.error[firstKey]
            errorMsg = Array.isArray(msgs) ? msgs[0] : msgs
          }
        }
      }
      showToast(errorMsg, 'error')
    }
  } catch (error) {
    showToast(error.message || '프로필 업데이트에 실패했습니다.', 'error')
  }
}

// 컴포넌트 마운트 시 사용자 정보 새로고침
onMounted(() => {
  authStore.fetchUser()
})
</script>

<style scoped>
/* Django 템플릿과 동일한 스타일 유지 */

.glass-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
}

.glass-input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: #7c3aed;
  color: #fff;
  box-shadow: 0 0 0 0.2rem rgba(124, 58, 237, 0.25);
}

.table-borderless th,
.table-borderless td {
  color: #fff;
  padding: 0.5rem 0;
}

.table-borderless th {
  font-weight: 600;
}

h5 {
  color: #fff;
  margin-bottom: 1rem;
  font-weight: 600;
}

.btn-outline-secondary {
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.btn-outline-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff;
}

/* Responsive Padding Utilities - Strictly matching Today.vue */
.responsive-padding {
  padding: 3rem !important; /* Desktop Default */
}

@media (max-width: 768px) {
  /* Percentage based padding for mobile */
  .responsive-padding {
    padding: 3% !important; /* Minimized padding */
  }
}
</style>
