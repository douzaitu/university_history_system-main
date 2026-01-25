<template>
  <section class="hero" :style="heroStyle">
    <div class="overlay"></div>
    <div class="center">
      <h1 class="title">{{ title }}</h1>
      <p class="desc" v-if="description">{{ description }}</p>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  image: String,
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  height: { type: Number, default: 300 },
  fadeColor: { type: String, default: '#1e2122' }
})
const heroStyle = computed(() => ({
  backgroundImage: props.image ? `url(${props.image})` : 'none',
  height: props.height + 'px',
  '--fade-color': props.fadeColor
}))
</script>

<style scoped>
.hero{
  position: relative;
  width: 100%;
  background-size: cover;
  background-position: center;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 28px rgba(0,0,0,0.25);
}
.overlay{
  position:absolute; inset:0;
  background: linear-gradient(180deg, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0.45) 45%, rgba(0,0,0,0.65) 70%, var(--fade-color) 100%);
}
.center{
  position:absolute; inset:0;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  text-align:center; color:#fff; padding: 0 24px;
}
.title{ margin:0 0 10px; font-size:28px; letter-spacing:1px; }
.desc{ max-width: 900px; line-height: 1.8; font-size: 14px; opacity: 0.92; }

@media (max-width: 640px){
  .title{ font-size:22px; }
  .desc{ font-size:13px; }
}
</style>