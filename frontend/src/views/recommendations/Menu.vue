<template>
  <DefaultLayout>
    <div class="page-container">
      <div class="content-wrapper wide">
        <!-- 페이지 헤더 -->
        <div class="page-header page-header-lg">
          <h1 class="page-title">
            <i class="fas fa-utensils" style="color: #a78bfa !important;"></i>
            오늘의 메뉴 추천
          </h1>
          <p class="page-subtitle">운세와 행운색을 기반으로 한 맞춤 메뉴</p>
        </div>

        <!-- 라우터 가드에서 인증/운세 체크 완료 후 진입 -->
        <template v-if="authStore.isAuthenticated">
          <!-- Loading State -->
          <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
              <span class="visually-hidden">Loading...</span>
            </div>
            <h5 class="text-white-50">메뉴 추천을 불러오는 중...</h5>
          </div>

          <!-- Fortune Info (OOTD 스타일) -->
          <div v-if="!isLoading && fortuneData" class="card-base card-sm text-center section-spacing">
              <!-- 종합 운세 한줄 요약 -->
              <p v-if="fortuneData.fortune_summary" class="text-white mb-2" style="font-size: 0.95rem;">
                <i class="fas fa-star-half-alt text-warning me-1"></i>
                {{ fortuneData.fortune_summary }}
              </p>
              <!-- 오늘의 행운색 - 텍스트로 표시 -->
              <div v-if="fortuneData.lucky_colors && fortuneData.lucky_colors.length" class="d-flex flex-wrap align-items-center justify-content-center gap-2">
                <span class="text-white opacity-75 me-1">
                  <i class="fas fa-palette me-1" style="color: #a78bfa;"></i>
                  오늘의 행운색:
                </span>
                <span class="text-white">{{ fortuneData.lucky_colors.join(', ') }}</span>
              </div>
          </div>

          <!-- Main Menu Recommendations (2열 그리드) -->
          <div v-if="!isLoading" class="section-spacing">
            <div class="row g-4">
              <div v-for="rec in recommendations" :key="rec.rank" class="col-md-6">
                <div class="card-base card-md card-interactive h-100 position-relative overflow-hidden text-center p-4">
                  <!-- Subtle Gradient Background Glow -->
                  <div class="position-absolute top-0 start-50 translate-middle-x"
                       :style="`width: 150px; height: 150px; background: ${rec.bg_gradient}; filter: blur(60px); opacity: 0.2; margin-top: -40px;`"></div>

                  <!-- 순위 배지 -->
                  <div class="mb-3 position-relative">
                    <span class="badge rounded-pill border border-white border-opacity-25 px-3 py-2 text-white"
                          style="background: rgba(255,255,255,0.1); backdrop-filter: blur(5px); font-size: 1rem;">
                      {{ rec.rank === 1 ? '🥇 1순위 추천' : '🥈 2순위 추천' }}
                    </span>
                  </div>

                  <!-- 이미지 (위) -->
                  <div class="menu-icon mb-4 animate-float d-flex justify-content-center position-relative">
                    <div class="rounded-circle overflow-hidden shadow-lg border border-2 border-white border-opacity-25 main-menu-img">
                      <img :src="getFoodImage(rec.menu.category, rec.menu.name)" :alt="rec.menu.name" class="w-100 h-100 object-fit-cover" />
                    </div>
                  </div>

                  <!-- 텍스트 (아래) -->
                  <h3 class="fw-bold mb-2 text-white position-relative main-menu-name">{{ rec.menu.name }}</h3>
                  <p class="text-white-50 mb-3 position-relative">{{ rec.menu.category }}</p>

                  <!-- 행운색 배지 -->
                  <div class="mb-4 position-relative">
                    <span class="badge px-3 py-2 rounded-pill d-inline-flex align-items-center"
                          :style="`background-color: ${colorMap[rec.color] || '#a78bfa'}; color: ${getTextColor(colorMap[rec.color])}; text-shadow: 0 1px 2px rgba(0,0,0,0.2);`">
                      <i class="fas fa-palette me-1"></i> {{ rec.color }}
                    </span>
                  </div>

                  <!-- 설명 -->
                  <div class="info-box position-relative">
                    <p class="small mb-0 text-white">{{ rec.menu.desc }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="!recommendations.length" class="text-center">
              <p class="text-white">추천할 메뉴가 없습니다.</p>
            </div>
          </div>

          <!-- Additional Recommendations -->
          <div v-if="!isLoading" class="card-base card-lg">
            <div class="d-flex justify-content-center align-items-center mb-4 border-bottom border-white border-opacity-10 pb-3">
              <div class="bg-primary bg-opacity-10 p-2 rounded-circle me-3">
                <i class="fas fa-utensils text-primary"></i>
              </div>
              <h5 class="mb-0 text-white">그 외 추천 메뉴</h5>
            </div>

            <div class="row text-center g-3">
              <div v-for="item in otherRecommendations" :key="item.menu.name" class="col-6 col-md-4">
                <div class="other-menu-item p-3 rounded-3 hover-lift">
                  <div class="mb-2">
                    <img :src="getFoodImage(item.menu.category, item.menu.name)" :alt="item.menu.name" class="other-menu-img rounded-circle" />
                  </div>
                  <h6 class="mb-1 text-white menu-name-md">{{ item.menu.name }}</h6>
                  <span class="badge rounded-pill px-2 py-1"
                        :style="`background-color: ${colorMap[item.color] || '#6b7280'}; color: ${getTextColor(colorMap[item.color])}; font-size: 0.75rem;`">
                    {{ item.color }}
                  </span>
                </div>
              </div>

              <div v-if="!otherRecommendations.length" class="col-12">
                <p class="text-white opacity-50">추가 추천 메뉴가 없습니다.</p>
              </div>
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
import { colorMap, getTextColor } from '@/utils/colors'

// 모든 음식 이미지를 동적으로 import (png, jpg 모두 지원)
const foodImages = import.meta.glob('@/assets/images/food/*.{png,jpg,jpeg}', { eager: true })

// 기본 이미지 (비빔밥)
const defaultImage = Object.values(foodImages).find(img =>
  img.default?.includes('bibimbap') || img.default?.includes('food_dish')
)?.default || ''

// 음식 이름 -> 파일명 매핑
const foodFileNameMap = {
  '김치찌개': 'kimchi_jjigae',
  '된장찌개': 'doenjang_jjigae',
  '순두부찌개': 'sundubu_jjigae',
  '갈비탕': 'galbitang',
  '삼계탕': 'samgyetang',
  '부대찌개': 'budae_jjigae',
  '감자탕': 'gamjatang',
  '육개장': 'yukgaejang',
  '떡국': 'tteokguk',
  '어묵탕': 'eomuk_tang',
  '소고기국밥': 'sogogi_gukbap',
  '돼지국밥': 'dwaeji_gukbap',
  '설렁탕': 'seolleongtang',
  '곰탕': 'gomtang',
  '해장국': 'haejangguk',
  '삼겹살': 'samgyeopsal',
  '불고기': 'bulgogi',
  '갈비찜': 'galbi_jjim',
  '제육볶음': 'jeyuk_bokkeum',
  '닭갈비': 'dakgalbi',
  '족발': 'jokbal',
  '보쌈': 'bossam',
  '곱창': 'gopchang',
  '막창': 'makchang',
  '비빔밥': 'bibimbap',
  '김밥': 'gimbap',
  '잡채': 'japchae',
  '볶음밥': 'bokkeumbap',
  '김치볶음밥': 'kimchi_bokkeumbap',
  '주먹밥': 'jumeokbap',
  '떡볶이': 'tteokbokki',
  '순대': 'sundae',
  '라면': 'ramyeon',
  '만두': 'mandu',
  '튀김': 'twigim',
  '해물파전': 'haemul_pajeon',
  '김치전': 'kimchi_jeon',
  '냉면': 'naengmyeon',
  '칼국수': 'kalguksu',
  '잔치국수': 'janchi_guksu',
  '짜장면': 'jajangmyeon',
  '짬뽕': 'jjamppong',
  '볶음면': 'bokkeummyeon',
  '우동': 'udon',
  '라멘': 'ramen',
  '쌀국수': 'ssalguksu',
  '팟타이': 'pad_thai',
  '볶음우동': 'bokkeum_udon',
  '탕수육': 'tangsuyuk',
  '마파두부': 'mapo_tofu',
  '초밥': 'sushi',
  '회': 'sashimi',
  '돈까스': 'donkatsu',
  '카레': 'curry',
  '오므라이스': 'omurice',
  '스테이크': 'steak',
  '파스타': 'pasta',
  '피자': 'pizza',
  '햄버거': 'hamburger',
  '샐러드': 'salad',
  '스프': 'soup',
  '리조또': 'risotto',
  '오믈렛': 'omelette',
  '후라이드치킨': 'fried_chicken',
  '양념치킨': 'yangnyeom_chicken',
  '간장치킨': 'ganjang_chicken',
  '치킨너겟': 'chicken_nuggets',
  '닭강정': 'dakgangjeong',
  '찜닭': 'jjimdak',
  '아이스크림': 'ice_cream',
  '팥빙수': 'patbingsu',
  '케이크': 'cake',
  '와플': 'waffle',
  '아메리카노': 'americano',
  '카페라떼': 'cafe_latte',
}

const authStore = useAuthStore()
const fortuneData = ref(null)
const recommendations = ref([])
const otherRecommendations = ref([])
const isLoading = ref(true)

// 음식 이름으로 이미지 찾기 (png, jpg 모두 지원)
const getFoodImage = (type, name = '') => {
  const fileName = foodFileNameMap[name]
  if (fileName) {
    // 파일명으로 이미지 찾기 (확장자 무관)
    const imageKey = Object.keys(foodImages).find(key => key.includes(fileName))
    if (imageKey) {
      return foodImages[imageKey].default
    }
  }
  // 기본값
  return defaultImage
}

const fetchMenuRecommendations = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/api/recommendations/menu/')
    const data = response.data

    if (data.fortune_data) {
      fortuneData.value = data.fortune_data
    }

    if (data.recommendations) {
      recommendations.value = data.recommendations
    }

    if (data.other_recommendations) {
      otherRecommendations.value = data.other_recommendations
    }
  } catch (error) {
    console.error('메뉴 추천 정보 가져오기 실패:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchMenuRecommendations()
  }
})

</script>

<style scoped>
.hover-lift {
  transition: transform 0.3s;
}

.hover-lift:hover {
  transform: translateY(-5px);
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}
/* 메인 추천 메뉴 이미지 */
.main-menu-img {
  width: 150px;
  height: 150px;
}

.main-menu-name {
  font-size: 1.5rem;
}

/* 그 외 추천 메뉴 스타일 */
.other-menu-item {
  background: rgba(255, 255, 255, 0.02);
  transition: all 0.3s ease;
}

.other-menu-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.other-menu-img {
  width: 70px;
  height: 70px;
  object-fit: cover;
}

.menu-name-md {
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.3;
  word-break: keep-all;
}

@media (max-width: 768px) {
  .responsive-padding {
    padding: 3% !important;
  }

  .main-menu-img {
    width: 110px;
    height: 110px;
  }

  .main-menu-name {
    font-size: 1.2rem;
  }

  .other-menu-img {
    width: 55px;
    height: 55px;
  }

  .menu-name-md {
    font-size: 0.85rem !important;
  }
}
</style>
