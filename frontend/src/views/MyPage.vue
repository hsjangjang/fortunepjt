<template>
  <DefaultLayout>
    <div class="page-container">
      <div class="content-wrapper wide">
        <div class="mypage-layout">
          <!-- 좌측 사이드바 -->
          <aside class="mypage-sidebar">
            <div class="sidebar-header">
              <div class="user-info">
                <h4 class="user-name">{{ userFullName }}님 <span class="user-id">@{{ authStore.user?.username }}</span></h4>
              </div>
            </div>
            <nav class="sidebar-nav">
              <button
                class="nav-btn"
                :class="{ active: activeTab === 'items' }"
                @click="activeTab = 'items'"
              >
                <Package :size="18" class="me-2" />
                내 아이템
              </button>
              <button
                class="nav-btn"
                :class="{ active: activeTab === 'profile' }"
                @click="activeTab = 'profile'"
              >
                <Settings :size="18" class="me-2" />
                프로필 설정
              </button>
            </nav>
          </aside>

          <!-- 우측 콘텐츠 영역 -->
          <main class="mypage-content">
            <!-- 내 아이템 탭 -->
            <div v-if="activeTab === 'items'" class="tab-content">
              <div class="page-header page-header-lg">
                <h1 class="page-title">
                  <img src="@/assets/images/logo.png" alt="" class="page-title-icon" />
                  내 아이템
                </h1>
                <p class="page-subtitle">업로드한 아이템과 행운색 매칭도를 확인하세요</p>
              </div>

              <!-- 운세 미생성 시 유도 배너 -->
              <div v-if="!fortuneData" class="fortune-prompt-banner mb-4">
                <div class="fortune-prompt-content">
                  <i class="fas fa-magic fortune-prompt-icon"></i>
                  <div class="fortune-prompt-text">
                    <p class="fortune-prompt-title">오늘의 운세를 아직 확인하지 않으셨네요!</p>
                    <p class="fortune-prompt-desc">당신의 아이템이 오늘 어떤 행운을 불러올지 궁금하다면, 지금 오늘의 운세를 확인해보세요!</p>
                  </div>
                  <router-link to="/fortune/today" class="btn btn-primary rounded-pill px-4">
                    <i class="fas fa-crystal-ball me-1"></i> 운세 확인하기
                  </router-link>
                </div>
              </div>

              <!-- 오늘의 행운색 표시 -->
              <div v-if="luckyColors.length > 0" class="card-base card-sm mb-4">
                <div class="lucky-colors-container">
                  <span class="text-white-50 fortune-label d-flex align-items-center justify-content-center">
                    <img src="@/assets/images/pallete.png" alt="" class="lucky-color-palette-icon me-2" />오늘의 행운색:
                  </span>
                  <div class="lucky-colors-list">
                    <span v-for="(color, index) in luckyColors" :key="index" class="lucky-color-item">
                      <span class="lucky-color-dot-lg" :style="{ background: getColorBackground(color) }"></span>
                      <span class="text-white lucky-color-name">{{ color }}</span>
                    </span>
                  </div>
                </div>
              </div>

              <!-- 아이템 카테고리 선택 -->
              <div class="card-base card-sm mb-4">
                <div class="d-flex flex-wrap align-items-center justify-content-center gap-2">
                  <button
                    v-for="cat in itemCategories"
                    :key="cat.key"
                    class="btn btn-sm rounded-pill item-cat-btn"
                    :class="{ active: selectedItemCategory === cat.key }"
                    @click="selectedItemCategory = cat.key"
                  >
                    <i :class="cat.icon" class="me-1"></i>
                    {{ cat.label }}
                  </button>
                </div>
              </div>

              <div class="d-flex justify-content-between align-items-center mb-4">
                <h5>총 {{ filteredItems.length }}개 아이템</h5>
                <router-link to="/items/upload" class="btn btn-primary">
                  <i class="fas fa-plus"></i> 아이템 추가
                </router-link>
              </div>

              <div v-if="filteredItems.length > 0" class="row g-2 g-md-4">
                <div v-for="item in filteredItems" :key="item.id" class="col-6 col-md-4 mb-2 mb-md-4">
                  <div class="card h-100 item-card border-0" :class="{ 'top-luck-item': item.id === topLuckItemId }" :style="item.id === topLuckItemId ? `--luck-color: ${selectedCategoryColor}` : ''">
                    <!-- 최고 행운 배지 -->
                    <div v-if="item.id === topLuckItemId" class="top-luck-badge">
                      <i class="fas fa-crown"></i> <span class="d-none d-md-inline">{{ fortuneCategories.find(c => c.key === selectedCategory)?.label }} 최고</span>
                    </div>
                    <div class="position-relative">
                      <router-link :to="`/items/${item.id}`">
                        <img
                          :src="getImageUrl(item.image)"
                          class="card-img-top item-image"
                          :alt="item.item_name"
                          @error="handleImageError"
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

                        <!-- 색상 태그 -->
                        <div v-if="item.dominant_colors && item.dominant_colors.length > 0" class="mb-1 mb-md-2">
                          <span
                            v-for="(color, index) in item.dominant_colors.slice(0, 1)"
                            :key="index"
                            class="badge rounded-pill"
                            :style="{
                              backgroundColor: color.hex,
                              color: getTextColor(color.hex),
                              border: '1px solid rgba(255,255,255,0.2)'
                            }"
                          >
                            {{ color.korean_name }}
                          </span>
                        </div>

                        <!-- 소분류 태그 -->
                        <div v-if="getSubCategoryDisplay(item)" class="mb-1 mb-md-2 d-none d-md-block">
                          <span class="badge rounded-pill sub-category-badge">
                            #{{ getSubCategoryDisplay(item) }}
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

                        <!-- 모바일 행운 점수 (간략) - 선택된 운세 카테고리 아이콘 표시 -->
                        <div class="mt-auto d-md-none">
                          <div class="mobile-luck-score" :style="{ background: `${selectedCategoryColor}25`, color: selectedCategoryColor }">
                            <i :class="'fas ' + fortuneCategories.find(c => c.key === selectedCategory)?.icon" class="me-1"></i>
                            <span>{{ getFortuneBoost(item, selectedCategory) }}</span>
                          </div>
                        </div>

                        <!-- 게임 스탯 스타일 운세 영향도 - 데스크탑 -->
                        <div class="mt-auto stat-section d-none d-md-block">
                          <div class="stat-row">
                            <span class="stat-label"><i class="fas fa-palette"></i> 색상</span>
                            <div class="stat-bar-container">
                              <div class="stat-bar" :style="{ width: getColorStat(item) + '%', background: 'linear-gradient(90deg, #a78bfa, #7c3aed)' }"></div>
                            </div>
                            <span class="stat-value">{{ getColorStat(item) }}</span>
                          </div>
                          <div class="stat-row">
                            <span class="stat-label"><i :class="'fas ' + fortuneCategories.find(c => c.key === selectedCategory)?.icon" :style="{ color: fortuneCategories.find(c => c.key === selectedCategory)?.color }"></i> {{ fortuneCategories.find(c => c.key === selectedCategory)?.label.slice(0, 2) }}</span>
                            <div class="stat-bar-container">
                              <div class="stat-bar" :style="{ width: getFortuneBoost(item, selectedCategory) + '%', background: `linear-gradient(90deg, ${fortuneCategories.find(c => c.key === selectedCategory)?.color}, ${fortuneCategories.find(c => c.key === selectedCategory)?.color}dd)` }"></div>
                            </div>
                            <span class="stat-value">{{ getFortuneBoost(item, selectedCategory) }}</span>
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
                  <h3 class="empty-title" v-if="items.length === 0">아직 업로드한 아이템이 없습니다</h3>
                  <h3 class="empty-title" v-else>{{ itemCategories.find(c => c.key === selectedItemCategory)?.label }} 카테고리에 아이템이 없습니다</h3>
                  <p class="empty-text" v-if="items.length === 0">첫 번째 아이템을 업로드하고 행운색 매칭도를 확인해보세요!</p>
                  <p class="empty-text" v-else>다른 카테고리를 선택하거나 새 아이템을 업로드해보세요!</p>
                  <router-link to="/items/upload" class="btn btn-primary btn-lg rounded-pill px-5">
                    <i class="fas fa-upload me-2"></i> {{ items.length === 0 ? '첫 아이템 업로드하기' : '아이템 업로드하기' }}
                  </router-link>
                </div>
              </div>
            </div>

            <!-- 프로필 설정 탭 -->
            <div v-if="activeTab === 'profile'" class="tab-content">
              <div class="glass-card responsive-padding shadow-lg">
                <div class="d-flex justify-content-between align-items-center mb-4">
                  <h2 class="text-white mb-0">
                    <i class="fas fa-user-circle text-primary me-2"></i> 프로필 설정
                  </h2>
                  <button
                    v-if="!isEditing"
                    @click="editProfile"
                    class="btn btn-outline-light rounded-pill px-4"
                  >
                    <i class="fas fa-edit me-2"></i> 수정
                  </button>
                </div>

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

                  <hr class="my-4 border-light border-opacity-25">

                  <div class="text-center d-flex justify-content-center gap-2 flex-wrap">
                    <router-link to="/change-password" class="btn btn-outline-light btn-sm rounded-pill px-3">
                      <i class="fas fa-key me-1"></i> 비밀번호 변경
                    </router-link>
                    <router-link to="/delete-account" class="btn btn-outline-danger btn-sm rounded-pill px-3">
                      <i class="fas fa-user-times me-1"></i> 회원 탈퇴
                    </router-link>
                  </div>
                </form>

                <!-- 프로필 보기 -->
                <div v-else id="profile-view">
                  <div class="row">
                    <!-- 기본 정보 블록 -->
                    <div class="col-md-6 mb-4">
                      <div class="info-section-block">
                        <h5 class="info-section-title">기본 정보</h5>
                        <div class="info-items">
                          <div class="info-row">
                            <span class="info-label">이름:</span>
                            <span class="info-value">{{ fullName || '미입력' }}</span>
                          </div>
                          <div class="info-row">
                            <span class="info-label">아이디:</span>
                            <span class="info-value">{{ authStore.user?.username }}</span>
                          </div>
                          <div class="info-row">
                            <span class="info-label">이메일:</span>
                            <span class="info-value">{{ authStore.user?.email || '미입력' }}</span>
                          </div>
                          <div class="info-row">
                            <span class="info-label">생년월일:</span>
                            <span class="info-value">{{ formatBirthDate(authStore.user?.birth_date) }}</span>
                          </div>
                          <div class="info-row">
                            <span class="info-label">성별:</span>
                            <span class="info-value">{{ formatGender(authStore.user?.gender) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- 추가 정보 블록 -->
                    <div class="col-md-6 mb-4">
                      <div class="info-section-block">
                        <h5 class="info-section-title">추가 정보</h5>
                        <div class="info-items">
                          <div class="info-row">
                            <span class="info-label">별자리:</span>
                            <span class="info-value">{{ authStore.user?.zodiac_sign || '계산중' }}</span>
                          </div>
                          <div class="info-row">
                            <span class="info-label">띠:</span>
                            <span class="info-value">{{ authStore.user?.chinese_zodiac || '계산중' }}</span>
                          </div>
                          <div class="info-row">
                            <span class="info-label">MBTI:</span>
                            <span class="info-value">{{ authStore.user?.mbti || '미입력' }}</span>
                          </div>
                          <div class="info-row">
                            <span class="info-label">퍼스널컬러:</span>
                            <span class="info-value">{{ getPersonalColorDisplay(authStore.user?.personal_color) }}</span>
                          </div>
                          <div class="info-row">
                            <span class="info-label">태어난 시간:</span>
                            <span class="info-value">{{ formatBirthTime(authStore.user?.birth_time) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <hr class="my-4">

                  <div class="text-center">
                    <router-link to="/fortune/today" class="btn btn-primary rounded-pill px-4">
                      <i class="fas fa-star me-1"></i> 오늘의 운세 보기
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'
import { API_BASE_URL } from '@/config/api'
import { getTextColor, getColorMatchScore, getColorBackground } from '@/utils/colors'
import { getFortuneBoostScore } from '@/utils/similarity'
import { FORTUNE_CATEGORIES, getCategoryColor } from '@/utils/fortuneCategories'
import { Package, Settings } from 'lucide-vue-next'

const route = useRoute()
const authStore = useAuthStore()
const { showToast } = useToast()

// 탭 상태 (기본값: items, 쿼리 파라미터로 profile 가능)
const activeTab = ref(route.query.tab === 'profile' ? 'profile' : 'items')

// 사용자 전체 이름 (성 + 이름)
const userFullName = computed(() => {
  const user = authStore.user
  if (!user) return authStore.username

  const lastName = user.last_name || ''
  const firstName = user.first_name || ''
  const fullName = (lastName + firstName).trim()

  return fullName || authStore.username
})

// ===== 아이템 관련 =====
const items = ref([])
const fortuneData = ref(null)
const luckyColors = ref([])
const fortuneCategories = FORTUNE_CATEGORIES
const selectedCategory = ref('overall')

// 아이템 카테고리 정의
const itemCategories = [
  { key: 'all', label: '전체', icon: 'fas fa-th-large' },
  { key: 'clothing', label: '의류', icon: 'fas fa-tshirt' },
  { key: 'accessories', label: '액세서리', icon: 'fas fa-gem' },
  { key: 'etc', label: '기타', icon: 'fas fa-ellipsis-h' }
]
const selectedItemCategory = ref('all')

// 필터링된 아이템 목록
const filteredItems = computed(() => {
  if (selectedItemCategory.value === 'all') {
    return items.value
  }
  return items.value.filter(item => item.main_category === selectedItemCategory.value)
})

// 소분류 표시 함수
const getSubCategoryDisplay = (item) => {
  if (item.sub_category) {
    return item.sub_category
  }
  if (item.custom_category) {
    return item.custom_category
  }
  return null
}

const selectedCategoryColor = computed(() => getCategoryColor(selectedCategory.value))

// 아이템별 운세 점수 계산 (유틸리티 사용)
const getFortuneBoost = (item, category) => {
  return getFortuneBoostScore(item, luckyColors.value, category, getColorMatchScore, fortuneData.value?.lucky_item)
}

// 선택된 카테고리 기준 최고 행운 아이템 ID 계산 (필터링된 아이템 기준)
const topLuckItemId = computed(() => {
  if (filteredItems.value.length === 0) return null
  let maxLuck = -1
  let topId = null
  filteredItems.value.forEach(item => {
    const luck = getFortuneBoost(item, selectedCategory.value)
    if (luck > maxLuck) {
      maxLuck = luck
      topId = item.id
    }
  })
  return topId
})

// 운세 데이터 가져오기
const fetchFortuneData = async () => {
  try {
    const response = await api.get('/api/fortune/today/')
    if (response.data.success && response.data.fortune) {
      fortuneData.value = response.data.fortune
      luckyColors.value = response.data.fortune.lucky_colors || []
    }
  } catch (error) {
    console.error('운세 데이터 가져오기 실패:', error)
  }
}

// 이미지 URL에 base URL 추가
const getImageUrl = (url) => {
  if (!url) return 'data:image/svg+xml,' + encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
      <rect fill="#2d2d3d" width="200" height="200"/>
      <text x="100" y="100" font-family="Arial" font-size="48" fill="#666" text-anchor="middle" dominant-baseline="middle">...</text>
    </svg>
  `)
  // 이미 절대 URL인 경우 (S3/CloudFront URL)
  if (url.startsWith('http')) return url
  // 상대 경로인 경우 API_BASE_URL 추가
  return `${API_BASE_URL}${url}`
}

// 이미지 로딩 실패 시 플레이스홀더로 대체
const handleImageError = (event) => {
  event.target.src = 'data:image/svg+xml,' + encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
      <rect fill="#2d2d3d" width="200" height="200"/>
      <text x="100" y="100" font-family="Arial" font-size="48" fill="#666" text-anchor="middle" dominant-baseline="middle">...</text>
    </svg>
  `)
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

// ===== 프로필 관련 =====
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

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchItems()
    fetchFortuneData()
    authStore.fetchUser()
  }
})
</script>

<style scoped>
/* 마이페이지 레이아웃 */
.mypage-layout {
  display: flex;
  gap: 2rem;
  min-height: calc(100vh - 200px);
}

/* 좌측 사이드바 */
.mypage-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  height: fit-content;
  position: sticky;
  top: 100px;
}

