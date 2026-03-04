<template>
  <div class="lib-card" @click="handleClick">
    <div class="thumb">
      <div v-if="loading" class="loading-placeholder">
        <div class="skeleton"></div>
      </div>
      <img 
        :src="imageUrl || '/People/default.jpg'" 
        :alt="title"
        @load="onImageLoad"
        @error="onImageError"
        class="card-image"
        loading="lazy"
      />
    </div>
    <div class="info">
      <h3 class="title">{{ title || '未知姓名' }}</h3>
      <p class="subtitle" v-if="subtitle">{{ subtitle }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const props = defineProps({
  title: String,
  subtitle: String,
  image: String,
  count: [String, Number],
  to: String,
  favorite: Boolean
})

const loading = ref(true)
const imageUrl = ref(props.image)

// 计算是否为收藏
const isFavorite = computed(() => {
  if (props.favorite !== undefined) return props.favorite
  
  // 从localStorage获取收藏状态
  const favorites = JSON.parse(localStorage.getItem('favoritePeople') || '[]')
  // 尝试从to属性中提取ID
  if (props.to && props.to.startsWith('/people/')) {
    const id = props.to.split('/').pop()
    return favorites.includes(id)
  }
  return false
})

// 格式化计数
const formattedCount = computed(() => {
  const count = Number(props.count || 0)
  if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'k'
  }
  return Intl.NumberFormat().format(count)
})

// 获取姓名首字母作为默认显示
const getInitials = (name) => {
  if (!name || typeof name !== 'string') return '?'
  
  // 对于中文名，返回姓
  if (/^[\u4e00-\u9fa5]/.test(name)) {
    return name.charAt(0)
  }
  
  // 对于英文名，返回首字母
  return name.charAt(0).toUpperCase()
}

// 处理图片加载
const onImageLoad = () => {
  loading.value = false
}

// 处理图片错误
const onImageError = () => {
  loading.value = false
  imageUrl.value = '/People/default.jpg' // 使用默认图片
}

// 处理点击事件
const handleClick = (event) => {
  // 阻止事件冒泡
  event.stopPropagation()
  
  if (props.to) {
    window.open(props.to, '_blank', 'noopener,noreferrer')
  }
}
</script>

<style scoped>
.lib-card{
  width: 100%;
  background: white;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.lib-card:hover{
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.thumb{
  aspect-ratio: 1 / 1;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
  border: 1px solid #e5e7eb;
  padding: 10px;
}

.loading-placeholder{
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
}

.skeleton{
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, #e0e0e0 25%, #f0f0f0 50%, #e0e0e0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.card-image{
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top;
  display: block;
  border: 1px solid #e5e7eb;
  background: white;
}

.no-image{
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e5e7eb;
  color: #6b7280;
}

.no-image-text{
  font-size: 48px;
  font-weight: bold;
}

.info{
  padding: 16px;
  text-align: center;
  background: white;
}

.title{
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #2d3748;
  font-weight: 600;
  line-height: 1.2;
}

.subtitle{
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  font-weight: 400;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .thumb{
    height: 180px;
  }
  
  .info{
    padding: 12px;
  }
  
  .title{
    font-size: 14px;
  }
  
  .subtitle{
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .thumb{
    height: 160px;
  }
  
  .info{
    padding: 10px;
  }
  
  .title{
    font-size: 13px;
  }
  
  .subtitle{
    font-size: 11px;
  }
}
</style>