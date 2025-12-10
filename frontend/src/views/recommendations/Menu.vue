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

          <!-- Fortune Info -->
          <div v-if="!isLoading && fortuneData" class="card-base card-md section-spacing">
              <!-- 운세 요약 -->
              <p v-if="fortuneData.fortune_summary" class="text-white text-center mb-3" style="font-size: 0.95rem;">
                <i class="fas fa-star-half-alt text-warning me-1"></i>
                {{ fortuneData.fortune_summary }}
              </p>
              <!-- 오늘의 행운색 -->
              <div v-if="fortuneData.lucky_colors && fortuneData.lucky_colors.length" class="text-center mb-3">
                <h6 class="text-white opacity-75 mb-2">
                  <i class="fas fa-palette text-primary me-1"></i>
                  오늘의 행운색
                </h6>
                <div class="d-flex flex-wrap align-items-center justify-content-center gap-2">
                  <span v-for="color in fortuneData.lucky_colors" :key="color" class="badge rounded-pill px-3 py-2" :style="`background-color: ${colorMap[color] || '#a78bfa'}; color: ${getTextColor(colorMap[color])};`">
                    {{ color }}
                  </span>
                </div>
              </div>
              <!-- 운세 정보 배지 -->
              <div class="badge-row justify-content-center">
                <div class="text-center px-4">
                  <h6 class="text-white opacity-75 mb-2">오늘의 운세 점수</h6>
                  <h3 class="text-primary-light mb-0">{{ fortuneData.fortune_score || 0 }}점</h3>
                </div>
                <div class="text-center px-4">
                  <h6 class="text-white opacity-75 mb-2">별자리</h6>
                  <h4 class="text-white mb-0">{{ fortuneData.zodiac_sign || '-' }}</h4>
                </div>
                <div class="text-center px-4">
                  <h6 class="text-white opacity-75 mb-2">띠</h6>
                  <h4 class="text-white mb-0">{{ fortuneData.chinese_zodiac || '-' }}</h4>
                </div>
              </div>
          </div>

          <!-- Main Menu Recommendations -->
          <div v-if="!isLoading" class="card-grid cols-2 section-spacing">
            <div v-for="rec in recommendations" :key="rec.rank" class="card-base card-md card-interactive position-relative overflow-hidden text-center">
                <!-- Subtle Gradient Background Glow -->
                <div class="position-absolute top-0 start-50 translate-middle-x mt-n4"
                     :style="`width: 150px; height: 150px; background: ${rec.bg_gradient}; filter: blur(60px); opacity: 0.2;`"></div>

                  <div class="mb-3 position-relative">
                    <span class="badge rounded-pill px-3 py-2 text-white"
                          style="background: rgba(255,255,255,0.1); backdrop-filter: blur(5px); font-size: 1.1rem;">
                      {{ rec.rank === 1 ? '🥇 1순위 추천' : '🥈 2순위 추천' }}
                    </span>
                  </div>

                  <div class="menu-icon mb-4 animate-float d-flex justify-content-center position-relative">
                    <div class="rounded-circle overflow-hidden shadow-lg border border-2 border-white border-opacity-25" style="width: 150px; height: 150px;">
                      <img :src="getFoodImage(rec.menu.category, rec.menu.name)" :alt="rec.menu.name" class="w-100 h-100 object-fit-cover" />
                    </div>
                  </div>

                  <h3 class="fw-bold mb-2 text-white position-relative">{{ rec.menu.name }}</h3>
                  <p class="text-white-50 mb-4 position-relative">{{ rec.menu.category }}</p>

                  <div class="mb-4 position-relative">
                    <span class="badge px-3 py-2 rounded-pill d-inline-flex align-items-center" :style="`background-color: ${colorMap[rec.color] || '#a78bfa'}; color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.3);`">
                      <i class="fas fa-palette me-1"></i> {{ rec.color }}
                    </span>
                  </div>

                  <div class="info-box position-relative">
                    <p class="small mb-0 text-white">{{ rec.menu.desc }}</p>
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

            <div class="card-grid cols-3">
              <div v-for="item in otherRecommendations" :key="item.menu.name" class="info-box text-center hover-lift d-flex flex-column align-items-center justify-content-center">
                  <div class="mb-2 flex-shrink-0">
                    <img :src="getFoodImage(item.menu.category, item.menu.name)" :alt="item.menu.name" class="other-menu-img rounded-circle" />
                  </div>
                  <h6 class="small mb-2 text-white menu-name justify-content-center">{{ item.menu.name }}</h6>
                  <span class="badge rounded-pill mt-auto" :style="`background-color: ${colorMap[item.color] || '#6B7280'}; color: ${getTextColor(colorMap[item.color])}; font-size: 0.7rem;`">{{ item.color }}</span>
              </div>

              <div v-if="!otherRecommendations.length" class="text-center">
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

