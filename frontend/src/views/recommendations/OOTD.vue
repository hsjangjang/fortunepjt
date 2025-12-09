<template>
  <DefaultLayout>
    <div class="row">
      <div class="col-lg-8 col-12 mx-auto px-1 px-md-3">
        <!-- Header -->
        <div class="glass-card mb-4 responsive-padding text-center py-4">
            <h1 class="display-5 fw-bold text-white">
              <i class="fas fa-tshirt me-2" style="color: #a78bfa !important;"></i> OOTD 추천
            </h1>
            <p class="lead text-white-50">날씨와 행운색 기반 오늘의 코디</p>
            <div v-if="luckyColors && luckyColors.length" class="mt-3 d-flex align-items-center justify-content-center overflow-auto flex-nowrap gap-3 pb-2" style="scrollbar-width: none;">
              <span class="text-white-50 d-inline-flex align-items-center flex-shrink-0">
                <Star class="text-warning me-1" :size="16" /> 오늘의 행운색:
              </span>
              <span v-for="color in luckyColors" :key="color" class="d-flex align-items-center text-white flex-shrink-0">
                <span class="color-dot me-2" :style="`background-color: ${colorMap[color] || '#a78bfa'}`"></span>
                {{ color }}
              </span>
            </div>
        </div>

        <!-- 라우터 가드에서 인증/운세 체크 완료 후 진입 -->
        <template v-if="authStore.isAuthenticated">
          <!-- Loading Screen -->
          <div v-if="isLoading" class="loading-overlay">
            <div class="loading-content">
              <div class="loading-spinner"></div>
              <p class="loading-text">날씨 정보를 업데이트 중입니다...</p>
            </div>
          </div>

          <!-- Weather Card -->
          <div class="weather-card" id="weatherCard">
            <div class="row">
              <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                  <MapPin class="text-primary me-2" :size="20" />
                  <span class="fs-5">{{ weather.city || '대전 유성구' }}</span>
                </div>
                <div class="current-temp mb-2" style="font-size: 3.5rem; font-weight: 700;">{{ weather.temp !== null ? Math.round(weather.temp) : '--' }}°</div>
                <div class="weather-desc">{{ weather.description || '날씨 정보 없음' }}</div>
                <div class="temp-range">
                  <span>↑{{ weather.temp_max !== null ? Math.round(weather.temp_max) : '--' }}°</span> /
                  <span>↓{{ weather.temp_min !== null ? Math.round(weather.temp_min) : '--' }}°</span>
                </div>
                <div class="mt-2 small opacity-75">체감온도 {{ weather.temp !== null ? Math.round(weather.temp) : '--' }}°</div>
              </div>
              <div class="col-md-6 d-flex flex-column justify-content-center align-items-end">
                <component :is="weatherIcon" :size="80" stroke-width="1.5" class="weather-icon-svg" />
                <button class="btn btn-outline-light btn-sm mt-3 rounded-pill px-3" @click="updateWeather">
                  <RefreshCw class="me-1" :size="14" /> 업데이트
                </button>
              </div>
            </div>

            <!-- Hourly Forecast Chart -->
            <div style="padding-bottom: 10px;">
              <div class="chart-scroll-wrapper">
                <canvas ref="weatherChart"></canvas>
              </div>
              <div class="rain-info-container" ref="rainInfoContainer"></div>
            </div>

            <div class="row mt-3 text-center small border-top pt-3 text-nowrap" style="border-color: rgba(255,255,255,0.1) !important;">
              <div class="col px-1 d-flex align-items-center justify-content-center">
                <Droplets class="text-primary me-1" :size="14" /> 강수확률 <span>{{ weather.rain_prob || 0 }}%</span>
              </div>
              <div class="col px-1 d-flex align-items-center justify-content-center">
                <Wind class="text-primary me-1" :size="14" /> 풍속 <span>{{ weather.wind_speed || 0 }}m/s</span>
              </div>
              <div class="col px-1 d-flex align-items-center justify-content-center">
                <Umbrella class="text-primary me-1" :size="14" /> 강수량 <span>{{ weather.rain_amount || 0 }}mm</span>
              </div>
            </div>
          </div>

          <!-- Main OOTD Recommendation -->
          <div class="row">
            <div class="col-md-6 mb-4">
              <div class="card glass-card outfit-card h-100 p-0">
                <div class="card-header bg-transparent border-bottom text-center" style="border-color: rgba(255,255,255,0.1);">
                  <h5 class="mb-0 text-white">오늘의 상의</h5>
                </div>
                <div class="card-body text-center responsive-padding">
                  <div class="mb-3 d-flex justify-content-center">
                    <img :src="getTopImage" alt="Top" width="100" class="img-fluid drop-shadow" />
                  </div>
                  <h4>{{ outfit.top || '니트' }}</h4>
                  <p class="text-muted">{{ outfit.top_desc || '따뜻하고 포근한 느낌' }}</p>
                  <div class="mt-3">
                    <h6 class="text-white-50 d-flex align-items-center justify-content-center mb-2">
                      <Star v-if="luckyColors" class="text-warning me-1" :size="12" />
                      {{ luckyColors ? '행운색 기반' : '추천 색상' }}
                    </h6>
                    <div class="d-flex align-items-center overflow-auto flex-nowrap gap-3 pb-2" style="scrollbar-width: none;">
                      <span class="d-flex align-items-center text-white small flex-shrink-0">
                        <span class="color-dot small me-1" :style="`background-color: ${colorMap[outfit.top_color] || '#ddd'}`"></span>
                        {{ outfit.top_color || '베이지' }}
                      </span>
                      <span v-for="color in outfit.top_alt_colors" :key="color" class="d-flex align-items-center text-white small flex-shrink-0">
                        <span class="color-dot small me-1" :style="`background-color: ${colorMap[color] || '#ddd'}`"></span>
                        {{ color }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6 mb-4">
              <div class="card glass-card outfit-card h-100">
                <div class="card-header bg-transparent border-bottom text-center" style="border-color: rgba(255,255,255,0.1);">
                  <h5 class="mb-0 text-white">오늘의 하의</h5>
                </div>
                <div class="card-body text-center">
                  <div class="mb-3 d-flex justify-content-center">
                    <img :src="getBottomImage" alt="Bottom" width="100" class="img-fluid drop-shadow" />
                  </div>
                  <h4>{{ outfit.bottom || '청바지' }}</h4>
                  <p class="text-muted">{{ outfit.bottom_desc || '편안한 일상 바지' }}</p>
                  <div class="mt-3">
                    <h6 class="text-white-50 d-flex align-items-center justify-content-center mb-2">
                      <Star v-if="luckyColors" class="text-warning me-1" :size="12" />
                      {{ luckyColors ? '행운색 기반' : '추천 색상' }}
                    </h6>
                    <div class="d-flex align-items-center overflow-auto flex-nowrap gap-3 pb-2" style="scrollbar-width: none;">
                      <span class="d-flex align-items-center text-white small flex-shrink-0">
                        <span class="color-dot small me-1" :style="`background-color: ${colorMap[outfit.bottom_color] || '#ddd'}`"></span>
                        {{ outfit.bottom_color || '블랙' }}
                      </span>
                      <span v-for="color in outfit.bottom_alt_colors" :key="color" class="d-flex align-items-center text-white small flex-shrink-0">
                        <span class="color-dot small me-1" :style="`background-color: ${colorMap[color] || '#ddd'}`"></span>
                        {{ color }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Outer Recommendation -->
          <div v-if="outfit.outer_required" class="card glass-card mb-4 outfit-card py-3">
            <div class="card-header bg-transparent border-bottom text-center mb-3" style="border-color: rgba(255,255,255,0.05) !important;">
              <h5 class="mb-0 text-white d-flex align-items-center justify-content-center">
                <AlertCircle class="text-warning me-2" :size="20" />필수 아우터
              </h5>
            </div>
            <div class="card-body text-center">
              <div class="mb-3 d-flex justify-content-center">
                <img :src="getOuterImage" alt="Outer" width="100" class="img-fluid drop-shadow" />
              </div>
              <h4>{{ outfit.outer || '코트' }}</h4>
              <p class="text-muted">{{ outfit.outer_desc || '오늘같은 날씨엔 꼭 필요합니다.' }}</p>
              <div class="d-flex justify-content-center gap-2 mt-2">
                <span class="badge dynamic-color-badge">블랙</span>
                <span class="badge dynamic-color-badge">차콜</span>
                <span class="badge dynamic-color-badge">네이비</span>
              </div>
            </div>
          </div>

          <!-- Accessories Recommendation -->
          <div v-if="outfit.accessories && outfit.accessories.length" class="card glass-card mb-4 outfit-card py-3">
            <div class="card-header bg-transparent border-bottom text-center mb-3" style="border-color: rgba(255,255,255,0.05) !important;">
              <h5 class="mb-0 text-white d-flex align-items-center justify-content-center">
                <Gem class="text-info me-2" :size="20" />추천 액세서리
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3 justify-content-center">
                <div v-for="acc in outfit.accessories" :key="acc.name" class="col-4 col-md-3">
                  <div class="text-center p-3 h-100" style="background: rgba(255,255,255,0.05); border-radius: 15px;">
                    <div class="mb-2 d-flex justify-content-center">
                      <img :src="getAccessoryImage(acc.name)" alt="Accessory" width="60" class="img-fluid drop-shadow" />
                    </div>
                    <h6 class="text-white mt-2 mb-1 text-truncate">{{ acc.name }}</h6>
                    <small class="text-muted d-block text-truncate">{{ acc.description }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import api from '@/services/api'
import { Chart, registerables } from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'
import { 
  Star, MapPin, RefreshCw, Droplets, Wind, Umbrella, 
  AlertCircle,
  Sun, Cloud, CloudRain, CloudSnow, Snowflake, ThermometerSnowflake,
  Hand, Smile
} from 'lucide-vue-next'

// 상의 이미지
import topSleeveless from '@/assets/images/ootd/top_sleeveless.png'
import topTshirt from '@/assets/images/ootd/top_tshirt.png'
import topLinenShirt from '@/assets/images/ootd/top_linen_shirt.png'
import topLongsleeve from '@/assets/images/ootd/top_longsleeve.png'
import topThinKnit from '@/assets/images/ootd/top_thin_knit.png'
import topSweatshirt from '@/assets/images/ootd/top_sweatshirt.png'
import topHoodie from '@/assets/images/ootd/top_hoodie.png'
import topShirt from '@/assets/images/ootd/top_shirt.png'
import topKnit from '@/assets/images/ootd/top_knit.png'
import topThickKnit from '@/assets/images/ootd/top_thick_knit.png'
import topTurtleneck from '@/assets/images/ootd/top_turtleneck.png'
import topFleeceSweatshirt from '@/assets/images/ootd/top_fleece_sweatshirt.png'
import topFleece from '@/assets/images/ootd/top_fleece.png'
import topPolo from '@/assets/images/ootd/top_polo.png'
import topCrop from '@/assets/images/ootd/top_crop.png'

// 하의 이미지
import bottomShorts from '@/assets/images/ootd/bottom_shorts.png'
import bottomLinen from '@/assets/images/ootd/bottom_linen.png'
import bottomCotton from '@/assets/images/ootd/bottom_cotton.png'
import bottomJeans from '@/assets/images/ootd/bottom_jeans.png'
import bottomSlacks from '@/assets/images/ootd/bottom_slacks.png'
import bottomJogger from '@/assets/images/ootd/bottom_jogger.png'
import bottomFleece from '@/assets/images/ootd/bottom_fleece.png'
import bottomCorduroy from '@/assets/images/ootd/bottom_corduroy.png'
import bottomWool from '@/assets/images/ootd/bottom_wool.png'
import bottomLeggings from '@/assets/images/ootd/bottom_leggings.png'
import bottomSkirt from '@/assets/images/ootd/bottom_skirt.png'
import bottomLongskirt from '@/assets/images/ootd/bottom_longskirt.png'
import bottomFleeceLeggings from '@/assets/images/ootd/bottom_fleece_leggings.png'
import bottomWide from '@/assets/images/ootd/bottom_wide.png'
import bottomCargo from '@/assets/images/ootd/bottom_cargo.png'

// 아우터 이미지
import outerCardigan from '@/assets/images/ootd/outer_cardigan.png'
import outerWindbreaker from '@/assets/images/ootd/outer_windbreaker.png'
import outerDenim from '@/assets/images/ootd/outer_denim.png'
import outerLeather from '@/assets/images/ootd/outer_leather.png'
import outerTrench from '@/assets/images/ootd/outer_trench.png'
import outerBlazer from '@/assets/images/ootd/outer_blazer.png'
import outerBomber from '@/assets/images/ootd/outer_bomber.png'
import outerCoat from '@/assets/images/ootd/outer_coat.png'
import outerPuffer from '@/assets/images/ootd/outer_puffer.png'
import outerLongPuffer from '@/assets/images/ootd/outer_long_puffer.png'
import outerShortPuffer from '@/assets/images/ootd/outer_short_puffer.png'
import outerShearling from '@/assets/images/ootd/outer_shearling.png'
import outerFleeceJacket from '@/assets/images/ootd/outer_fleece_jacket.png'
import outerRaincoat from '@/assets/images/ootd/outer_raincoat.png'

// 액세서리 이미지
import accScarf from '@/assets/images/ootd/acc_scarf.png'
import accGloves from '@/assets/images/ootd/acc_gloves.png'
import accBeanie from '@/assets/images/ootd/acc_beanie.png'
import accCap from '@/assets/images/ootd/acc_cap.png'
import accUmbrella from '@/assets/images/ootd/acc_umbrella.png'

// 이미지 매핑 객체
const topImageMap = {
  '민소매': topSleeveless,
  '반팔 티셔츠': topTshirt,
  '반팔': topTshirt,
  '린넨 셔츠': topLinenShirt,
  '얇은 긴팔 티': topLongsleeve,
  '얇은 긴팔': topLongsleeve,
  '긴팔': topLongsleeve,
  '얇은 니트': topThinKnit,
  '맨투맨': topSweatshirt,
  '후드티': topHoodie,
  '후드': topHoodie,
  '셔츠': topShirt,
  '니트': topKnit,
  '두꺼운 니트': topThickKnit,
  '터틀넥': topTurtleneck,
  '기모 맨투맨': topFleeceSweatshirt,
  '플리스': topFleece,
  '카라 티셔츠': topPolo,
  '폴로': topPolo,
  '크롭티': topCrop,
}

const bottomImageMap = {
  '반바지': bottomShorts,
  '숏팬츠': bottomShorts,
  '린넨 팬츠': bottomLinen,
  '린넨': bottomLinen,
  '면바지': bottomCotton,
  '청바지': bottomJeans,
  '데님': bottomJeans,
  '슬랙스': bottomSlacks,
  '정장 바지': bottomSlacks,
  '조거팬츠': bottomJogger,
  '조거': bottomJogger,
  '기모 바지': bottomFleece,
  '코듀로이 팬츠': bottomCorduroy,
  '코듀로이': bottomCorduroy,
  '울 팬츠': bottomWool,
  '울': bottomWool,
  '레깅스': bottomLeggings,
  '치마': bottomSkirt,
  '스커트': bottomSkirt,
  '롱스커트': bottomLongskirt,
  '기모 레깅스': bottomFleeceLeggings,
  '와이드 팬츠': bottomWide,
  '와이드': bottomWide,
  '카고 팬츠': bottomCargo,
  '카고': bottomCargo,
}

const outerImageMap = {
  '얇은 가디건': outerCardigan,
  '가디건': outerCardigan,
  '바람막이': outerWindbreaker,
  '윈드브레이커': outerWindbreaker,
  '청자켓': outerDenim,
  '데님 자켓': outerDenim,
  '가죽자켓': outerLeather,
  '레더 자켓': outerLeather,
  '트렌치코트': outerTrench,
  '트렌치': outerTrench,
  '블레이저': outerBlazer,
  '항공점퍼': outerBomber,
  '봄버 자켓': outerBomber,
  '코트': outerCoat,
  '패딩': outerPuffer,
  '롱패딩': outerLongPuffer,
  '숏패딩': outerShortPuffer,
  '무스탕': outerShearling,
  '플리스 자켓': outerFleeceJacket,
  '레인코트': outerRaincoat,
  '우비': outerRaincoat,
}

const accImageMap = {
  '머플러': accScarf,
  '스카프': accScarf,
  '목도리': accScarf,
  '장갑': accGloves,
  '비니': accBeanie,
  '모자': accCap,
  '캡': accCap,
  '우산': accUmbrella,
}

Chart.register(...registerables, ChartDataLabels)

const authStore = useAuthStore()
const { showToast } = useToast()
const weatherChart = ref(null)
const rainInfoContainer = ref(null)

const isLoading = ref(true)
const luckyColors = ref([])
const weather = ref({
  city: '대전 유성구',
  temp: 0,
  temp_max: 0,
  temp_min: 0,
  description: '날씨 정보 없음',
  rain_prob: 0,
  wind_speed: 0,
  rain_amount: 0
})

const outfit = ref({
  top: '니트',
  top_desc: '따뜻하고 포근한 느낌',
  top_color: '베이지',
  top_alt_colors: [],
  bottom: '청바지',
  bottom_desc: '편안한 일상 바지',
  bottom_color: '블랙',
  bottom_alt_colors: [],
  outer_required: false,
  outer: '',
  outer_desc: '',
  accessories: []
})

let chartInstance = null

const weatherIcon = computed(() => {
  const temp = weather.value.temp
  const desc = weather.value.description

  if (desc.includes('비')) return CloudRain
  if (desc.includes('눈')) return CloudSnow
  if (desc.includes('구름') || desc.includes('흐림')) return Cloud
  if (temp < 0) return ThermometerSnowflake
  return Sun
})

// 상의 이미지 가져오기
const getTopImage = computed(() => {
  const topName = outfit.value.top
  return topImageMap[topName] || topKnit
})

// 하의 이미지 가져오기
const getBottomImage = computed(() => {
  const bottomName = outfit.value.bottom
  return bottomImageMap[bottomName] || bottomJeans
})

// 아우터 이미지 가져오기
const getOuterImage = computed(() => {
  const outerName = outfit.value.outer
  return outerImageMap[outerName] || outerCoat
})

// 액세서리 이미지 가져오기
const getAccessoryImage = (name) => {
  if (!name) return accScarf
  return accImageMap[name] || accScarf
}

const colorMap = {
  '블랙': '#000000', '검은색': '#000000', '검정': '#000000', '검정색': '#000000',
  '화이트': '#FFFFFF', '흰색': '#FFFFFF', '하양': '#FFFFFF', '하얀색': '#FFFFFF',
  '그레이': '#808080', '회색': '#808080', '그래이': '#808080',
  '차콜': '#36454F',
  '네이비': '#000080', '남색': '#000080',
  '블루': '#0000FF', '파란색': '#0000FF', '파랑': '#0000FF',
  '스카이블루': '#87CEEB', '하늘색': '#87CEEB',
  '레드': '#FF0000', '빨간색': '#FF0000', '빨강': '#FF0000',
  '진한 빨간색': '#8B0000', '다크레드': '#8B0000',
  '핑크': '#FFC0CB', '분홍색': '#FFC0CB', '분홍': '#FFC0CB',
  '오렌지': '#FFA500', '주황색': '#FFA500', '주황': '#FFA500',
  '옐로우': '#FFD700', '노란색': '#FFD700', '노랑': '#FFD700',
  '골드': '#FFD700', '금색': '#FFD700', '금': '#FFD700', '황금색': '#FFD700',
  '실버': '#C0C0C0', '은색': '#C0C0C0', '은': '#C0C0C0',
  '그린': '#008000', '초록색': '#008000', '초록': '#008000', '녹색': '#008000',
  '연두색': '#9ACD32', '연두': '#9ACD32',
  '베이지': '#F5F5DC',
  '브라운': '#8B4513', '갈색': '#8B4513',
  '퍼플': '#800080', '보라색': '#800080', '보라': '#800080',
  '라벤더': '#E6E6FA', '연보라': '#E6E6FA',
  '와인': '#722F37', '버건디': '#800020', '마룬': '#800000',
  '카키': '#8B8B00', '올리브': '#808000',
  '민트': '#98FF98', '민트색': '#98FF98',
  '아이보리': '#FFFFF0', '크림': '#FFFDD0',
  '코랄': '#FF7F50', '살몬': '#FA8072',
  '터콰이즈': '#40E0D0', '청록': '#008B8B', '청록색': '#008B8B'
}

const applyDynamicColors = () => {
  nextTick(() => {
    const badges = document.querySelectorAll('.dynamic-color-badge')
    badges.forEach(badge => {
      const text = badge.textContent.trim()
      const colorCode = colorMap[text] || colorMap[text.slice(0, -1)]

      if (colorCode) {
        badge.style.backgroundColor = colorCode
        badge.style.border = '1px solid rgba(255,255,255,0.2)'

        const hex = colorCode.replace('#', '')
        const r = parseInt(hex.substr(0, 2), 16)
        const g = parseInt(hex.substr(2, 2), 16)
        const b = parseInt(hex.substr(4, 2), 16)
        const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000

        badge.style.color = (yiq >= 128) ? '#000000' : '#FFFFFF'
      } else {
        badge.style.backgroundColor = '#4a5568'
        badge.style.color = '#ffffff'
      }
    })
  })
}

const updateWeather = async () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude
        const lon = position.coords.longitude

        try {
          // OOTD API를 다시 호출하여 날씨 + 코디 모두 새로고침
          isLoading.value = true
          const response = await api.get(`/api/recommendations/ootd/?lat=${lat}&lon=${lon}`)
          const data = response.data

          if (data.success) {
            if (data.weather) updateWeatherUI(data.weather)
            if (data.lucky_colors) luckyColors.value = data.lucky_colors
            if (data.outfit) outfit.value = { ...outfit.value, ...data.outfit }
            applyDynamicColors()
            showToast('날씨 정보가 업데이트되었습니다!', 'success')
          }
        } catch (error) {
          console.error('날씨 정보 가져오기 실패:', error)
          showToast('날씨 정보를 가져올 수 없습니다.', 'error')
        } finally {
          isLoading.value = false
        }
      },
      async (error) => {
        console.error('위치 정보 획득 실패:', error)

        try {
          // 기본 위치(대전 유성구)로 OOTD API 호출
          isLoading.value = true
          const response = await api.get('/api/recommendations/ootd/?lat=36.3621&lon=127.3565')
          const data = response.data

          if (data.success) {
            if (data.weather) updateWeatherUI(data.weather)
            if (data.lucky_colors) luckyColors.value = data.lucky_colors
            if (data.outfit) outfit.value = { ...outfit.value, ...data.outfit }
            applyDynamicColors()
            showToast('대전 유성구 날씨 정보를 표시합니다.', 'success')
          }
        } catch (err) {
          console.error('기본 날씨 정보 가져오기 실패:', err)
          showToast('날씨 정보를 가져올 수 없습니다.', 'error')
        } finally {
          isLoading.value = false
        }
      }
    )
  } else {
    showToast('브라우저가 위치 정보를 지원하지 않습니다.', 'error')
  }
}

