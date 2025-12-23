<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-6 mx-auto">
        <div class="card">
          <div class="card-body p-5">
            <h2 class="text-center mb-4">
              <i class="fas fa-camera text-warning"></i> 아이템 업로드
            </h2>

            <div v-if="!authStore.isAuthenticated" class="alert alert-warning" role="alert">
              <i class="fas fa-exclamation-triangle"></i>
              아이템 업로드는 로그인 후 이용 가능합니다.
              <router-link to="/login" class="alert-link">로그인하기</router-link>
            </div>

            <form v-else @submit.prevent="handleSubmit" id="uploadForm">
              <div class="mb-4">
                <label class="form-label">아이템 이미지</label>
                <div
                  ref="uploadArea"
                  class="upload-area border rounded text-center"
                  :class="imagePreview ? 'p-3' : 'p-5'"
                  style="border-style: dashed !important;"
                  @dragenter.prevent="handleDragEnter"
                  @dragover.prevent="handleDragOver"
                  @dragleave.prevent="handleDragLeave"
                  @drop.prevent="handleDrop"
                >
                  <!-- 이미지 미리보기 -->
                  <div v-if="imagePreview" class="preview-container" @click="triggerFileInput" style="cursor: pointer;">
                    <img :src="imagePreview" alt="미리보기" class="preview-image">
                    <p class="text-primary small mt-2 mb-0">클릭하여 다른 이미지 선택</p>
                  </div>
                  <!-- 기본 업로드 안내 -->
                  <div v-else>
                    <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                    <p class="text-muted mb-3">아이템 사진을 업로드하세요</p>
                    <p class="small text-muted">JPG, PNG 파일 (최대 10MB)</p>

                    <!-- 카메라/갤러리 선택 버튼 -->
                    <div class="d-flex gap-2 justify-content-center mt-3 flex-nowrap">
                      <button type="button" class="btn btn-primary px-3 upload-btn" @click="openCamera">
                        <i class="fas fa-camera"></i> 카메라
                      </button>
                      <button type="button" class="btn btn-primary px-3 upload-btn" @click="openGallery">
                        <i class="fas fa-image"></i> 갤러리
                      </button>
                    </div>

                    <!-- 드래그 앤 드롭 안내 (데스크톱용) -->
                    <p class="text-muted small mt-3 mb-0 d-none d-md-block">또는 이미지를 드래그하여 업로드</p>
                  </div>
                  <input
                    ref="fileInput"
                    type="file"
                    class="form-control d-none"
                    accept="image/*"
                    @change="handleFileChange"
                  >
                  <input
                    ref="cameraInput"
                    type="file"
                    class="form-control d-none"
                    accept="image/*"
                    capture="environment"
                    @change="handleFileChange"
                  >
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">아이템 이름</label>
                <input v-model="formData.item_name" type="text" class="form-control" required>
              </div>

              <div class="mb-3">
                <label class="form-label">대분류</label>
                <select v-model="formData.main_category" class="form-select" required>
                  <option value="">선택하세요</option>
                  <option value="clothing">의류</option>
                  <option value="accessories">악세서리</option>
                  <option value="etc">기타</option>
                </select>
              </div>

              <!-- 소분류 -->
              <div v-if="showSubCategory" class="mb-3">
                <label class="form-label">소분류</label>
                <div>
                  <div v-for="sub in currentSubCategories" :key="sub" class="form-check">
                    <input
                      class="form-check-input"
                      type="radio"
                      name="sub_category"
                      :value="sub"
                      :id="'sub_' + sub"
                      v-model="formData.sub_category"
                    >
                    <label class="form-check-label" :for="'sub_' + sub">
                      {{ sub }}
                    </label>
                  </div>
                </div>
              </div>

              <!-- 기타 - 직접 입력 -->
              <div v-if="formData.main_category === 'etc'" class="mb-3">
                <label class="form-label">카테고리 직접 입력</label>
                <input
                  v-model="formData.custom_category"
                  type="text"
                  class="form-control"
                  placeholder="예: 텀블러, 키링, 파우치 등"
                  :required="formData.main_category === 'etc'"
                >
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg">
                  <i class="fas fa-upload"></i> 업로드 및 색상 분석
                </button>
              </div>
            </form>

            <hr v-if="authStore.isAuthenticated" class="my-4">

            <div v-if="authStore.isAuthenticated" class="text-center">
              <p class="text-muted">업로드한 아이템의 색상을 분석하여<br>오늘의 행운색과 매칭도를 계산합니다</p>
              <router-link to="/mypage" class="btn btn-outline-primary">
                내 아이템 보기
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isUploading" class="loading-overlay">
      <div class="spinner-border text-light mb-3" role="status" style="width: 3rem; height: 3rem;">
        <span class="visually-hidden">Loading...</span>
      </div>
      <h4 class="fw-bold">업로드 및 분석 중...</h4>
      <p>잠시만 기다려주세요</p>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const fromItemCheck = ref(false)

