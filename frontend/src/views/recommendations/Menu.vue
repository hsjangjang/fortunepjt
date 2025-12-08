<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-12 mx-auto">
        <!-- Menu Header -->
        <div class="glass-card mb-4">
          <div class="card-body text-center py-4">
            <h1 class="display-5 fw-bold">
              <i class="fas fa-utensils text-success"></i> 오늘의 메뉴 추천
            </h1>
            <p class="lead text-white-50">운세와 행운색을 기반으로 한 맞춤 메뉴</p>
          </div>
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
          <div v-if="!isLoading && fortuneData" class="glass-card mb-4">
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-4">
                  <h6 class="text-white-50">오늘의 운세 점수</h6>
                  <h3 class="text-primary-light">{{ fortuneData.fortune_score || 0 }}점</h3>
                </div>
                <div class="col-md-4">
                  <h6 class="text-white-50">별자리</h6>
                  <h4 class="text-white">{{ fortuneData.zodiac_sign || '-' }}</h4>
                </div>
                <div class="col-md-4">
                  <h6 class="text-white-50">띠</h6>
                  <h4 class="text-white">{{ fortuneData.chinese_zodiac || '-' }}</h4>
                </div>
              </div>
            </div>
          </div>

          <!-- Main Menu Recommendations -->
          <div v-if="!isLoading" class="row">
            <div v-for="rec in recommendations" :key="rec.rank" class="col-md-6 mb-4">
              <div class="glass-card h-100 position-relative overflow-hidden hover-lift">
                <!-- Subtle Gradient Background Glow -->
                <div class="position-absolute top-0 start-50 translate-middle-x mt-n4"
                     :style="`width: 150px; height: 150px; background: ${rec.bg_gradient}; filter: blur(60px); opacity: 0.2;`"></div>

                <div class="card-body text-center p-4 position-relative">
                  <div class="mb-3">
                    <span class="badge rounded-pill border border-white border-opacity-25 px-3 py-2 text-white fs-5"
                          style="background: rgba(255,255,255,0.1); backdrop-filter: blur(5px);">
                      {{ rec.rank === 1 ? '🥇 1순위 추천' : '🥈 2순위 추천' }}
                    </span>
                  </div>

                  <div class="menu-icon mb-4 animate-float">
                    <img :src="getFoodImage(rec.menu.category, rec.menu.name)" :alt="rec.menu.name" width="120" class="img-fluid drop-shadow rounded-circle" style="border: 2px solid rgba(255,255,255,0.2);" />
                  </div>

                  <h3 class="fw-bold mb-2 text-white">{{ rec.menu.name }}</h3>
                  <p class="text-white-50 mb-4">{{ rec.menu.category }}</p>

                  <div class="mb-4">
                    <span class="badge bg-primary bg-opacity-75 text-white px-3 py-2 rounded-pill">
                      <i class="fas fa-palette me-1"></i> {{ rec.color }}
                    </span>
                  </div>

                  <div class="p-3 rounded-3" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);">
                    <p class="small mb-0 text-white">{{ rec.menu.desc }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="!recommendations.length" class="col-12 text-center">
              <p class="text-white">추천할 메뉴가 없습니다.</p>
            </div>
          </div>

          <!-- Additional Recommendations -->
          <div v-if="!isLoading" class="glass-card p-4">
            <div class="d-flex align-items-center mb-4 border-bottom border-white border-opacity-10 pb-3">
              <div class="bg-primary bg-opacity-10 p-2 rounded-circle me-3">
                <i class="fas fa-utensils text-primary"></i>
              </div>
              <h5 class="mb-0 text-white">그 외 추천 메뉴</h5>
            </div>

            <div class="row text-center g-4">
              <div v-for="item in otherRecommendations" :key="item.menu.name" class="col-4 col-md-2">
                <div class="p-3 rounded-3 hover-lift transition" style="background: rgba(255,255,255,0.02);">
                  <div class="mb-2">
                    <img :src="getFoodImage(item.menu.category, item.menu.name)" :alt="item.menu.name" width="50" class="img-fluid rounded-circle" />
                  </div>
                  <h6 class="small mb-1 text-white">{{ item.menu.name }}</h6>
                  <span class="badge bg-secondary bg-opacity-50 text-white" style="font-size: 0.7rem;">{{ item.color }}</span>
                </div>
              </div>

              <div v-if="!otherRecommendations.length" class="col-12">
                <p class="text-muted">추가 추천 메뉴가 없습니다.</p>
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
</style>