.sidebar-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1.5rem;
}

.user-avatar {
  color: #fff;
}

.user-info {
  overflow: hidden;
  text-align: center;
}

.user-name {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-id {
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.0rem;
  font-weight: 400;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.nav-btn.active {
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  color: #fff;
  font-weight: 600;
}

/* 우측 콘텐츠 영역 */
.mypage-content {
  flex: 1;
  min-width: 0;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 모바일 반응형 */
@media (max-width: 991.98px) {
  .mypage-layout {
    flex-direction: column;
    gap: 1rem;
  }

  .mypage-sidebar {
    width: 100%;
    position: static;
    padding: 1rem;
  }

  .sidebar-header {
    padding-bottom: 1rem;
    margin-bottom: 1rem;
  }

  .sidebar-nav {
    flex-direction: row;
    gap: 0.5rem;
  }

  .nav-btn {
    flex: 1;
    justify-content: center;
    padding: 0.6rem 0.75rem;
    font-size: 0.85rem;
  }
}

/* ===== 아이템 목록 스타일 (List.vue에서 가져옴) ===== */
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
  --luck-color: #a78bfa;
  box-shadow: 0 0 0 2px var(--luck-color), 0 0 20px color-mix(in srgb, var(--luck-color) 40%, transparent);
  animation: luck-glow 2s ease-in-out infinite;
}

.top-luck-item:hover {
  box-shadow: 0 0 0 2px var(--luck-color), 0 8px 30px color-mix(in srgb, var(--luck-color) 50%, transparent);
}

@keyframes luck-glow {
  0%, 100% {
    box-shadow: 0 0 0 2px var(--luck-color), 0 0 15px color-mix(in srgb, var(--luck-color) 30%, transparent);
  }
  50% {
    box-shadow: 0 0 0 2px var(--luck-color), 0 0 25px color-mix(in srgb, var(--luck-color) 60%, transparent);
  }
}

.top-luck-badge {
  position: absolute;
  top: -1px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, var(--luck-color), color-mix(in srgb, var(--luck-color) 80%, black));
  color: #fff;
  padding: 4px 12px;
  border-radius: 0 0 10px 10px;
  font-size: 11px;
  font-weight: 700;
  z-index: 10;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
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

/* 운세 카테고리 버튼 */
.fortune-cat-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
  transition: all 0.2s;
}

.fortune-cat-btn:hover {
  background: rgba(124, 58, 237, 0.3);
  border-color: rgba(124, 58, 237, 0.5);
  color: #fff;
}

.fortune-cat-btn.active {
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  border-color: #7c3aed;
  color: #fff;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.4);
}

/* 아이템 카테고리 버튼 */
.item-cat-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  padding: 0.4rem 1rem;
  transition: all 0.2s;
}

