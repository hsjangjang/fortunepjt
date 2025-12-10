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
            <!-- 운세 요약 한줄 -->
            <p v-if="fortuneSummary" class="text-white mt-2 mb-2" style="font-size: 0.95rem;">
              <i class="fas fa-star-half-alt text-warning me-1"></i>
              {{ fortuneSummary }}
            </p>
            <div v-if="luckyColors && luckyColors.length" class="mt-3">
              <div class="d-flex flex-wrap align-items-center justify-content-center gap-2">
                <Star class="text-warning" :size="16" />
                <span v-for="color in luckyColors" :key="color" class="badge dynamic-color-badge">
                  {{ color }}
                </span>
              </div>
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
            <div class="hourly-forecast-section">
              <div class="hourly-scroll-container">
                <!-- 아이콘 행 -->
                <div class="hourly-icons" ref="hourlyIcons">
                  <!-- 동적으로 생성됨 -->
                </div>
                <!-- 온도 라인 그래프 (아이콘과 온도 사이) -->
                <div class="chart-container">
                  <canvas ref="tempChart"></canvas>
                </div>
                <!-- 온도/시간/강수확률 행 -->
                <div class="hourly-details" ref="hourlyDetails">
                  <!-- 동적으로 생성됨 -->
                </div>
              </div>
            </div>
          </div>

          <!-- Main OOTD Recommendation -->
          <div class="row">
            <div class="col-md-6 mb-4">
              <div class="card glass-card outfit-card h-100 py-3">
                <div class="card-header bg-transparent border-bottom text-center mb-3" style="border-color: rgba(255,255,255,0.05) !important;">
                  <h5 class="mb-0 text-white">오늘의 상의</h5>
                </div>
                <div class="card-body text-center">
                  <div class="mb-3 d-flex justify-content-center">
                    <img :src="getTopImage" alt="Top" width="100" class="img-fluid drop-shadow" />
                  </div>
                  <h4>{{ outfit.top || '니트' }}</h4>
                  <p class="text-muted">{{ outfit.top_desc || '따뜻하고 포근한 느낌' }}</p>
                  <div class="d-flex justify-content-center gap-2 mt-2 flex-wrap">
                    <span class="badge dynamic-color-badge">{{ outfit.top_color || '베이지' }}</span>
                    <span v-for="color in outfit.top_alt_colors" :key="color" class="badge dynamic-color-badge">{{ color }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6 mb-4">
              <div class="card glass-card outfit-card h-100 py-3">
                <div class="card-header bg-transparent border-bottom text-center mb-3" style="border-color: rgba(255,255,255,0.05) !important;">
                  <h5 class="mb-0 text-white">오늘의 하의</h5>
                </div>
                <div class="card-body text-center">
                  <div class="mb-3 d-flex justify-content-center">
                    <img :src="getBottomImage" alt="Bottom" width="100" class="img-fluid drop-shadow" />
                  </div>
                  <h4>{{ outfit.bottom || '청바지' }}</h4>
                  <p class="text-muted">{{ outfit.bottom_desc || '편안한 일상 바지' }}</p>
                  <div class="d-flex justify-content-center gap-2 mt-2 flex-wrap">
                    <span class="badge dynamic-color-badge">{{ outfit.bottom_color || '블랙' }}</span>
                    <span v-for="color in outfit.bottom_alt_colors" :key="color" class="badge dynamic-color-badge">{{ color }}</span>
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
import { colorMap } from '@/utils/colors'
import { Chart, registerables } from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'
import {
  Star, MapPin, RefreshCw, AlertCircle,
  Sun, Cloud, CloudRain, CloudSnow, ThermometerSnowflake
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
const hourlyIcons = ref(null)
const hourlyDetails = ref(null)
const tempChart = ref(null)
let chartInstance = null

const isLoading = ref(true)
const luckyColors = ref([])
const fortuneSummary = ref('')
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
            if (data.fortune_summary) fortuneSummary.value = data.fortune_summary
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
            if (data.fortune_summary) fortuneSummary.value = data.fortune_summary
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
    renderHourlyForecast(data.hourly)
  }
}

