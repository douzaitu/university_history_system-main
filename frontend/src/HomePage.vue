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
      <div class="actions"></div>
    </div>

    <div class="main-content">
      <h1 class="page-title">校史馆数字记忆 · 首页</h1>

      <div class="card-row">
        <Card
          title="人物"
          desc="以知识图谱形式收录计算机与网络安全学院相关人物"
          :count="counts.people"
          to="/people"
          image="/HomePage/peopel.jpg"
        />
        <Card
          title="地点"
          desc="收录与计算机与网络安全学院相关的地理位置、建筑等"
          :count="counts.places"
          to="/places"
          image="/HomePage/place.jpg"
        />
        <Card
          title="学科"
          desc="学科库为用户提供了解计算机与网络安全学院学科的信息"
          :count="counts.subjects"
          to="/subjects"
          image="/HomePage/subject.gif"
        />
        <Card
          title="机构"
          desc="收录与计算机与网络安全学院相关的组织和机构资料"
          :count="counts.organizations"
          to="/organizations"
          image="/HomePage/机构.jpg"
        />
        <Card
          title="事件"
          desc="记录与计算机与网络安全学院相关的重要事件"
          :count="counts.events"
          to="/events"
          image="/HomePage/事件.jpg"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Card from "./components/Card.vue";
import { getEntitiesByType } from "./api/knowledgeGraph";

const counts = ref({
  people: 0,
  places: 0,
  subjects: 0,
  organizations: 0,
  events: 0,
});

onMounted(async () => {
  try {
    // 并行获取各类型实体数量（只统计核心实体）
    const results = await Promise.all([
      getEntitiesByType("person", true),
      getEntitiesByType("location", true),
      getEntitiesByType("subject", true),
      getEntitiesByType("organization", true),
      getEntitiesByType("event", true),
    ]);

    counts.value = {
      people: results[0].length,
      places: results[1].length,
      subjects: results[2].length,
      organizations: results[3].length,
      events: results[4].length,
    };
  } catch (error) {
    console.error("Failed to fetch entity counts:", error);
  }
});
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
  position: relative;
  overflow-x: hidden;
  box-sizing: border-box;
  color: #2d3748;
}

/* 添加微妙的背景纹理效果 */
.home::before {
  content: "";
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(
      circle at 20% 80%,
      rgba(74, 158, 255, 0.05) 0%,
      transparent 50%
    ),
    radial-gradient(
      circle at 80% 20%,
      rgba(74, 158, 255, 0.05) 0%,
      transparent 50%
    ),
    radial-gradient(
      circle at 40% 40%,
      rgba(74, 158, 255, 0.03) 0%,
      transparent 50%
    );
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
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.icon:hover {
  background-color: #f3f4f6;
}

.icon img {
  width: 20px;
  height: 20px;
}

.main-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 50px;
  color: #1e293b;
  position: relative;
  display: inline-block;
}

.card-row {
  display: flex;
  flex-wrap: wrap; /* 允许换行以适应小屏幕 */
  gap: 32px;
  justify-content: center;
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