.item-cat-btn:hover {
  background: rgba(124, 58, 237, 0.3);
  border-color: rgba(124, 58, 237, 0.5);
  color: #fff;
}

.item-cat-btn.active {
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  border-color: #7c3aed;
  color: #fff;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.4);
}

/* 소분류 배지 */
.sub-category-badge {
  background: rgba(124, 58, 237, 0.3);
  color: #c4b5fd;
  font-size: 0.75rem;
  font-weight: 500;
}

/* 행운색 컨테이너 - 데스크톱: 가로 배치, 모바일: 세로 배치 */
.lucky-colors-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.lucky-colors-list {
  display: flex;
  align-items: center;
  gap: 1rem;
}

@media (max-width: 767.98px) {
  .lucky-colors-container {
    flex-direction: column !important;
    gap: 0.75rem !important;
  }

  .lucky-colors-list {
    justify-content: center !important;
  }
}

/* 모바일 행운 점수 - 선택된 운세 카테고리 색상으로 동적 표시 */
.mobile-luck-score {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  padding: 4px 8px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background 0.3s, color 0.3s;
}

/* 운세별/행운색 라벨 동일 스타일 */
.fortune-label {
  font-size: 0.9rem;
}

/* 행운색 아이템 (점 + 텍스트) */
.lucky-color-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.lucky-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