const updateWeatherUI = (data) => {
  weather.value = {
    city: data.city || '대전 유성구',
    temp: data.temp || 0,
    temp_max: data.temp_max || 0,
    temp_min: data.temp_min || 0,
    description: data.description || '날씨 정보 없음',
    rain_prob: data.current?.rain_probability || 0,
    wind_speed: data.current?.wind_speed || 0,
    rain_amount: data.current?.rain_amount || 0
  }

  if (data.hourly && data.hourly.length > 0) {
    renderChart(data.hourly)
  }
}

const renderChart = (hourlyData) => {
  if (!weatherChart.value) return

  const ctx = weatherChart.value.getContext('2d')

  if (chartInstance) {
    chartInstance.destroy()
  }

  const labels = hourlyData.map(item => item.time)
  const temps = hourlyData.map(item => item.temp)
  const rainProbs = hourlyData.map(item => item.rain_probability)

  // 강수 정보 컨테이너 비우기 (차트 afterDraw에서 위치 맞춰서 다시 채움)
  if (rainInfoContainer.value) {
    rainInfoContainer.value.innerHTML = ''
  }

  // 커스텀 플러그인: 차트 아래에 강수확률 표시
  const rainPlugin = {
    id: 'rainInfo',
    afterDraw: (chart) => {
      if (!rainInfoContainer.value) return
      rainInfoContainer.value.innerHTML = ''

      const xAxis = chart.scales.x
      const chartArea = chart.chartArea

      hourlyData.forEach((item, index) => {
        const x = xAxis.getPixelForValue(index)
        const div = document.createElement('div')
        div.className = 'rain-info-item'
        div.style.position = 'absolute'
        div.style.left = `${x}px`
        div.style.transform = 'translateX(-50%)'

        let html = `<div style="color: white;">${item.rain_probability}%</div>`
        if (item.rain_amount > 0) {
          html += `<div style="color: #81d4fa;">${item.rain_amount}mm</div>`
        }
        div.innerHTML = html
        rainInfoContainer.value.appendChild(div)
      })
    }
  }

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: '기온 (°C)',
        data: temps,
        borderColor: 'rgba(255, 255, 255, 0.9)',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(255, 255, 255, 1)',
        pointRadius: 4,
        tension: 0.4,
        fill: false,
        datalabels: {
          align: 'top',
          anchor: 'end',
          color: 'white',
          font: {
            weight: 'bold',
            size: 12
          },
          formatter: function(value) {
            return Math.round(value) + '°'
          }
        }
      }]
    },
    plugins: [rainPlugin],
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
        datalabels: { display: true }
      },
      scales: {
        x: {
          grid: { display: false, drawBorder: false },
          ticks: {
            color: 'rgba(255, 255, 255, 0.8)',
            maxRotation: 0,
            minRotation: 0,
            autoSkip: true,
            maxTicksLimit: 8,
            font: { size: 11 }
          }
        },
        y: {
          display: false,
          min: Math.min(...temps) - 5,
          max: Math.max(...temps) + 5
        }
      },
      layout: {
        padding: { left: 25, right: 25, top: 20, bottom: 10 }
      }
    }
  })
}

