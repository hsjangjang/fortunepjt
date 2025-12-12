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
                  style="border-style: dashed !important; cursor: pointer;"
                  @click="triggerFileInput"
                  @dragenter.prevent="handleDragEnter"
                  @dragover.prevent="handleDragOver"
                  @dragleave.prevent="handleDragLeave"
                  @drop.prevent="handleDrop"
                >
                  <!-- 이미지 미리보기 -->
                  <div v-if="imagePreview" class="preview-container">
                    <img :src="imagePreview" alt="미리보기" class="preview-image">
                    <p class="text-primary small mt-2 mb-0">클릭하여 다른 이미지 선택</p>
                  </div>
                  <!-- 기본 업로드 안내 -->
                  <div v-else>
                    <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                    <p class="text-muted mb-0">이미지를 드래그하거나 클릭하여 업로드</p>
                  </div>
                  <input
                    ref="fileInput"
                    type="file"
                    class="form-control d-none"
                    accept="image/*"
                    required
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
                  <option value="cosmetics">화장품</option>
                  <option value="electronics">전자제품</option>
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

              <div class="form-check mb-3">
                <input
                  v-model="formData.is_favorite"
                  class="form-check-input"
                  type="checkbox"
                  id="favorite"
                >
                <label class="form-check-label" for="favorite">
                  즐겨찾기에 추가
                </label>
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
              <router-link to="/items" class="btn btn-outline-primary">
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
const fileName = ref('')
const imagePreview = ref(null)
const isUploading = ref(false)

const formData = ref({
  item_name: '',
  main_category: '',
  sub_category: '',
  custom_category: '',
  is_favorite: false,
  image: null
})

const subCategoryMap = {
  'clothing': ['상의', '하의', '아우터', '원피스', '신발', '가방'],
  'cosmetics': ['스킨케어', '메이크업', '헤어'],
  'electronics': ['스마트폰', '태블릿', '노트북', '이어폰', '기타'],
  'accessories': ['귀걸이', '목걸이', '반지', '팔찌', '지갑'],
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

      // 이미지 미리보기 설정 (base64)
      if (data.imagePreview) {
        imagePreview.value = data.imagePreview
      }
    } catch (e) {
      console.error('ItemCheck 데이터 파싱 실패:', e)
    }
  }
})

const handleSubmit = async () => {
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

  isUploading.value = true

  try {
    const data = new FormData()
    data.append('image', formData.value.image)
    data.append('item_name', formData.value.item_name)
    data.append('main_category', formData.value.main_category)
    data.append('category', formData.value.main_category) // 하위 호환성
    data.append('is_favorite', formData.value.is_favorite)

    if (formData.value.main_category === 'etc') {
      data.append('custom_category', formData.value.custom_category)
    } else if (formData.value.sub_category) {
      data.append('sub_category', formData.value.sub_category)
    }

    const response = await api.post('/api/items/', data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      alert('아이템이 성공적으로 업로드되었습니다!')
      router.push('/items')
    }
  } catch (error) {
    console.error('업로드 실패:', error)
    alert('업로드 중 오류가 발생했습니다.')
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
}
</style>