// 75개 음식 개별 이미지 imports
import kimchiJjigae from '@/assets/images/food/kimchi_jjigae.png'
import doenjangJjigae from '@/assets/images/food/doenjang_jjigae.png'
import sundubuJjigae from '@/assets/images/food/sundubu_jjigae.png'
import galbitang from '@/assets/images/food/galbitang.png'
import samgyetang from '@/assets/images/food/samgyetang.png'
import budaeJjigae from '@/assets/images/food/budae_jjigae.png'
import gamjatang from '@/assets/images/food/gamjatang.png'
import yukgaejang from '@/assets/images/food/yukgaejang.png'
import tteokguk from '@/assets/images/food/tteokguk.png'
import eomukTang from '@/assets/images/food/eomuk_tang.png'
import sogogiGukbap from '@/assets/images/food/sogogi_gukbap.png'
import dwaejiGukbap from '@/assets/images/food/dwaeji_gukbap.png'
import seolleongtang from '@/assets/images/food/seolleongtang.png'
import gomtang from '@/assets/images/food/gomtang.png'
import haejangguk from '@/assets/images/food/haejangguk.png'
import samgyeopsal from '@/assets/images/food/samgyeopsal.png'
import bulgogi from '@/assets/images/food/bulgogi.png'
import galbiJjim from '@/assets/images/food/galbi_jjim.png'
import jeyukBokkeum from '@/assets/images/food/jeyuk_bokkeum.png'
import dakgalbi from '@/assets/images/food/dakgalbi.png'
import jokbal from '@/assets/images/food/jokbal.png'
import bossam from '@/assets/images/food/bossam.png'
import gopchang from '@/assets/images/food/gopchang.png'
import makchang from '@/assets/images/food/makchang.png'
import bibimbap from '@/assets/images/food/bibimbap.png'
import gimbap from '@/assets/images/food/gimbap.png'
import japchae from '@/assets/images/food/japchae.png'
import bokkeumbap from '@/assets/images/food/bokkeumbap.png'
import kimchiBokkeumbap from '@/assets/images/food/kimchi_bokkeumbap.png'
import jumeokbap from '@/assets/images/food/jumeokbap.png'
import tteokbokki from '@/assets/images/food/tteokbokki.png'
import sundae from '@/assets/images/food/sundae.png'
import ramyeon from '@/assets/images/food/ramyeon.png'
import mandu from '@/assets/images/food/mandu.png'
import twigim from '@/assets/images/food/twigim.png'
import haemulPajeon from '@/assets/images/food/haemul_pajeon.png'
import kimchiJeon from '@/assets/images/food/kimchi_jeon.png'
import naengmyeon from '@/assets/images/food/naengmyeon.png'
import kalguksu from '@/assets/images/food/kalguksu.png'
import janchiGuksu from '@/assets/images/food/janchi_guksu.png'
import jajangmyeon from '@/assets/images/food/jajangmyeon.png'
import jjamppong from '@/assets/images/food/jjamppong.png'
import bokkeummyeon from '@/assets/images/food/bokkeummyeon.png'
import udon from '@/assets/images/food/udon.png'
import ramen from '@/assets/images/food/ramen.png'
import ssalguksu from '@/assets/images/food/ssalguksu.png'
import padThai from '@/assets/images/food/pad_thai.png'
import bokkeumUdon from '@/assets/images/food/bokkeum_udon.png'
import tangsuyuk from '@/assets/images/food/tangsuyuk.png'
import mapoTofu from '@/assets/images/food/mapo_tofu.png'
import sushi from '@/assets/images/food/sushi.png'
import sashimi from '@/assets/images/food/sashimi.png'
import donkatsu from '@/assets/images/food/donkatsu.png'
import curry from '@/assets/images/food/curry.png'
import omurice from '@/assets/images/food/omurice.png'
import steak from '@/assets/images/food/steak.png'
import pasta from '@/assets/images/food/pasta.png'
import pizza from '@/assets/images/food/pizza.png'
import hamburger from '@/assets/images/food/hamburger.png'
import salad from '@/assets/images/food/salad.png'
import soup from '@/assets/images/food/soup.png'
import risotto from '@/assets/images/food/risotto.png'
import omelette from '@/assets/images/food/omelette.png'
import friedChicken from '@/assets/images/food/fried_chicken.png'
import yangnyeomChicken from '@/assets/images/food/yangnyeom_chicken.png'
import ganjangChicken from '@/assets/images/food/ganjang_chicken.png'
import chickenNuggets from '@/assets/images/food/chicken_nuggets.png'
import dakgangjeong from '@/assets/images/food/dakgangjeong.png'
import jjimdak from '@/assets/images/food/jjimdak.png'
import iceCream from '@/assets/images/food/ice_cream.png'
import patbingsu from '@/assets/images/food/patbingsu.png'
import cake from '@/assets/images/food/cake.png'
import waffle from '@/assets/images/food/waffle.png'
import americano from '@/assets/images/food/americano.png'
import cafeLatte from '@/assets/images/food/cafe_latte.png'