/* 팔레트 아이콘 */
.lucky-color-palette-icon {
  width: 22px;
  height: 22px;
  object-fit: contain;
}

/* 페이지 타이틀 아이콘 */
.page-title-icon {
  width: 40px;
  height: 40px;
  margin-right: 0.5rem;
  vertical-align: middle;
  object-fit: contain;
}

/* 행운색 스타일 */
.lucky-color-dot-lg {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.lucky-color-name {
  font-size: 1rem;
  font-weight: 500;
}

/* 운세 미생성 시 유도 배너 */
.fortune-prompt-banner {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(59, 130, 246, 0.2));
  border: 1px solid rgba(124, 58, 237, 0.4);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
}

.fortune-prompt-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.fortune-prompt-icon {
  font-size: 2rem;
  color: #a78bfa;
  flex-shrink: 0;
}

.fortune-prompt-text {
  flex: 1;
  min-width: 200px;
  text-align: center;
}

.fortune-prompt-title {
  color: #fff;
  font-weight: 600;
  margin-bottom: 0.25rem;
  font-size: 1rem;
}

.fortune-prompt-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 0;
}

@media (max-width: 767.98px) {
  .fortune-cat-btn {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }

  .item-cat-btn {
    font-size: 0.75rem;
    padding: 0.3rem 0.6rem;
  }

  .item-cat-btn i {
    display: none;
  }

  .fortune-label {
    font-size: 0.8rem;
  }

  .fortune-prompt-banner {
    padding: 1rem;
  }

  .fortune-prompt-icon {
    font-size: 1.5rem;
  }

  .fortune-prompt-title {
    font-size: 0.95rem;
  }

  .fortune-prompt-desc {
    font-size: 0.85rem;
  }
}

/* ===== 프로필 스타일 (Profile.vue에서 가져옴) ===== */
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

.table-borderless {
  background: transparent !important;
}

.table-borderless th,
.table-borderless td {
  color: #fff !important;
  padding: 0.5rem 0;
  background: transparent !important;
}

.table-borderless th {
  font-weight: 600;
}

/* Bootstrap table 배경 오버라이드 */
.table {
  --bs-table-bg: transparent;
  --bs-table-striped-bg: transparent;
  background-color: transparent !important;
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

.btn-outline-danger.btn-sm.rounded-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}

/* Responsive Padding Utilities */
.responsive-padding {
  padding: 3rem !important;
}

/* 정보 섹션 블록 스타일 */
.info-section-block {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  height: 100%;
}

.info-section-title {
  text-align: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 1.1rem;
  font-weight: 600;
}

.info-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.info-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
}

.info-value {
  color: #fff;
  font-weight: 700;
  font-size: 0.95rem;
  text-align: right;
}

@media (max-width: 768px) {
  .responsive-padding {
    padding: 3% !important;
  }
}
</style>
