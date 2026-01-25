<template>
  <div class="card" @click="handleClick">
    <div class="card-image" :style="imageStyle"></div>
    <div class="card-body">
      <h3 class="card-title">{{ title }}</h3>
      <p class="card-desc">{{ desc }}</p >
      <div class="card-meta">
        <span class="count">{{ formattedCount }}</span>
        <span class="view">查看 →</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const props = defineProps({
  title: String,
  desc: String,
  count: [String, Number],
  to: String,
  image: String
})
const emit = defineEmits(['open'])
const formattedCount = computed(()=> Intl.NumberFormat().format(Number(props.count || 0)))
const imageStyle = computed(() => ({
  backgroundImage: props.image
    ? `linear-gradient(180deg, rgba(0,0,0,0.06), rgba(0,0,0,0)), url(${props.image})`
    : 'linear-gradient(180deg, rgba(0,0,0,0.06), rgba(0,0,0,0))'
}))
function handleClick(){
  if (props.to) {
    router.push(props.to)
  } else {
    emit('open')
    console.log('打开：', props.title)
  }
}
</script>

<style scoped>
.card{
  width: 260px;
  min-width: 260px;
  height: 700px;
  border-radius: 12px;
  overflow: hidden;
  background: white;
  border: 1px solid rgba(74, 158, 255, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display:flex;
  flex-direction:column;
  cursor:pointer;
  transition: all 0.3s ease;
}
.card:hover{ transform: translateY(-4px); box-shadow: 0 8px 24px rgba(74, 158, 255, 0.2); border-color: rgba(74, 158, 255, 0.3); }

.card-image{
  height:310px;
  background-size:cover;
  background-position:center;
  /* 这里可以放占位色或图片 */
  background-color:#ebe8ec;
}

.card-body{
  padding:18px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
  flex:1;
}
.card-title{
  font-size:28px;
  margin:0;
  color:#2d3748;
  font-weight: 600;
}
.card-desc{
  margin:10px 0 0;
  font-size:13px;
  color:#6b7280;
  height:90px;
  overflow:hidden;
}
.card-meta{
  display:flex;
  justify-content:space-between;
  align-items:center;
}
.count{
  background: rgba(74, 158, 255, 0.2);
  padding:6px 10px;
  border-radius:20px;
  font-weight:600;
  color: #4a9eff;
  font-size: 13px;
  border: 1px solid rgba(74, 158, 255, 0.3);
}
.view{ color:#4a9eff; font-size:13px; font-weight: 500; }
</style>