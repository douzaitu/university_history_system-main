<template>
  <div class="detail-page">
    <div class="topbar">
      <div class="logo-section">
        <img src="/logo.svg" alt="成都理工大学" class="logo" />
        <div class="logo-text">
          <div class="university-name">成都理工大学</div>
          <div class="system-name">数字记忆</div>
        </div>
      </div>
      <div class="nav-section">
        <router-link to="/organizations" class="back">← 返回机构库</router-link>
        <div class="site-title">
          机构详情 <span class="sub">dm.cdut.edu.cn</span>
        </div>
      </div>
      <div class="actions">
        <button class="icon">🔍</button>
        <button class="icon">🏢</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="organization" class="content">
      <h1 class="name">{{ organization.name }}</h1>
      <div class="meta-row">
        <span>{{ organization.readCount }} 阅读</span>
        <span>｜ 收藏</span>
      </div>

      <div class="body">
        <div class="left">
          <div class="field">
            <span class="label">名称</span
            ><span class="value">{{ organization.name }}</span>
          </div>
          <div class="field">
            <span class="label">类别</span
            ><span class="value">{{ organization.category }}</span>
          </div>
          <div class="bio">
            <div class="label">简介</div>
            <p class="text">{{ organization.desc }}</p>
          </div>
        </div>
        <div class="right">
          <div class="photo">
            <img :src="organization.photo" alt="photo" />
          </div>
        </div>
      </div>

      <div class="footer">
        <button class="pager">‹</button>
        <div class="progress"><div class="bar"></div></div>
        <button class="pager">›</button>
      </div>
    </div>

    <div v-else class="notfound">
      未找到机构信息。
      <router-link to="/organizations" class="back">返回机构库</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { getEntityDetail } from "../api/entityDetail";

const route = useRoute();
const organization = ref(null);
const loading = ref(false);

// 获取机构详情数据
const fetchOrganizationDetail = async (id) => {
  try {
    loading.value = true;
    console.log("加载机构详情，ID:", id);

    const response = await getEntityDetail(id);
    console.log("机构详情API返回:", response);

    if (response) {
      organization.value = {
        id: response.id,
        name: response.name,
        category: response.entity_type,
        desc: response.description,
        photo: "/Organizations/default.jpg",
        readCount: 0,
      };
    }
  } catch (error) {
    console.error("加载机构详情失败:", error);
    organization.value = null;
  } finally {
    loading.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  if (route.params.id) {
    fetchOrganizationDetail(route.params.id);
  }
});

// 监听路由变化
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      fetchOrganizationDetail(newId);
    }
  }
);
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #f7f4f3;
  color: #2b2b2b;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 80px;
  background: #2b2b2b;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
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
  color: #ffffff;
}

.system-name {
  font-size: 14px;
  color: #b8c2cc;
}

.nav-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.back {
  color: #cfe9ff;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.back:hover {
  color: #4a9eff;
}

.site-title {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.site-title .sub {
  font-size: 12px;
  font-weight: 400;
  color: #8a949e;
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
  color: #b8c2cc;
  transition: color 0.2s;
  padding: 8px;
  border-radius: 4px;
}

.icon:hover {
  color: #4a9eff;
  background: rgba(74, 158, 255, 0.1);
}
.content {
  padding: 20px;
}
.name {
  font-size: 30px;
  margin: 10px 0 6px;
}
.meta-row {
  color: #9a9a9a;
  font-size: 12px;
}
.body {
  display: flex;
  gap: 30px;
  margin-top: 10px;
}
.left {
  flex: 1;
}
.field {
  display: flex;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px dashed #ddd;
}
.label {
  width: 90px;
  color: #7c7c7c;
}
.value {
  color: #333;
}
.bio {
  margin-top: 18px;
}
.text {
  line-height: 1.75;
  text-align: justify;
}
.right {
  width: 300px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
.photo {
  background: #fff;
  border: 1px solid #ddd;
  padding: 10px;
}
.photo img {
  width: 100%;
  height: auto;
  display: block;
}
.footer {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 60px;
  background: #1f1f1f;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}
.pager {
  background: #333;
  color: #fff;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 18px;
  cursor: pointer;
}
.progress {
  width: 260px;
  height: 6px;
  background: #444;
  border-radius: 10px;
  overflow: hidden;
}
.bar {
  width: 30%;
  height: 100%;
  background: #bbb;
}
.notfound {
  padding: 20px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #9a9a9a;
}

.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4a9eff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
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
}
</style>
