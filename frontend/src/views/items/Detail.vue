<template>
  <DefaultLayout>
    <div class="page-container">
      <div class="content-wrapper">
        <!-- 페이지 헤더 -->
        <div class="page-header">
          <h1 class="page-title">
            <i class="fas fa-search text-primary"></i>
            아이템 상세 분석
          </h1>
          <p class="page-subtitle">AI가 분석한 아이템의 상세 정보입니다</p>
        </div>

        <div v-if="item" class="card-base card-lg">
          <div class="row g-0">
            <div class="col-md-5">
              <img
                v-if="item.image"
                :src="item.image"
                class="img-fluid rounded-start h-100"
                :alt="item.item_name"
                style="object-fit: cover; min-height: 400px;"
              >
              <div
                v-else
                class="d-flex align-items-center justify-content-center h-100 bg-light"
                style="min-height: 400px;"
              >
                <span class="text-muted">이미지 없음</span>
              </div>
            </div>
            <div class="col-md-7">
              <div class="card-body p-4">
                <!-- 아이템 이름 (수정 모드) -->
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div v-if="isEditing" class="flex-grow-1 me-2">
                    <input
                      v-model="editForm.item_name"
                      type="text"
                      class="form-control form-control-lg fw-bold"
                      placeholder="아이템 이름"
                    >
                  </div>
                  <h2 v-else class="card-title fw-bold mb-0">{{ item.item_name }}</h2>
                  <div class="d-flex align-items-center gap-2">
                    <button
                      v-if="!isEditing"
                      class="btn btn-sm btn-outline-secondary"
                      @click="startEditing"
                      title="수정"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <span v-if="item.is_favorite" class="text-warning">
                      <i class="fas fa-star fa-lg"></i>
                    </span>
                  </div>
                </div>

                <!-- 카테고리 (수정 모드) -->
                <div v-if="isEditing" class="mb-4">
                  <label class="form-label text-muted small">카테고리</label>
                  <select v-model="editForm.main_category" class="form-select">
                    <option value="clothing">의류</option>
                    <option value="cosmetics">화장품</option>
                    <option value="electronics">전자제품</option>
                    <option value="accessories">악세서리</option>
                    <option value="etc">기타</option>
                  </select>
                </div>
                <p v-else class="text-muted mb-4">
                  <span class="badge bg-secondary me-2">{{ item.category_display }}</span>
                  <small>{{ formatDate(item.created_at) }} 등록</small>
                </p>

                <!-- 수정 버튼들 -->
                <div v-if="isEditing" class="d-flex gap-2 mb-4">
                  <button class="btn btn-primary" @click="saveEdit" :disabled="isSaving">
                    <i class="fas fa-check me-1"></i> 저장
                  </button>
                  <button class="btn btn-outline-secondary" @click="cancelEdit">
                    <i class="fas fa-times me-1"></i> 취소
                  </button>
                </div>

                <hr class="my-4">

                <!-- 행운도 측정 버튼 -->
                <div class="alert mb-4 text-center" style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.15), rgba(59, 130, 246, 0.15)); border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 15px;">
                  <h6 class="mb-2"><i class="fas fa-magic text-primary me-2"></i>오늘의 행운도 측정</h6>
                  <small class="text-muted d-block mb-3">오늘의 행운과 얼마나 맞는지 확인하세요</small>
                  <button class="btn btn-primary rounded-pill px-4" @click="checkLuck">
                    <i class="fas fa-star me-1"></i> 행운 체크
                  </button>
                </div>

                <!-- 주요 색상 -->
                <h5 class="fw-bold mb-3"><i class="fas fa-palette text-primary"></i> 주요 색상</h5>
                <div v-if="item.dominant_colors && item.dominant_colors.length > 0" class="mb-4">
                  <div
                    v-for="(color, index) in item.dominant_colors"
                    :key="index"
                    class="d-flex align-items-center mb-2"
                  >
                    <div
                      class="rounded-circle border me-3"
                      :style="{
                        width: '30px',
                        height: '30px',
                        backgroundColor: color.hex
                      }"
                    ></div>
                    <div>
                      <span class="fw-bold">{{ color.korean_name }}</span>
                      <small class="text-muted ms-2">({{ color.hex }})</small>
                    </div>
                  </div>
                </div>
                <p v-else class="text-muted mb-4">분석된 색상 정보가 없습니다.</p>

                <!-- AI 분석 결과 - 해시태그만 표시 -->
                <div v-if="aiAnalysis.tags && aiAnalysis.tags.length > 0" class="mb-4">
                  <h5 class="fw-bold mb-3"><i class="fas fa-robot text-success"></i> AI 분석 결과</h5>
                  <div class="d-flex flex-wrap gap-2">
                    <span
                      v-for="(tag, index) in aiAnalysis.tags.slice(0, 4)"
                      :key="index"
                      class="badge rounded-pill"
                      style="background: rgba(124, 58, 237, 0.3); color: #c4b5fd; font-size: 0.9rem; padding: 10px 16px;"
                    >
                      #{{ tag }}
                    </span>
                  </div>
                </div>

                <div class="d-grid gap-3 mt-4">
                  <router-link to="/items" class="btn btn-outline-light rounded-pill py-2">
                    <i class="fas fa-list me-2"></i> 목록으로 돌아가기
                  </router-link>
                  <button class="btn btn-outline-danger rounded-pill py-2" @click="handleDelete">
                    <i class="fas fa-trash me-2"></i> 삭제하기
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-else class="card-base card-lg">
          <div class="empty-state">
            <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="empty-text">아이템 정보를 불러오는 중...</p>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'