// 음식 이름 -> 이미지 매핑
const foodImageMap = {
  '김치찌개': kimchiJjigae,
  '된장찌개': doenjangJjigae,
  '순두부찌개': sundubuJjigae,
  '갈비탕': galbitang,
  '삼계탕': samgyetang,
  '부대찌개': budaeJjigae,
  '감자탕': gamjatang,
  '육개장': yukgaejang,
  '떡국': tteokguk,
  '어묵탕': eomukTang,
  '소고기국밥': sogogiGukbap,
  '돼지국밥': dwaejiGukbap,
  '설렁탕': seolleongtang,
  '곰탕': gomtang,
  '해장국': haejangguk,
  '삼겹살': samgyeopsal,
  '불고기': bulgogi,
  '갈비찜': galbiJjim,
  '제육볶음': jeyukBokkeum,
  '닭갈비': dakgalbi,
  '족발': jokbal,
  '보쌈': bossam,
  '곱창': gopchang,
  '막창': makchang,
  '비빔밥': bibimbap,
  '김밥': gimbap,
  '잡채': japchae,
  '볶음밥': bokkeumbap,
  '김치볶음밥': kimchiBokkeumbap,
  '주먹밥': jumeokbap,
  '떡볶이': tteokbokki,
  '순대': sundae,
  '라면': ramyeon,
  '만두': mandu,
  '튀김': twigim,
  '해물파전': haemulPajeon,
  '김치전': kimchiJeon,
  '냉면': naengmyeon,
  '칼국수': kalguksu,
  '잔치국수': janchiGuksu,
  '짜장면': jajangmyeon,
  '짬뽕': jjamppong,
  '볶음면': bokkeummyeon,
  '우동': udon,
  '라멘': ramen,
  '쌀국수': ssalguksu,
  '팟타이': padThai,
  '볶음우동': bokkeumUdon,
  '탕수육': tangsuyuk,
  '마파두부': mapoTofu,
  '초밥': sushi,
  '회': sashimi,
  '돈까스': donkatsu,
  '카레': curry,
  '오므라이스': omurice,
  '스테이크': steak,
  '파스타': pasta,
  '피자': pizza,
  '햄버거': hamburger,
  '샐러드': salad,
  '스프': soup,
  '리조또': risotto,
  '오믈렛': omelette,
  '후라이드치킨': friedChicken,
  '양념치킨': yangnyeomChicken,
  '간장치킨': ganjangChicken,
  '치킨너겟': chickenNuggets,
  '닭강정': dakgangjeong,
  '찜닭': jjimdak,
  '아이스크림': iceCream,
  '팥빙수': patbingsu,
  '케이크': cake,
  '와플': waffle,
  '아메리카노': americano,
  '카페라떼': cafeLatte,
}

const authStore = useAuthStore()
const fortuneData = ref(null)
const recommendations = ref([])
const otherRecommendations = ref([])
const isLoading = ref(true)

// 음식 이름으로 정확한 이미지 매핑
const getFoodImage = (type, name = '') => {
  // 정확한 이름 매칭
  if (foodImageMap[name]) {
    return foodImageMap[name]
  }
  // 기본값
  return bibimbap
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
/* 그 외 추천 메뉴 카드 스타일 */
.other-menu-card {
  min-height: 140px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.other-menu-img {
  width: 50px;
  height: 50px;
  object-fit: cover;
}

.menu-name {
  line-height: 1.3;
  word-break: keep-all;
  min-height: 2.6em;
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .responsive-padding {
    padding: 3% !important;
  }

  .other-menu-card {
    min-height: 120px;
    padding: 0.75rem !important;
  }

  .other-menu-img {
    width: 40px;
    height: 40px;
  }

  .menu-name {
    font-size: 0.75rem !important;
  }
}
</style>