// 날씨 아이콘 SVG 반환 (sky: 하늘상태, pty: 강수형태)
const getWeatherIconSvg = (sky, pty, isMobile = false) => {
  // pty(강수형태): 0=없음, 1=비, 2=비/눈, 3=눈, 4=소나기
  // sky(하늘상태): 1=맑음, 3=구름많음, 4=흐림
  const size = isMobile ? 18 : 24
  if (pty === 1 || pty === 4) {
    // 비 또는 소나기
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#81d4fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M16 14v6"/><path d="M8 14v6"/><path d="M12 16v6"/></svg>`
  }
  if (pty === 2 || pty === 3) {
    // 눈 또는 비/눈
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M8 15h.01"/><path d="M8 19h.01"/><path d="M12 17h.01"/><path d="M12 21h.01"/><path d="M16 15h.01"/><path d="M16 19h.01"/></svg>`
  }
  if (sky === 1) {
    // 맑음
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>`
  }
  if (sky === 3) {
    // 구름많음 (해+구름)
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="M20 12h2"/><path d="m19.07 4.93-1.41 1.41"/><circle cx="12" cy="10" r="4"/><path d="M4 15.5a3.5 3.5 0 0 1 3.5-3.5c.36 0 .72.05 1.05.15A5.5 5.5 0 0 1 18.5 14a4 4 0 0 1 .22 7.99H6a4 4 0 0 1-.22-7.99" stroke="#9ca3af"/></svg>`
  }
  // 흐림 (sky === 4 또는 기본)
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>`
}

// 시간별 예보 렌더링 (아이콘 행 / 그래프 / 온도+시간+강수확률 행 분리)
const renderHourlyForecast = (hourlyData) => {
  if (!hourlyIcons.value || !hourlyDetails.value) return

  hourlyIcons.value.innerHTML = ''
  hourlyDetails.value.innerHTML = ''

  const isMobile = window.innerWidth <= 768
  const dataCount = hourlyData.length // 실제 데이터 개수 (보통 12개)

  // 모바일: 6개가 화면에 보이고, 12개 데이터면 200% 너비로 스크롤
  // 웹: 12개 모두 화면에 표시
  const containerWidthPercent = isMobile ? (dataCount / 6) * 100 : 100

  // 컨테이너에 인라인 스타일 적용 (모바일에서 스크롤을 위해 너비 확장)
  hourlyIcons.value.style.cssText = `display: flex; gap: 0; width: ${containerWidthPercent}%;`
  hourlyDetails.value.style.cssText = `display: flex; gap: 0; width: ${containerWidthPercent}%;`

  // 각 아이템은 컨테이너의 1/dataCount 너비
  const itemWidth = `${100 / dataCount}%`

  hourlyData.forEach((item) => {
    // 아이콘 행 아이템
    const iconItem = document.createElement('div')
    iconItem.style.cssText = `
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex: 0 0 ${itemWidth};
      min-width: ${itemWidth};
      max-width: ${itemWidth};
      padding: ${isMobile ? '4px 2px' : '6px 4px'};
      box-sizing: border-box;
    `
    const iconDiv = document.createElement('div')
    iconDiv.innerHTML = getWeatherIconSvg(item.sky, item.pty, isMobile)
    iconItem.appendChild(iconDiv)
    hourlyIcons.value.appendChild(iconItem)

    // 상세 정보 행 아이템 (온도, 시간, 강수확률)
    const detailItem = document.createElement('div')
    detailItem.style.cssText = `
      display: flex;
      flex-direction: column;
      align-items: center;
      flex: 0 0 ${itemWidth};
      min-width: ${itemWidth};
      max-width: ${itemWidth};
      padding: ${isMobile ? '4px 2px' : '6px 4px'};
      box-sizing: border-box;
    `

    // 온도
    const tempDiv = document.createElement('div')
    tempDiv.style.cssText = `font-size: ${isMobile ? '14px' : '16px'}; font-weight: 600; color: white; margin-bottom: 4px;`
    tempDiv.textContent = `${Math.round(item.temp)}°`

    // 시간
    const timeDiv = document.createElement('div')
    timeDiv.style.cssText = `font-size: ${isMobile ? '10px' : '11px'}; color: rgba(255, 255, 255, 0.7); margin-bottom: 4px;`
    timeDiv.textContent = item.time

    // 강수확률
    const probDiv = document.createElement('div')
    probDiv.style.cssText = `font-size: ${isMobile ? '10px' : '11px'}; color: #81d4fa;`
    probDiv.textContent = `${item.rain_probability}%`

    detailItem.appendChild(tempDiv)
    detailItem.appendChild(timeDiv)
    detailItem.appendChild(probDiv)
    hourlyDetails.value.appendChild(detailItem)
  })

  // 온도 라인 차트 렌더링 (데이터 개수와 컨테이너 너비 전달)
  renderTempChart(hourlyData, containerWidthPercent)
}

