<template>
  <div class="lucky-item-card text-center p-4 h-100"
       style="background: rgba(124, 58, 237, 0.15); border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 15px; cursor: pointer;"
       @click.stop.prevent="toggleDesc">
    <div class="mb-2">
      <span class="badge" style="background: #a78bfa; color: white;">{{ badge }}</span>
    </div>
    <img v-if="image"
         :src="image"
         :alt="name"
         class="lucky-item-img d-block mb-3 mx-auto">
    <span v-else class="lucky-item-icon d-block mb-3">{{ emoji }}</span>
    <h5 class="text-white fw-bold mb-2" style="word-break: keep-all;">{{ name }}</h5>
    <div class="item-desc-toggle" :class="{ 'show': showDesc }">
      <p class="text-white opacity-75 small mb-0" v-html="formattedDescription"></p>
    </div>
    <div class="toggle-hint mt-2">
      <i class="fas" :class="showDesc ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
      <span class="small text-white opacity-50 ms-1">{{ showDesc ? '접기' : '설명 보기' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { formatDescription } from '@/utils/fortuneLoader'

const props = defineProps({
  badge: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  image: {
    type: String,
    default: null
  },
  emoji: {
    type: String,
    default: '🎁'
  }
})

const showDesc = ref(false)

const toggleDesc = () => {
  showDesc.value = !showDesc.value
}

const formattedDescription = computed(() => {
  return formatDescription(props.description || '', props.name)
})
</script>

<style scoped>
.lucky-item-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.lucky-item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
}

.lucky-item-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
}

.lucky-item-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
}

.item-desc-toggle {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out, opacity 0.3s ease-out, margin 0.3s ease-out;
  opacity: 0;
  margin-top: 0;
}

.item-desc-toggle.show {
  max-height: 200px;
  opacity: 1;
  margin-top: 15px;
}

.item-desc-toggle p {
  padding: 15px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  line-height: 1.6;
}

.toggle-hint {
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.2s;
}

.lucky-item-card:hover .toggle-hint {
  color: rgba(255, 255, 255, 0.8);
}

@media (max-width: 768px) {
  .lucky-item-card {
    padding: 0.75rem !important;
  }

  .lucky-item-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem !important;
  }

  .lucky-item-img {
    width: 50px;
    height: 50px;
    margin-bottom: 0.5rem !important;
  }

  .lucky-item-card h5 {
    font-size: 0.9rem;
  }

  .lucky-item-card .badge {
    font-size: 0.65rem;
    padding: 0.25rem 0.5rem;
  }

  .toggle-hint {
    font-size: 0.7rem;
  }

  .item-desc-toggle p {
    font-size: 0.75rem;
    padding: 10px;
  }
}
</style>
