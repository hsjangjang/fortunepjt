<template>
  <DefaultLayout>
    <div class="page-container">
      <div class="content-wrapper">
        <!-- 페이지 헤더 -->
        <div class="page-header">
          <h1 class="page-title">
            <img src="@/assets/images/ootd-icon.png" alt="" class="page-title-icon-ootd" />
            OOTD 추천
          </h1>
          <p class="page-subtitle">날씨와 행운색 기반 오늘의 코디</p>
        </div>

        <!-- 운세 요약 카드 -->
        <div v-if="fortuneSummary || (luckyColors && luckyColors.length)" class="card-base card-sm text-center mb-5 lucky-color-card">
            <!-- 운세 요약 한줄 -->
            <p v-if="fortuneSummary" class="text-white mb-2 fortune-summary-text">
              <i class="fas fa-star-half-alt text-warning me-1"></i>
              {{ fortuneSummary }}
            </p>
            <!-- 오늘의 행운색 - 메뉴 추천과 동일한 레이아웃 -->
            <div v-if="luckyColors && luckyColors.length" class="lucky-colors-row">
              <span class="lucky-colors-label">
                <img src="@/assets/images/pallete.png" alt="" class="lucky-color-palette-icon" />
                오늘의 행운색:
              </span>
              <div class="lucky-colors-list">
                <span v-for="(color, index) in luckyColors" :key="index" class="lucky-color-badge">
                  <span class="lucky-color-dot" :style="{ background: getColorBackground(color) }"></span>
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
                  <div class="outfit-image-container mb-3">
                    <img :src="getTopImage" alt="Top" class="outfit-image" />
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
                  <div class="outfit-image-container mb-3">
                    <img :src="getBottomImage" alt="Bottom" class="outfit-image" />
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
              <div class="outfit-image-container mb-3">
                <img :src="getOuterImage" alt="Outer" class="outfit-image" />
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
              <div class="accessories-grid">
                <div v-for="acc in outfit.accessories" :key="acc.name" class="accessory-item">
                  <div class="accessory-card text-center p-3 h-100">
                    <div class="accessory-image-container mb-2">
                      <img :src="getAccessoryImage(acc.name)" alt="Accessory" class="accessory-image" />
                    </div>
                    <h6 class="text-white mt-2 mb-0 text-truncate">{{ acc.name }}</h6>
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
import { colorMap, getColorBackground } from '@/utils/colors'
import { Chart, registerables } from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'
import {
  MapPin, RefreshCw, AlertCircle, Gem,
  Sun, Cloud, CloudRain, CloudSnow, ThermometerSnowflake
} from 'lucide-vue-next'
import {
  getTopImage as getTopImageUtil,
  getBottomImage as getBottomImageUtil,
  getOuterImage as getOuterImageUtil,
  getAccessoryImage
} from '@/utils/ootdImages'

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
const getTopImage = computed(() => getTopImageUtil(outfit.value.top))

// 하의 이미지 가져오기
const getBottomImage = computed(() => getBottomImageUtil(outfit.value.bottom))

// 아우터 이미지 가져오기
const getOuterImage = computed(() => getOuterImageUtil(outfit.value.outer))


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

/* 상의/하의 카드 내부 요소 아래 정렬 */
.outfit-card .card-body {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.outfit-card .card-body .d-flex.justify-content-center {
  margin-top: auto;
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

.weather-icon-svg {
  color: #f59e0b;
  filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.5));
}

/* OOTD 페이지 타이틀 아이콘 */
.page-title-icon-ootd {
  width: 63px;
  height: 63px;
  margin-right: -8px;
  vertical-align: middle;
  object-fit: contain;
}

/* 팔레트 아이콘 */
.lucky-color-palette-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

/* 행운색 카드 내부 스타일 */
.lucky-color-card {
  padding: 1.25rem 1.5rem;
}

.fortune-summary-text {
  font-size: 1.05rem;
}

.lucky-color-label {
  font-size: 1.05rem;
}

.lucky-color-name {
  font-size: 1.05rem;
  font-weight: 500;
}

.lucky-color-dot-lg {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

/* 행운색 가로 배치 (메뉴 추천과 동일) */
.lucky-colors-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.lucky-colors-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.75);
  font-size: 1rem;
}

.lucky-colors-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}

.lucky-color-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: white;
  font-weight: 500;
}

/* 옷 이미지 고정 크기 컨테이너 */
.outfit-image-container {
  width: 160px;
  height: 160px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
}

.outfit-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

/* 액세서리 그리드 - flexbox로 가운데 정렬 */
.accessories-grid {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.accessory-item {
  flex: 0 0 auto;
  width: 140px;
}

/* 액세서리 카드 스타일 */
.accessory-card {
  background: rgba(255,255,255,0.05);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

/* 액세서리 이미지 고정 크기 컨테이너 */
.accessory-image-container {
  width: 91px;
  height: 91px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 액세서리 이름 */
.accessory-card h6 {
  width: 100%;
  text-align: center;
}

.accessory-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
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

  /* 모바일에서 액세서리 3개 가로 일렬 배치 */
  .accessories-grid {
    flex-wrap: nowrap;
    justify-content: center;
    gap: 0.25rem;
    padding: 0 0.5rem;
  }

  .accessory-item {
    flex: 0 0 30%;
    max-width: 117px;
    min-width: 0;
  }

  .accessory-card {
    padding: 0.5rem !important;
  }

  .accessory-image-container {
    width: 55px;
    height: 55px;
  }

  .accessory-card h6 {
    font-size: 0.8rem;
  }
}
</style>
