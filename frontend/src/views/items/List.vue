<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-10 mx-auto">
        <div class="card mb-4">
          <div class="card-body text-center py-4">
            <h1 class="display-5">
              <i class="fas fa-closet text-primary"></i> 내 아이템
            </h1>
            <p class="lead text-muted">업로드한 아이템과 행운색 매칭도를 확인하세요</p>
          </div>
        </div>

        <div v-if="!authStore.isAuthenticated" class="alert alert-warning text-center p-4" role="alert">
          <div class="mb-3">
            <i class="fas fa-lock fa-3x text-warning"></i>
          </div>
          <h5 class="mb-3">
            <i class="fas fa-lock"></i> 로그인 후 이용해주세요
          </h5>
          <p class="mb-3">내 아이템 서비스는 회원 전용 기능입니다.</p>
          <hr>
          <p class="mb-0 text-muted">
            상단 메뉴에서 <strong>로그인</strong> 또는 <strong>회원가입</strong>을 해주세요.
          </p>
        </div>

        <template v-else>
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5>총 {{ items.length }}개 아이템</h5>
            <router-link to="/items/upload" class="btn btn-primary">
              <i class="fas fa-plus"></i> 아이템 추가
            </router-link>
          </div>

          <div v-if="items.length > 0" class="row">
            <div v-for="item in items" :key="item.id" class="col-md-4 mb-4">
              <div class="card h-100 item-card border-0">
                <div class="position-relative">
                  <router-link :to="`/items/${item.id}`">
                    <img
                      :src="getImageUrl(item.image)"
                      class="card-img-top"
                      :alt="item.item_name"
                      style="height: 200px; object-fit: cover; border-radius: 12px 12px 0 0;"
                    >
                  </router-link>
                  <!-- 삭제 버튼 - 이미지 우상단 -->
                  <button
                    class="btn-delete"
                    @click.stop="deleteItem(item.id)"
                    title="삭제"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <router-link
                  :to="`/items/${item.id}`"
                  class="text-decoration-none h-100 d-flex flex-column"
                >
                  <div class="card-body flex-grow-1">
                    <h5 class="card-title text-white mb-1">{{ item.item_name }}</h5>
                    <p class="card-text small mb-2" style="color: rgba(255,255,255,0.5);">{{ item.category_display }}</p>

                    <!-- 색상 태그 -->
                    <div v-if="item.dominant_colors && item.dominant_colors.length > 0" class="mb-2">
                      <span
                        v-for="(color, index) in item.dominant_colors.slice(0, 3)"
                        :key="index"
                        class="badge rounded-pill me-1"
                        :style="{
                          backgroundColor: color.hex,
                          color: (color.name === 'white' || color.name === 'yellow') ? '#000' : '#fff',
                          border: '1px solid rgba(255,255,255,0.2)'
                        }"
                      >
                        {{ color.korean_name }}
                      </span>
                    </div>
                    <!-- AI 분석 태그 -->
                    <div v-if="item.ai_analysis && item.ai_analysis.tags && item.ai_analysis.tags.length > 0" class="mb-2">
                      <span
                        v-for="(tag, index) in item.ai_analysis.tags.slice(0, 3)"
                        :key="'tag-' + index"
                        class="badge me-1"
                        style="background: rgba(124, 58, 237, 0.3); color: #c4b5fd;"
                      >
                        #{{ tag }}
                      </span>
                    </div>
                    <!-- 날짜 -->
                    <div class="mt-auto pt-2">
                      <small style="color: rgba(255,255,255,0.4);">{{ formatDate(item.created_at) }}</small>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>

          <!-- 아이템이 없을 때 -->
          <div v-else class="card">
            <div class="card-body text-center py-5">
              <i class="fas fa-camera fa-5x text-muted mb-3"></i>
              <h4>아직 업로드한 아이템이 없습니다</h4>
              <p class="text-muted">첫 번째 아이템을 업로드하고 행운색 매칭도를 확인해보세요!</p>
              <router-link to="/items/upload" class="btn btn-primary">
                <i class="fas fa-upload"></i> 첫 아이템 업로드하기
              </router-link>
            </div>
          </div>
        </template>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'
import { API_BASE_URL } from '@/config/api'

const authStore = useAuthStore()
const items = ref([])

// 이미지 URL에 base URL 추가
const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}

const fetchItems = async () => {
  try {
    const response = await api.get('/api/items/')
    items.value = response.data.items || []
  } catch (error) {
    console.error('아이템 목록 가져오기 실패:', error)
  }
}

const deleteItem = async (itemId) => {
  if (!confirm('정말 이 아이템을 삭제하시겠습니까?')) {
    return
  }

  try {
    const response = await api.delete(`/api/items/${itemId}/`)
    if (response.data.success) {
      // 목록에서 제거
      items.value = items.value.filter(item => item.id !== itemId)
      alert('삭제되었습니다.')
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
  return `${year}.${month}.${day}`
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchItems()
  }
})
</script>

<style scoped>
.item-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.item-card .card-body {
  background: rgba(30, 41, 59, 0.8);
}

.btn-delete {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
}

.btn-delete:hover {
  background: rgba(239, 68, 68, 0.9);
  color: #fff;
  transform: scale(1.1);
}
</style>
