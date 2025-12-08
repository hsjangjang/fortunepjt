<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-8 mx-auto">
        <div class="card mb-4">
          <div class="card-body text-center py-4">
            <h1 class="display-5 mb-3">
              <i class="fas fa-search text-primary"></i> 아이템 상세 분석
            </h1>
            <p class="lead text-muted">AI가 분석한 아이템의 상세 정보입니다</p>
          </div>
        </div>

        <div v-if="item" class="card shadow-sm">
          <div class="row g-0">
            <div class="col-md-6">
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
            <div class="col-md-6">
              <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <h2 class="card-title fw-bold mb-0">{{ item.item_name }}</h2>
                  <span v-if="item.is_favorite" class="text-warning">
                    <i class="fas fa-star fa-lg"></i>
                  </span>
                </div>

                <p class="text-muted mb-4">
                  <span class="badge bg-secondary me-2">{{ item.category_display }}</span>
                  <small>{{ formatDate(item.created_at) }} 등록</small>
                </p>

                <hr class="my-4">

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

                <div v-if="item.ai_analysis_result && item.ai_analysis_result.tags">
                  <h5 class="fw-bold mb-3"><i class="fas fa-robot text-success"></i> AI 분석 태그</h5>
                  <div class="mb-4">
                    <span
                      v-for="(tag, index) in item.ai_analysis_result.tags"
                      :key="index"
                      class="badge bg-light text-dark border me-1 mb-1"
                    >
                      #{{ tag }}
                    </span>
                  </div>
                </div>

                <div class="d-grid gap-2 mt-5">
                  <router-link to="/items" class="btn btn-outline-primary">
                    <i class="fas fa-list"></i> 목록으로 돌아가기
                  </router-link>
                  <button class="btn btn-outline-danger" @click="handleDelete">
                    <i class="fas fa-trash"></i> 삭제하기
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-else class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3 text-muted">아이템 정보를 불러오는 중...</p>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const item = ref(null)

const fetchItemDetail = async () => {
  try {
    const itemId = route.params.id
    const response = await api.get(`/api/items/${itemId}/`)
    item.value = response.data
  } catch (error) {
    console.error('아이템 상세 정보 가져오기 실패:', error)
    alert('아이템을 찾을 수 없습니다.')
    router.push('/items')
  }
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
  const date = new Date(dateString)
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