const fetchOOTD = async (lat = null, lon = null) => {
  try {
    isLoading.value = true

    // 위치 정보가 있으면 쿼리 파라미터로 전달
    let url = '/api/recommendations/ootd/'
    if (lat !== null && lon !== null) {
      url += `?lat=${lat}&lon=${lon}`
    }

    const response = await api.get(url)
    const data = response.data

    if (data.lucky_colors) luckyColors.value = data.lucky_colors
    if (data.weather) updateWeatherUI(data.weather)
    if (data.outfit) outfit.value = { ...outfit.value, ...data.outfit }

    applyDynamicColors()
  } catch (error) {
    console.error('OOTD 정보 가져오기 실패:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  // 운세 체크는 라우터 가드에서 처리됨 (requiresFortune: true)

  // Geolocation으로 위치 정보 가져오기
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lon = position.coords.longitude
        console.log('[OOTD] 위치 정보 획득:', lat, lon)
        fetchOOTD(lat, lon)
      },
      (error) => {
        console.warn('[OOTD] 위치 정보 획득 실패, 기본값 사용:', error.message)
        // 위치 정보 실패 시 기본값으로 호출
        fetchOOTD()
      },
      {
        enableHighAccuracy: false,
        timeout: 5000,
        maximumAge: 300000  // 5분간 캐시 사용
      }
    )
  } else {
    console.warn('[OOTD] Geolocation 미지원, 기본값 사용')
    fetchOOTD()
  }

  applyDynamicColors()
})
</script>

