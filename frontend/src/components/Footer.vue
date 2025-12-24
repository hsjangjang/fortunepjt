<template>
  <!-- Footer - Django base.html과 동일 -->
  <footer class="footer text-center text-muted py-5 mt-5 border-top" style="border-color: var(--glass-border) !important;">
    <div class="container">
      <p class="small mb-2">Made with <i class="fas fa-heart text-danger"></i> for your lucky day</p>
      <router-link to="/about" class="footer-link">
        <i class="fas fa-info-circle me-1"></i> 사이트 소개
      </router-link>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: transparent;
}

.footer-link {
  display: inline-flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 0.85rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-link:hover {
  color: white;
  background: rgba(124, 58, 237, 0.2);
  border-color: rgba(124, 58, 237, 0.5);
}
</style>
