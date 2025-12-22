<template>
  <DefaultLayout>
    <!-- Hero Section -->
    <div class="row align-items-center mb-5 py-5">
      <div class="col-lg-8 mx-auto text-center">
        <div class="mb-4 animate-float">
        </div>
        <h1 class="display-title fw-bold mb-4">
          행운을 PICK<span class="star-icon">✨</span><br>당신의 하루를 열어보아요
        </h1>
        <p class="lead text-muted mb-5">
          사주와 별자리를 분석하여<br>
          당신에게 딱 맞는 <span class="text-white fw-bold">행운의 아이템, OOTD, 메뉴</span>를 추천해드립니다
        </p>
        <div class="d-flex justify-content-center gap-3">
          <router-link to="/fortune/calculate" class="btn btn-primary btn-lg px-5 fortune-loading-link">
            <i class="fas fa-calendar-check me-2"></i> 운세 보기
          </router-link>
        </div>
      </div>
    </div>

    <!-- Main Features -->
    <div id="features" class="row mb-5 g-4">
      <!-- 오늘의 운세 -->
      <div class="col-md-4">
        <div class="glass-card h-100 p-4 text-center position-relative overflow-hidden feature-card">
          <div class="position-absolute top-0 start-50 translate-middle-x mt-n4" style="width: 100px; height: 100px; background: var(--primary); filter: blur(60px); opacity: 0.4;"></div>
          <div class="feature-content">
            <div class="mb-4 mt-3">
              <img src="@/assets/images/logo.png" alt="" class="feature-icon" />
            </div>
            <h4 class="mb-3">아이템 행운도</h4>
            <p class="text-muted mb-0">
              내 아이템이 오늘의 행운과<br>
              얼마나 맞는지 AI가 분석합니다
            </p>
          </div>
          <router-link to="/fortune/item-check" class="btn btn-outline-light w-100 feature-btn stretched-link">
            행운도 측정하기
          </router-link>
        </div>
      </div>

      <!-- OOTD 추천 -->
      <div class="col-md-4">
        <div class="glass-card h-100 p-4 text-center position-relative overflow-hidden feature-card">
          <div class="position-absolute top-0 start-50 translate-middle-x mt-n4" style="width: 100px; height: 100px; background: var(--success); filter: blur(60px); opacity: 0.3;"></div>
          <div class="feature-content">
            <div class="mb-4 mt-3">
              <img src="@/assets/images/ootd-icon.png" alt="" class="feature-icon" />
            </div>
            <h4 class="mb-3">OOTD 추천</h4>
            <p class="text-muted mb-0">
              행운색과 날씨를 고려한<br>
              완벽한 코디를 제안합니다
            </p>
          </div>
          <router-link to="/recommendations/ootd" class="btn btn-outline-light w-100 feature-btn stretched-link">
            코디 추천받기
          </router-link>
        </div>
      </div>

      <!-- 메뉴 추천 -->
      <div class="col-md-4">
        <div class="glass-card h-100 p-4 text-center position-relative overflow-hidden feature-card">
          <div class="position-absolute top-0 start-50 translate-middle-x mt-n4" style="width: 100px; height: 100px; background: var(--warning); filter: blur(60px); opacity: 0.3;"></div>
          <div class="feature-content">
            <div class="mb-4 mt-3" style="font-size: 3.5rem;">🍽️</div>
            <h4 class="mb-3">메뉴 추천</h4>
            <p class="text-muted mb-0">
              오늘의 운세에 맞는<br>
              행운의 메뉴를 추천합니다
            </p>
          </div>
          <router-link to="/recommendations/menu" class="btn btn-outline-light w-100 feature-btn stretched-link">
            메뉴 추천받기
          </router-link>
        </div>
      </div>
    </div>

    <!-- How It Works -->
    <div class="glass-card mb-5 p-5">
      <h2 class="text-center mb-5">어떻게 작동하나요?</h2>
      <div class="row text-center g-4">
        <div class="col-6 col-md-3">
          <div class="d-inline-flex align-items-center justify-content-center rounded-circle border border-primary border-opacity-50 mb-3" style="width: 60px; height: 60px; background: rgba(124, 58, 237, 0.1);">
            <span class="h4 mb-0 text-primary">1</span>
          </div>
          <h5>정보 입력</h5>
          <p class="text-muted small">생년월일과 성별 입력</p>
        </div>
        <div class="col-6 col-md-3">
          <div class="d-inline-flex align-items-center justify-content-center rounded-circle border border-primary border-opacity-50 mb-3" style="width: 60px; height: 60px; background: rgba(124, 58, 237, 0.1);">
            <span class="h4 mb-0 text-primary">2</span>
          </div>
          <h5>운세 계산</h5>
          <p class="text-muted small">사주, 별자리 분석</p>
        </div>
        <div class="col-6 col-md-3">
          <div class="d-inline-flex align-items-center justify-content-center rounded-circle border border-primary border-opacity-50 mb-3" style="width: 60px; height: 60px; background: rgba(124, 58, 237, 0.1);">
            <span class="h4 mb-0 text-primary">3</span>
          </div>
          <h5>AI 분석</h5>
          <p class="text-muted small">개인 맞춤 추천 생성</p>
        </div>
        <div class="col-6 col-md-3">
          <div class="d-inline-flex align-items-center justify-content-center rounded-circle border border-primary border-opacity-50 mb-3" style="width: 60px; height: 60px; background: rgba(124, 58, 237, 0.1);">
            <span class="h4 mb-0 text-primary">4</span>
          </div>
          <h5>일상 추천</h5>
          <p class="text-muted small">색상, OOTD, 메뉴 제안</p>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
</script>

<style scoped>
/* 피처 아이콘 */
.feature-icon {
  width: 72px;
  height: 72px;
  object-fit: contain;
}

/* 별 아이콘 노란색 - 이모지는 filter 대신 text-shadow 사용 */
.star-icon {
  text-shadow: 0 0 10px rgba(251, 191, 36, 0.8), 0 0 20px rgba(251, 191, 36, 0.5);
}

/* 메인 피처 카드: 내용은 상단에, 버튼만 아래 고정 */
.feature-card {
  display: flex;
  flex-direction: column;
}

.feature-content {
  flex-shrink: 0;
}

.feature-btn {
  margin-top: auto;
  padding-top: 1.5rem;
}
</style>