// 온도 라인 차트 렌더링
const renderTempChart = (hourlyData, containerWidthPercent = 100) => {
  if (!tempChart.value) return

  // 기존 차트 제거
  if (chartInstance) {
    chartInstance.destroy()
  }

  // 차트 컨테이너 너비 설정 (모바일에서 스크롤을 위해)
  const chartContainer = tempChart.value.parentElement
  if (chartContainer) {
    chartContainer.style.width = `${containerWidthPercent}%`
  }

  const ctx = tempChart.value.getContext('2d')
  const temps = hourlyData.map(item => Math.round(item.temp))
  const labels = hourlyData.map(item => item.time)

  // 실제 렌더링될 차트 너비 기준으로 패딩 계산
  const scrollContainer = chartContainer?.parentElement
  const visibleWidth = scrollContainer?.clientWidth || 600
  // 한 아이템의 보이는 너비 (모바일: 화면의 1/6, 웹: 화면의 1/12)
  const isMobile = window.innerWidth <= 768
  const visibleItemCount = isMobile ? 6 : 12
  const itemVisibleWidth = visibleWidth / visibleItemCount
  // 좌우 패딩 = 아이템 너비의 절반 (점이 컬럼 중앙에 오도록)
  const sidePadding = itemVisibleWidth / 2

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        data: temps,
        borderColor: '#ffffff',
        borderWidth: 2,
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4,
        pointRadius: 3,
        pointBackgroundColor: '#ffffff',
        pointBorderColor: '#ffffff',
        pointHoverRadius: 5,
        pointHoverBackgroundColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: {
          left: sidePadding,
          right: sidePadding
        }
      },
      plugins: {
        legend: { display: false },
        datalabels: { display: false },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          titleColor: '#fff',
          bodyColor: '#fff',
          displayColors: false,
          callbacks: {
            label: (context) => `${context.raw}°C`
          }
        }
      },
      scales: {
        x: { display: false },
        y: {
          display: false,
          min: Math.min(...temps) - 2,
          max: Math.max(...temps) + 2
        }
      },
      interaction: {
        intersect: false,
        mode: 'index'
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
    if (data.fortune_summary) fortuneSummary.value = data.fortune_summary
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

/* 시간별 예보 섹션 */
.hourly-forecast-section {
  margin-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 15px;
}

.hourly-scroll-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.hourly-scroll-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari */
}

.hourly-icons {
  display: flex;
  gap: 0;
}

.hourly-details {
  display: flex;
  gap: 0;
}

.chart-container {
  height: 50px;
  margin: 0;
  padding: 0 4px;
}

.hourly-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 0 0 calc(100% / 12); /* 웹: 12개 모두 표시 */
  min-width: calc(100% / 12);
  max-width: calc(100% / 12);
  padding: 8px 4px;
  box-sizing: border-box;
}

.hourly-icon {
  margin-bottom: 8px;
}

.hourly-temp {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
}

.hourly-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 6px;
}

.hourly-prob {
  font-size: 11px;
  color: #81d4fa;
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
    padding: 1.5rem !important;
  }

  .glass-card {
    border-radius: 12px;
  }

  /* 모바일에서 시간별 예보: 6개만 보이고 스크롤 */
  .hourly-item {
    flex: 0 0 calc(100% / 6) !important; /* 모바일: 6개만 화면에 표시 */
    min-width: calc(100% / 6) !important;
    max-width: calc(100% / 6) !important;
    padding: 6px 2px;
  }

  .hourly-icon {
    margin-bottom: 4px;
  }

  .hourly-icon svg {
    width: 18px;
    height: 18px;
  }

  .hourly-temp {
    font-size: 14px;
  }

  .hourly-time {
    font-size: 10px;
  }

  .hourly-prob {
    font-size: 10px;
  }
}
</style>
