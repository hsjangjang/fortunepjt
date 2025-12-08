<template>
  <DefaultLayout>
    <div class="not-found-page">
      <div class="not-found-content">
        <i class="fas fa-ghost"></i>
        <h1>404</h1>
        <h2>페이지를 찾을 수 없습니다</h2>
        <p>요청하신 페이지가 존재하지 않거나 이동되었습니다.</p>
        <router-link to="/" class="btn btn-primary">
          <i class="fas fa-home"></i> 홈으로 돌아가기
        </router-link>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
</script>

<style scoped>
.not-found-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 400px);
  padding: 2rem 1rem;
}

.not-found-content {
  text-align: center;
  color: white;
}

.not-found-content i {
  font-size: 6rem;
  margin-bottom: 1rem;
  opacity: 0.8;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.not-found-content h1 {
  font-size: 6rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.not-found-content h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.not-found-content p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.btn {
  padding: 0.75rem 2rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}
</style>