const uploadArea = ref(null)
const fileInput = ref(null)
const cameraInput = ref(null)
const fileName = ref('')
const imagePreview = ref(null)
const isUploading = ref(false)

const formData = ref({
  item_name: '',
  main_category: '',
  sub_category: '',
  custom_category: '',
  image: null
})

const subCategoryMap = {
  'clothing': ['상의', '하의', '아우터', '원피스', '신발', '가방', '기타'],
  'accessories': ['귀걸이', '목걸이', '반지', '팔찌', '지갑', '기타'],
  'etc': []
}

const currentSubCategories = computed(() => {
  return subCategoryMap[formData.value.main_category] || []
})

const showSubCategory = computed(() => {
  return formData.value.main_category &&
         formData.value.main_category !== 'etc' &&
         currentSubCategories.value.length > 0
})

// 대분류 변경 시 소분류 초기화
watch(() => formData.value.main_category, () => {
  formData.value.sub_category = ''
  formData.value.custom_category = ''
})

const triggerFileInput = () => {
  fileInput.value.click()
}

const openCamera = () => {
  cameraInput.value.click()
}

const openGallery = () => {
  fileInput.value.click()
}

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    formData.value.image = file
    fileName.value = `선택된 파일: ${file.name}`

    // 이미지 미리보기 생성
    const reader = new FileReader()
    reader.onload = (event) => {
      imagePreview.value = event.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleDragEnter = (e) => {
  uploadArea.value.classList.add('bg-light')
  uploadArea.value.style.borderColor = '#7c3aed'
}

const handleDragOver = (e) => {
  uploadArea.value.classList.add('bg-light')
  uploadArea.value.style.borderColor = '#7c3aed'
}

const handleDragLeave = (e) => {
  uploadArea.value.classList.remove('bg-light')
  uploadArea.value.style.borderColor = '#dee2e6'
}

const handleDrop = (e) => {
  uploadArea.value.classList.remove('bg-light')
  uploadArea.value.style.borderColor = '#dee2e6'

  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    formData.value.image = file
    fileName.value = `선택된 파일: ${file.name}`
    // Update file input
    const dataTransfer = new DataTransfer()
    dataTransfer.items.add(file)
    fileInput.value.files = dataTransfer.files

    // 이미지 미리보기 생성
    const reader = new FileReader()
    reader.onload = (event) => {
      imagePreview.value = event.target.result
    }
    reader.readAsDataURL(file)
  }
}

// base64를 File 객체로 변환하는 함수
const base64ToFile = (base64String, filename) => {
  // base64 데이터에서 mime type과 데이터 부분 분리
  const arr = base64String.split(',')
  const mimeMatch = arr[0].match(/:(.*?);/)
  const mime = mimeMatch ? mimeMatch[1] : 'image/jpeg'
  const bstr = atob(arr[1])
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n)
  }
  return new File([u8arr], filename, { type: mime })
}

