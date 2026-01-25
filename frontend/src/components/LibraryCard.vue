<template>
  <div class="lib-card" @click="handleClick">
  <!-- 查看按钮在右上角 -->
  <div class="view-link">查看 →</div>
  
  <!-- 阅读量在左上角 -->
  <div class="count-indicator">{{ formattedCount }}</div>
  
  <div class="thumb">
    <div v-if="loading" class="loading-placeholder">
      <div class="skeleton"></div>
    </div>
    <img 
      v-if="imageUrl" 
      :src="imageUrl" 
      :alt="title"
      @load="onImageLoad"
      @error="onImageError"
      class="card-image"
      loading="lazy"
    />
    <div v-else class="no-image">
      <span class="no-image-text">{{ getInitials(title) }}</span>
    </div>
  </div>
  <div class="info">
    <h3 class="title">{{ title || '未知姓名' }}</h3>
    <p class="subtitle" v-if="subtitle">{{ subtitle }}</p>
  </div>
  <div v-if="isFavorite" class="favorite-indicator">❤️</div>
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
  imageUrl.value = null // 使用文字占位符
}

// 处理点击事件
const handleClick = (event) => {
  // 阻止事件冒泡
  event.stopPropagation()
  
  if (props.to) {
    router.push(props.to)
  }
}
</script>

<style scoped>
.lib-card{
  width: 100%;
  min-width: 240px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.lib-card:hover{
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.thumb{
  height: 200px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border-radius: 0;
}

.loading-placeholder{
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skeleton{
  width: 90%;
  height: 90%;
  background: linear-gradient(90deg, #e0e0e0 25%, #f0f0f0 50%, #e0e0e0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 12px;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.card-image{
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  background: white;
  padding: 20px;
  transition: transform 0.2s ease;
  border-radius: 0;
}

.lib-card:hover .card-image{
  transform: scale(1.08);
}

.no-image{
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
}

.no-image-text{
  font-size: 56px;
  font-weight: bold;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  letter-spacing: -2px;
}

.info{
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 0 0 16px 16px;
}

.title{
  margin: 0;
  font-size: 24px;
  color: #2d3748;
  font-weight: 700;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: -0.5px;
}

.subtitle{
  margin: 8px 0 16px;
  font-size: 14px;
  color: #6b7280;
  padding: 0;
  border-radius: 0;
  align-self: flex-start;
  font-weight: 500;
  transition: all 0.3s ease;
  background: transparent;
}

.lib-card:hover .subtitle{
  color: #475569;
}

.meta{
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.count{
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  color: #0369a1;
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.lib-card:hover .count{
  background: linear-gradient(135deg, #bae6fd 0%, #bfdbfe 100%);
}

.view{
  font-size: 13px;
  color: #4a9eff;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.lib-card:hover .view{
  color: #1677ff;
  transform: translateX(4px);
}

.favorite-indicator{
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 20px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
  z-index: 10;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.lib-card:hover .favorite-indicator{
  transform: scale(1.1);
}

.view-link {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.9);
  color: #4a9eff;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  border: 1px solid rgba(74, 158, 255, 0.2);
}

.lib-card:hover .view-link {
  background: #4a9eff;
  color: white;
  transform: scale(1.05);
}

.count-indicator {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 255, 255, 0.9);
  color: #6b7280;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .lib-card{
    min-width: unset;
  }
  
  .thumb{
    height: 180px;
  }
  
  .title{
    font-size: 18px;
  }
  
  .info{
    padding: 16px;
  }
  
  .view-link, .count-indicator {
    font-size: 11px;
    padding: 5px 10px;
  }
}
</style>