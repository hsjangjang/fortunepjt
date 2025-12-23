<template>
  <DefaultLayout>
    <div class="page-container">
      <div class="content-wrapper">
        <!-- 페이지 헤더 -->
        <div class="page-header text-center mb-5">
          <h1 class="page-title">
            <Info class="page-title-icon" :size="48" />
            사이트 소개
          </h1>
          <p class="page-subtitle">Lucky Picky가 어떻게 작동하는지 알아보세요</p>
        </div>

        <!-- How It Works -->
        <div class="glass-card mb-5 p-5">
          <h2 class="text-center mb-5">어떻게 작동하나요?</h2>
          <div class="row text-center g-4">
            <div class="col-6 col-md-3">
              <div class="step-circle mb-3">
                <span class="h4 mb-0 text-primary">1</span>
              </div>
              <h5>정보 입력</h5>
              <p class="text-muted small">생년월일과 성별 입력</p>
            </div>
            <div class="col-6 col-md-3">
              <div class="step-circle mb-3">
                <span class="h4 mb-0 text-primary">2</span>
              </div>
              <h5>운세 계산</h5>
              <p class="text-muted small">사주, 별자리 분석</p>
            </div>
            <div class="col-6 col-md-3">
              <div class="step-circle mb-3">
                <span class="h4 mb-0 text-primary">3</span>
              </div>
              <h5>AI 분석</h5>
              <p class="text-muted small">개인 맞춤 추천 생성</p>
            </div>
            <div class="col-6 col-md-3">
              <div class="step-circle mb-3">
                <span class="h4 mb-0 text-primary">4</span>
              </div>
              <h5>일상 추천</h5>
              <p class="text-muted small">색상, OOTD, 메뉴 제안</p>
            </div>
          </div>
        </div>

        <!-- 주요 기능 소개 -->
        <div class="glass-card mb-5 p-5">
          <h2 class="text-center mb-5">주요 기능</h2>
          <div class="row g-4">
            <div class="col-md-4">
              <div class="feature-box text-center p-4">
                <div class="feature-icon-wrapper mb-3">
                  <img src="@/assets/images/logo.png" alt="" class="feature-icon" />
                </div>
                <h5 class="text-white mb-2">아이템 행운도</h5>
                <p class="text-muted small mb-0">
                  내 아이템이 오늘의 행운과 얼마나 맞는지 AI가 분석합니다
                </p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="feature-box text-center p-4">
                <div class="feature-icon-wrapper mb-3">
                  <img src="@/assets/images/ootd-icon.png" alt="" class="feature-icon" />
                </div>
                <h5 class="text-white mb-2">OOTD 추천</h5>
                <p class="text-muted small mb-0">
                  행운색과 날씨를 고려한 완벽한 코디를 제안합니다
                </p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="feature-box text-center p-4">
                <div class="feature-icon-wrapper mb-3">
                  <span class="feature-emoji">🍽️</span>
                </div>
                <h5 class="text-white mb-2">메뉴 추천</h5>
                <p class="text-muted small mb-0">
                  오늘의 운세에 맞는 행운의 메뉴를 추천합니다
                </p>
              </div>
            </div>
          </div>
        </div>

        
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { Info, Sparkles } from 'lucide-vue-next'
</script>

<style scoped>
.page-header {
  padding-top: 2rem;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 2rem;
  font-weight: 700;
  color: white;
}

.page-title-icon {
  color: var(--primary);
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin-top: 0.5rem;
}

.step-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 1px solid rgba(124, 58, 237, 0.5);
  background: rgba(124, 58, 237, 0.1);
}

.feature-box {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.3s, border-color 0.3s;
}

.feature-box:hover {
  transform: translateY(-5px);
  border-color: rgba(124, 58, 237, 0.3);
}

.feature-icon-wrapper {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-icon {
  width: 72px;
  height: 72px;
  object-fit: contain;
}

.feature-emoji {
  font-size: 3.5rem;
  line-height: 1;
}
</style>