// ItemCheck에서 넘어온 데이터 처리
onMounted(() => {
  const itemCheckData = sessionStorage.getItem('itemCheckData')
  if (itemCheckData) {
    try {
      const data = JSON.parse(itemCheckData)
      sessionStorage.removeItem('itemCheckData')
      fromItemCheck.value = true

      // AI가 감지한 아이템 이름 설정
      if (data.itemName && data.itemName !== '분석 중...' && data.itemName !== '알 수 없음') {
        formData.value.item_name = data.itemName
      }

      // 이미지 미리보기 설정 및 File 객체 생성 (base64)
      if (data.imagePreview) {
        imagePreview.value = data.imagePreview
        // base64를 File 객체로 변환하여 formData에 설정
        const file = base64ToFile(data.imagePreview, `item_${Date.now()}.jpg`)
        formData.value.image = file
        fileName.value = `선택된 파일: ${file.name}`
      }
    } catch (e) {
      console.error('ItemCheck 데이터 파싱 실패:', e)
    }
  }
})

const handleSubmit = async () => {
  // 이미지 필수 체크
  if (!formData.value.image) {
    alert('이미지를 선택해주세요.')
    return
  }

  // 아이템 이름 필수 체크
  if (!formData.value.item_name || !formData.value.item_name.trim()) {
    alert('아이템 이름을 입력해주세요.')
    return
  }

  // 대분류 필수 체크
  if (!formData.value.main_category) {
    alert('대분류를 선택해주세요.')
    return
  }

  // 소분류 검증
  if (formData.value.main_category &&
      formData.value.main_category !== 'etc' &&
      formData.value.main_category !== '' &&
      currentSubCategories.value.length > 0) {
    if (!formData.value.sub_category) {
      alert('소분류를 선택해주세요.')
      return
    }
  }

  // 기타 카테고리인 경우 직접 입력 필수 체크
  if (formData.value.main_category === 'etc' && !formData.value.custom_category?.trim()) {
    alert('카테고리를 직접 입력해주세요.')
    return
  }

  isUploading.value = true

  try {
    const data = new FormData()
    data.append('image', formData.value.image)
    data.append('item_name', formData.value.item_name.trim())
    data.append('main_category', formData.value.main_category)

    // sub_categories 배열로 전송 (백엔드 기대 형식)
    if (formData.value.main_category === 'etc') {
      // 기타 카테고리: custom_category를 sub_categories 배열에 추가
      data.append('sub_categories', formData.value.custom_category.trim())
    } else if (formData.value.sub_category) {
      // 일반 소분류 선택
      data.append('sub_categories', formData.value.sub_category)
    }

    const response = await api.post('/api/items/', data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      alert('아이템이 성공적으로 업로드되었습니다!')
      router.push('/mypage')
    } else {
      // 서버에서 success: false 응답
      alert(response.data.error || '업로드에 실패했습니다.')
    }
  } catch (error) {
    console.error('업로드 실패:', error)

    // 상세 에러 메시지 표시
    if (error.response) {
      // 서버 응답 에러
      const status = error.response.status
      const errorData = error.response.data

      if (status === 401) {
        alert('로그인이 필요합니다. 다시 로그인해주세요.')
        router.push('/login')
      } else if (status === 503 || errorData?.error_type === 'quota_exceeded') {
        alert('AI 분석 서비스가 일시적으로 제한되었습니다. 잠시 후 다시 시도해주세요.')
      } else if (status >= 500) {
        alert('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
      } else {
        alert(errorData?.error || '업로드 중 오류가 발생했습니다.')
      }
    } else if (error.request) {
      // 네트워크 에러 (서버 응답 없음)
      alert('서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요.')
    } else {
      alert('업로드 중 오류가 발생했습니다.')
    }
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
}

.preview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .preview-image {
    max-height: 180px;
  }

  /* 모바일에서 업로드 버튼 스타일 */
  .upload-btn {
    font-size: 0.8rem;
    padding: 0.5rem 1rem !important;
    border-radius: 50px;
    white-space: nowrap;
  }

  .upload-btn i {
    margin-right: 0.25rem;
  }
}
</style>
