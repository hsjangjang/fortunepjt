import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/css/style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// 라우터 설정 전에 인증 상태 초기화
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
authStore.init()

app.use(router)

app.mount('#app')