<style scoped>
.weather-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 25px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  position: relative;
  overflow: hidden;
}

.weather-card::before {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  filter: blur(50px);
}

.current-temp {
  font-size: 72px;
  font-weight: bold;
  line-height: 1;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.weather-desc {
  font-size: 24px;
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.9);
}

.temp-range {
  font-size: 18px;
  opacity: 0.7;
}

.chart-scroll-wrapper {
  width: 100%;
  height: 180px;
  margin-top: 20px;
  padding: 10px 0;
}

.rain-info-container {
  position: relative;
  height: 35px;
  margin-top: 5px;
  font-size: 11px;
  opacity: 0.7;
  width: 100%;
}

.rain-info-item {
  text-align: center;
}

.outfit-card {
  border-radius: 20px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
  transition: transform 0.3s;
  overflow: hidden;
}

.outfit-card:hover {
  transform: translateY(-5px);
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.3);
  display: inline-block;
}

.color-dot.small {
  width: 10px;
  height: 10px;
}

.weather-icon-svg {
  color: #f59e0b;
  filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.5));
}

/* Loading Screen Styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 15, 35, 0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(124, 58, 237, 0.3);
  border-top: 4px solid #7c3aed;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #ffffff;
  font-size: 18px;
  font-weight: 500;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .responsive-padding {
    padding-left: 3% !important;
    padding-right: 3% !important;
  }
  
  /* Apply to weather card specifically if it uses fixed padding */
  .weather-card {
    padding: 1.5rem !important; /* Reduce from whatever it was */
  }
  
  .glass-card {
    border-radius: 12px;
  }
}
</style>
