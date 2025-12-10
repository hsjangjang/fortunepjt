<template>
  <DefaultLayout>
    <div class="page-container">
      <div class="content-wrapper wide">
        <!-- 페이지 헤더 -->
        <div class="page-header">
          <h1 class="page-title">
            <i class="fas fa-box-open text-primary"></i>
            내 아이템
          </h1>
          <p class="page-subtitle">업로드한 아이템과 행운색 매칭도를 확인하세요</p>
        </div>

        <div v-if="!authStore.isAuthenticated" class="card-base card-lg text-center">
          <div class="empty-state">
            <i class="fas fa-lock empty-icon" style="color: #fbbf24;"></i>
            <h3 class="empty-title">로그인 후 이용해주세요</h3>
            <p class="empty-text">내 아이템 서비스는 회원 전용 기능입니다.<br>상단 메뉴에서 로그인 또는 회원가입을 해주세요.</p>
          </div>
        </div>

        <template v-else>
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5>총 {{ items.length }}개 아이템</h5>
            <router-link to="/items/upload" class="btn btn-primary">
              <i class="fas fa-plus"></i> 아이템 추가
            </router-link>
          </div>

          <div v-if="items.length > 0" class="row g-2 g-md-4">
            <div v-for="item in items" :key="item.id" class="col-4 col-md-4 mb-2 mb-md-4">
              <div class="card h-100 item-card border-0" :class="{ 'top-luck-item': item.id === topLuckItemId }">
                <!-- 최고 행운 배지 -->
                <div v-if="item.id === topLuckItemId" class="top-luck-badge">
                  <i class="fas fa-crown"></i> <span class="d-none d-md-inline">오늘의 행운</span>
                </div>
                <div class="position-relative">
                  <router-link :to="`/items/${item.id}`">
                    <img
                      :src="getImageUrl(item.image)"
                      class="card-img-top item-image"
                      :alt="item.item_name"
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
                  <div class="card-body flex-grow-1 d-flex flex-column item-body">
                    <h5 class="card-title text-white mb-1 mb-md-2 item-name">{{ item.item_name }}</h5>

                    <!-- 색상 태그 - 모바일에서 숨김 -->
                    <div v-if="item.dominant_colors && item.dominant_colors.length > 0" class="mb-1 mb-md-2 d-none d-md-block">
                      <span
                        v-for="(color, index) in item.dominant_colors.slice(0, 1)"
                        :key="index"
                        class="badge rounded-pill"
                        :style="{
                          backgroundColor: color.hex,
                          color: (color.name === 'white' || color.name === 'yellow') ? '#000' : '#fff',
                          border: '1px solid rgba(255,255,255,0.2)'
                        }"
                      >
                        {{ color.korean_name }}
                      </span>
                    </div>

                    <!-- AI 분석 태그 - 모바일에서 숨김 -->
                    <div v-if="item.ai_analysis && item.ai_analysis.tags && item.ai_analysis.tags.length > 0" class="mb-3 d-none d-md-block">
                      <span
                        v-for="(tag, index) in item.ai_analysis.tags.slice(0, 3)"
                        :key="'tag-' + index"
                        class="badge me-1"
                        style="background: rgba(124, 58, 237, 0.3); color: #c4b5fd;"
                      >
                        #{{ tag }}
                      </span>
                    </div>

                    <!-- 게임 스탯 스타일 운세 영향도 - 모바일에서 숨김 -->
                    <div class="mt-auto stat-section d-none d-md-block">
                      <div class="stat-row">
                        <span class="stat-label"><i class="fas fa-palette"></i> 색상</span>
                        <div class="stat-bar-container">
                          <div class="stat-bar" :style="{ width: getColorStat(item) + '%', background: 'linear-gradient(90deg, #a78bfa, #7c3aed)' }"></div>
                        </div>
                        <span class="stat-value">{{ getColorStat(item) }}</span>
                      </div>
                      <div class="stat-row">
                        <span class="stat-label"><i class="fas fa-star"></i> 행운</span>
                        <div class="stat-bar-container">
                          <div class="stat-bar" :style="{ width: getLuckStat(item) + '%', background: 'linear-gradient(90deg, #fbbf24, #f59e0b)' }"></div>
                        </div>
                        <span class="stat-value">{{ getLuckStat(item) }}</span>
                      </div>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>

          <!-- 아이템이 없을 때 -->
          <div v-else class="card-base card-lg">
            <div class="empty-state">
              <i class="fas fa-camera empty-icon"></i>
              <h3 class="empty-title">아직 업로드한 아이템이 없습니다</h3>
              <p class="empty-text">첫 번째 아이템을 업로드하고 행운색 매칭도를 확인해보세요!</p>
              <router-link to="/items/upload" class="btn btn-primary btn-lg rounded-pill px-5">
                <i class="fas fa-upload me-2"></i> 첫 아이템 업로드하기
              </router-link>
            </div>
          </div>
        </template>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'