import { colorMap, getTextColor } from '@/utils/colors'

const route = useRoute()
const router = useRouter()
const item = ref(null)
const isEditing = ref(false)
const isSaving = ref(false)
const editForm = ref({
  item_name: '',
  main_category: ''
})

// 카테고리 한글 매핑
const categoryDisplayMap = {
  'clothing': '의류',
  'cosmetics': '화장품',
  'electronics': '전자제품',
  'accessories': '악세서리',
  'etc': '기타'
}

// AI 분석 결과 computed
const aiAnalysis = computed(() => {
  if (!item.value) return {}
  return item.value.ai_analysis_result || item.value.ai_analysis || {}
})

// 색상 hex 값 가져오기
const getColorHex = (colorName) => {
  return colorMap[colorName] || '#6c757d'
}

// 배경색에 따른 텍스트 색상
const getTextColorForBg = (colorName) => {
  const hex = colorMap[colorName] || '#6c757d'
  return getTextColor(hex)
}

const fetchItemDetail = async () => {
  try {
    const itemId = route.params.id
    const response = await api.get(`/api/items/${itemId}/`)
    // API 응답 구조: { success: true, item: {...} }
    const itemData = response.data.item || response.data
    // category_display 추가
    itemData.category_display = categoryDisplayMap[itemData.main_category] || itemData.main_category || '기타'
    // image 필드 매핑 (image_url -> image)
    if (!itemData.image && itemData.image_url) {
      itemData.image = itemData.image_url
    }
    item.value = itemData
  } catch (error) {
    console.error('아이템 상세 정보 가져오기 실패:', error)
    alert('아이템을 찾을 수 없습니다.')
    router.push('/items')
  }
}

// 수정 모드 시작
const startEditing = () => {
  editForm.value = {
    item_name: item.value.item_name,
    main_category: item.value.main_category || 'etc'
  }
  isEditing.value = true
}

// 수정 취소
const cancelEdit = () => {
  isEditing.value = false
  editForm.value = { item_name: '', main_category: '' }
}

// 수정 저장
const saveEdit = async () => {
  if (!editForm.value.item_name.trim()) {
    alert('아이템 이름을 입력해주세요.')
    return
  }

  isSaving.value = true
  try {
    const response = await api.put(`/api/items/${item.value.id}/`, {
      item_name: editForm.value.item_name,
      main_category: editForm.value.main_category
    })

    if (response.data.success) {
      // 로컬 데이터 업데이트
      item.value.item_name = editForm.value.item_name
      item.value.main_category = editForm.value.main_category
      item.value.category_display = categoryDisplayMap[editForm.value.main_category] || '기타'
      isEditing.value = false
      alert('수정되었습니다.')
    } else {
      alert(response.data.message || '수정 중 오류가 발생했습니다.')
    }
  } catch (error) {
    console.error('수정 실패:', error)
    alert('수정 중 오류가 발생했습니다.')
  } finally {
    isSaving.value = false
  }
}

// 행운도 측정 페이지로 이동
const checkLuck = () => {
  // 아이템 정보를 sessionStorage에 저장하고 행운 체크 페이지로 이동
  sessionStorage.setItem('checkLuckItem', JSON.stringify({
    id: item.value.id,
    item_name: item.value.item_name,
    image: item.value.image,
    dominant_colors: item.value.dominant_colors,
    ai_analysis: item.value.ai_analysis_result || item.value.ai_analysis
  }))
  router.push('/fortune/item-check')
}

const handleDelete = async () => {
  if (!confirm('정말 이 아이템을 삭제하시겠습니까?')) {
    return
  }

  try {
    const response = await api.delete(`/api/items/${item.value.id}/delete/`)
    if (response.data.success) {
      alert('삭제되었습니다.')
      router.push('/items')
    } else {
      alert(response.data.message || '삭제 중 오류가 발생했습니다.')
    }
  } catch (error) {
    console.error('삭제 실패:', error)
    alert('삭제 중 오류가 발생했습니다.')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '날짜 정보 없음'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '날짜 정보 없음'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}.${month}.${day} ${hour}:${minute}`
}

onMounted(() => {
  fetchItemDetail()
})
</script>
