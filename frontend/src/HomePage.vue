<template>
  <div class="home">
    <div class="topbar">
      <div class="logo-section">
        <img src="/logo.svg" alt="成都理工大学" class="logo" />
        <div class="logo-text">
          <div class="university-name">成都理工大学</div>
          <div class="system-name">数字记忆</div>
        </div>
      </div>
      <div class="nav-section">
        <div class="site-title">
          首页 <span class="sub">dm.cdut.edu.cn</span>
        </div>
      </div>
      <div class="actions">
      </div>
    </div>

    <div class="main-content">
      <h1 class="page-title">校史馆数字记忆 · 首页</h1>

      <div class="card-row">
        <Card title="人物" desc="以知识图谱形式收录计算机与网络安全学院相关人物" count="41" to="/people" image="/HomePage/peopel.jpg" />
        <Card title="地点" desc="收录与计算机与网络安全学院相关的地理位置、建筑等" count="1" to="/places" image="/HomePage/place.jpg" />
        <Card title="学科" desc="学科库为用户提供了解计算机与网络安全学院学科的信息" count="1" to="/subjects" image="/HomePage/subject.gif" />
        <Card title="机构" desc="收录与计算机与网络安全学院相关的组织和机构资料" count="1" to="/organizations" image="/HomePage/机构.jpg" />
        <Card title="事件" desc="记录与计算机与网络安全学院相关的重要事件" count="1" to="/events" image="/HomePage/事件.jpg" />
      </div>
    </div>
  </div>
</template>

<script setup>
import Card from './components/Card.vue'
</script>

<style scoped>
.home{
  min-height:100vh;
  padding:0;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
  position: relative;
  overflow-x: hidden;
  box-sizing:border-box;
  color: #2d3748;
}

/* 添加微妙的背景纹理效果 */
.home::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 20% 80%, rgba(74, 158, 255, 0.05) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(74, 158, 255, 0.05) 0%, transparent 50%),
              radial-gradient(circle at 40% 40%, rgba(74, 158, 255, 0.03) 0%, transparent 50%);
  z-index: -1;
  pointer-events: none;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 80px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  width: 50px;
  height: 50px;
  object-fit: contain;
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.university-name {
  font-size: 16px;
  font-weight: 700;
  color: #2d3748;
}

.system-name {
  font-size: 14px;
  color: #64748b;
}

.nav-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.site-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.site-title .sub {
  font-size: 12px;
  font-weight: 400;
  color: #9ca3af;
  margin-left: 8px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #64748b;
  transition: color 0.2s;
  padding: 8px;
  border-radius: 4px;
}

.icon:hover {
  color: #3b82f6;
  background: #f3f4f6;
}

.main-content {
  padding: 28px 20px;
}

.page-title {
  text-align: center;
  color: #2d3748;
  font-size: 24px;
  margin: 6px 0 18px;
  font-weight: 600;
}

.card-row {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
  flex-wrap: nowrap;
  overflow: auto;
  align-items: flex-start;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .topbar {
    height: 70px;
    padding: 0 20px;
  }
  
  .logo {
    width: 40px;
    height: 40px;
  }
  
  .university-name {
    font-size: 14px;
  }
  
  .system-name {
    font-size: 12px;
  }
  
  .site-title {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .topbar {
    padding: 0 16px;
    height: 60px;
    flex-wrap: wrap;
  }
  
  .logo-section {
    gap: 12px;
  }
  
  .logo {
    width: 36px;
    height: 36px;
  }
  
  .university-name {
    font-size: 13px;
  }
  
  .system-name {
    font-size: 11px;
  }
  
  .nav-section {
    gap: 16px;
  }
  
  .site-title {
    font-size: 14px;
  }
  
  .site-title .sub {
    display: none;
  }
  
  .main-content {
    padding: 20px 16px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .card-row {
    gap: 16px;
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .topbar {
    height: auto;
    padding: 12px 16px;
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .nav-section {
    width: 100%;
    justify-content: space-between;
  }
  
  .actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .main-content {
    padding: 16px 12px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .card-row {
    gap: 12px;
    padding: 12px;
  }
}
</style>