import { API_BASE_URL } from '@/config/api'

const authStore = useAuthStore()
const items = ref([])

// 최고 행운 아이템 ID 계산
const topLuckItemId = computed(() => {
  if (items.value.length === 0) return null
  let maxLuck = -1
  let topId = null
  items.value.forEach(item => {
    const luck = getLuckStat(item)
    if (luck > maxLuck) {
      maxLuck = luck
      topId = item.id
    }
  })
  return topId
})

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

// 색상 스탯 계산 (색상 다양성 기준)
const getColorStat = (item) => {
  if (!item.dominant_colors || item.dominant_colors.length === 0) return 50
  // 색상 개수와 다양성에 따라 스탯 계산
  const colorCount = item.dominant_colors.length
  const baseStat = Math.min(colorCount * 25 + 25, 100)
  // 약간의 랜덤성 추가 (아이템 ID 기반으로 일관된 값)
  const variation = (item.id % 20) - 10
  return Math.max(30, Math.min(100, baseStat + variation))
}

// 행운 스탯 계산 (AI 분석 결과 기준)
const getLuckStat = (item) => {
  let stat = 50
  if (item.ai_analysis) {
    if (item.ai_analysis.tags && item.ai_analysis.tags.length > 0) {
      stat += item.ai_analysis.tags.length * 8
    }
    if (item.ai_analysis.matching_colors && item.ai_analysis.matching_colors.length > 0) {
      stat += item.ai_analysis.matching_colors.length * 5
    }
  }
  // 아이템 ID 기반 변동
  const variation = ((item.id * 7) % 20) - 10
  return Math.max(30, Math.min(100, stat + variation))
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

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchItems()
  }
})
</script>

<style scoped>
/* 이미지 크기 - 데스크탑 */
.item-image {
  height: 200px;
  object-fit: cover;
  border-radius: 12px 12px 0 0;
}

/* 모바일용 이미지 & 카드 축소 */
@media (max-width: 767.98px) {
  .item-image {
    height: 100px;
    border-radius: 8px 8px 0 0;
  }

  .item-card {
    border-radius: 8px;
  }

  .item-body {
    padding: 0.5rem !important;
  }

  .item-name {
    font-size: 0.75rem;
    line-height: 1.2;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .btn-delete {
    width: 20px;
    height: 20px;
    font-size: 10px;
    top: 4px;
    right: 4px;
  }

  .top-luck-badge {
    padding: 2px 6px;
    font-size: 9px;
    border-radius: 0 0 6px 6px;
  }
}

.item-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
  position: relative;
}

.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

/* 최고 행운 아이템 강조 */
.top-luck-item {
  box-shadow: 0 0 0 2px #fbbf24, 0 0 20px rgba(251, 191, 36, 0.4);
  animation: luck-glow 2s ease-in-out infinite;
}

.top-luck-item:hover {
  box-shadow: 0 0 0 2px #fbbf24, 0 8px 30px rgba(251, 191, 36, 0.5);
}

@keyframes luck-glow {
  0%, 100% {
    box-shadow: 0 0 0 2px #fbbf24, 0 0 15px rgba(251, 191, 36, 0.3);
  }
  50% {
    box-shadow: 0 0 0 2px #fbbf24, 0 0 25px rgba(251, 191, 36, 0.6);
  }
}

.top-luck-badge {
  position: absolute;
  top: -1px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #1a1a2e;
  padding: 4px 12px;
  border-radius: 0 0 10px 10px;
  font-size: 11px;
  font-weight: 700;
  z-index: 10;
  white-space: nowrap;
}

.top-luck-badge i {
  margin-right: 4px;
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

/* 게임 스탯 스타일 */
.stat-section {
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.stat-row:last-child {
  margin-bottom: 0;
}

.stat-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  width: 50px;
  flex-shrink: 0;
}

.stat-label i {
  margin-right: 4px;
}

.stat-bar-container {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.stat-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.stat-value {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  width: 24px;
  text-align: right;
  flex-shrink: 0;
}
</style>
