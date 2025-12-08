<template>
  <div class="default-layout">
    <Navbar />
    <main class="main-content">
      <div class="container">
        <slot />
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
</script>

<style scoped>
.default-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  margin-top: 80px;
  padding: 20px 0;
  min-height: calc(100vh - 200px);
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
}
</style>
