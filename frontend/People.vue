<template>
  <div class="page">
    <div class="topbar">
      <div class="logo-section">
        <img src="/logo.svg" alt="成都理工大学" class="logo" />
        <div class="logo-text">
          <div class="university-name">成都理工大学</div>
          <div class="system-name">数字记忆</div>
        </div>
      </div>
      <div class="nav-section">
        <router-link to="/" class="back">← 返回首页</router-link>
        <div class="site-title">
          人物库 <span class="sub">dm.cdut.edu.cn</span>
        </div>
      </div>
      <div class="actions">
        <button class="icon" @click="handleSearch">🔍</button>
      </div>
    </div>
    <div class="hero-banner">
      <img src="/HomePage/peopel.jpg" alt="人物库" class="hero-bg" />
      <div class="hero-overlay">
        <div class="hero-content">
          <h1 class="hero-title">人物库</h1>
          <p class="hero-desc">
            人物库，主要以知识图谱的形式收录了成都理工大学校史中的相关人物。每个人物被表示为一个节点，节点包含了人物的基本信息，如姓名、职务、学术领域等。不同人物之间的关系则通过边来表示，例如师生关系、合作关系等。通过这种方式，可以清晰地展示出重大人物群体的人物网络，帮助人们更好地了解和研究成都理工大学的历史和学术发展。
          </p>
        </div>
      </div>
    </div>

    <div class="search-container">
      <div class="searchbar">
        <input
          v-model="query"
          class="search-input"
          placeholder="搜索人物姓名、职务、研究方向…"
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch" class="search-btn">搜索</button>
      </div>
      
      <div class="filter-options">
        <label class="filter-label">排序方式:</label>
        <select v-model="sortBy" class="sort-select">
          <option value="name">按姓名</option>
          <option value="readCount">按阅读量</option>
        </select>

        <label class="filter-label">显示:</label>
        <select v-model="categoryFilter" class="category-select">
          <option value="">全部</option>
          <option
            v-for="category in uniqueCategories"
            :key="category"
            :value="category"
          >
            {{ category }}
          </option>
        </select>

        <span class="data-count"
          >共 {{ filteredAndSortedPeople.length }} 条数据</span
        >
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>正在加载数据...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!hasData" class="empty-state">
      <p>暂无人物数据</p>
      <button @click="fetchPeopleData" class="retry-btn">重新加载</button>
    </div>

    <!-- 数据展示 -->
    <div v-else>
      <div class="grid">
        <div
          v-for="item in filteredAndSortedPeople"
          :key="item.id"
          class="person-card"
          :to="`/people/${item.id}`"
        >
          <div class="person-photo">
            <img 
              :src="item.photo" 
              :alt="item.name" 
              @error="handleImageError"
            />
          </div>
          <div class="person-info">
            <h3 class="person-name">{{ item.name }}</h3>
            <p class="person-title">{{ item.category }}</p>
          </div>
        </div>
      </div>

      <!-- 知识图谱跳转链接 -->
      <div class="knowledge-graph-link">
        <router-link to="/knowledge-graph" class="graph-link-btn">
          🔍 知识图谱查询
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import LibraryCard from "../components/LibraryCard.vue";
// 添加API导入
import { getEntitiesByType, searchEntities } from "../api/knowledgeGraph";
import { ref, computed, onMounted } from "vue";

// 从人物简介中提取职位信息
const extractPosition = (bio) => {
  if (!bio) return "未知职位";
  
  // 定义职位关键词
  const positionKeywords = [
    "教授", "副教授", "讲师", "助教", "博导", "硕导",
    "研究员", "副研究员", "助理研究员",
    "院长", "副院长", "系主任", "副主任",
    "所长", "副所长", "主任", "副主任",
    "党委书记", "副书记", "党委副书记",
    "博士", "工学博士", "理学博士", "文学博士", "医学博士", "法学博士"
  ];
  
  // 遍历关键词，查找第一个匹配的职位
  for (const keyword of positionKeywords) {
    if (bio.includes(keyword)) {
      return keyword;
    }
  }
  
  return "未知职位";
};

const query = ref("");
const sortBy = ref("name");
const categoryFilter = ref("");
const loading = ref(false);
// 改为从API获取数据
const peopleData = ref([]);

// 在组件挂载时加载数据
onMounted(async () => {
  await fetchPeopleData();
});

// 获取人物数据的方法
const fetchPeopleData = async () => {
  try {
    loading.value = true;
    // 调用后端API获取人物类型实体
    const response = await getEntitiesByType("person");
    console.log("API返回数据:", response);

    peopleData.value = response.map((entity) => ({
      id: entity.id,
      name: entity.name,
      category: extractPosition(entity.description), // 从简介中提取职位信息
      bio: entity.description,
      photo: entity.photo_url
        ? `http://localhost:8000/media/${entity.photo_url}` // 使用后端返回的图片URL
        : "/People/default.jpg", // 默认图片
      readCount: 0,
      lastUpdated: new Date().toISOString(),
      dataVersion: "1.0",
    }));

    console.log("转换后数据:", peopleData.value);
  } catch (error) {
    console.error("加载人物数据失败:", error);
    // 可以添加用户友好的错误提示
  } finally {
    loading.value = false;
  }
};

// 搜索功能 - 修改为调用API
const handleSearch = async () => {
  const searchTerm = query.value.trim();

  if (!searchTerm) {
    await fetchPeopleData(); // 如果搜索为空，重新加载所有数据
    return;
  }

  try {
    loading.value = true;
    console.log("开始搜索:", searchTerm);

    // 方法1: 使用搜索API
    const response = await searchEntities(searchTerm);
    console.log("搜索API返回:", response);

    if (response && response.length > 0) {
      // 转换数据格式
      peopleData.value = response.map((entity) => ({
        id: entity.id,
        name: entity.name,
        category: extractPosition(entity.description), // 从简介中提取职位信息
        bio: entity.description,
        photo: entity.photo_url 
          ? `http://localhost:8000/media/${entity.photo_url}` 
          : "/People/default.jpg",
        readCount: 0,
        lastUpdated: new Date().toISOString(),
      }));
      console.log("搜索成功，找到数据:", peopleData.value.length, "条");
    } else {
      // 如果没有搜索结果，显示提示但不清空数据
      console.log("搜索无结果，保持原数据");
      // 可以在这里添加用户提示
    }
  } catch (error) {
    console.error("搜索失败:", error);
    // 搜索失败时也保持原数据不变
  } finally {
    loading.value = false;
  }
};

// 清空搜索
const clearSearch = () => {
  query.value = "";
  fetchPeopleData(); // 清空时重新加载所有数据
};

// 处理图片加载失败
const handleImageError = (event) => {
  event.target.src = '/People/default-avatar.svg';
};

// 计算属性：是否有数据
const hasData = computed(() => peopleData.value && peopleData.value.length > 0);

// 计算属性：唯一的职位类别列表
const uniqueCategories = computed(() => {
  if (!peopleData.value) return [];
  const categories = new Set(
    peopleData.value.map((p) => p.category).filter(Boolean)
  );
  return Array.from(categories).sort();
});

// 计算属性：过滤和排序后的人员列表
const filteredAndSortedPeople = computed(() => {
  let result = peopleData.value;

  // 类别过滤
  if (categoryFilter.value) {
    result = result.filter((p) => p.category === categoryFilter.value);
  }

  // 关键词搜索（本地过滤，因为已经调用了搜索API）
  const q = query.value.trim().toLowerCase();
  if (q) {
    result = result.filter((person) => {
      const searchFields = [person.name, person.category, person.bio]
        .filter(Boolean)
        .map((v) => String(v).toLowerCase());

      return searchFields.some((field) => field.includes(q));
    });
  }

  // 排序
  if (sortBy.value === "name") {
    result = [...result].sort((a, b) => a.name.localeCompare(b.name));
  } else if (sortBy.value === "readCount") {
    result = [...result].sort(
      (a, b) => (b.readCount || 0) - (a.readCount || 0)
    );
  }

  return result;
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f8f8f8;
  padding: 0;
  box-sizing: border-box;
  color: #333;
  position: relative;
  overflow-x: hidden;
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

.back {
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.2s;
}

.back:hover {
  background: #f3f4f6;
  color: #3b82f6;
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

.hero-banner {
  position: relative;
  height: 400px;
  overflow: hidden;
}

.hero-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(30%);
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.8));
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-content {
  text-align: center;
  color: white;
  padding: 0 20px;
  max-width: 800px;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  margin: 0 0 24px;
  letter-spacing: 8px;
  text-shadow: 
    2px 2px 4px rgba(0,0,0,0.5),
    0 0 30px rgba(255,255,255,0.1);
  font-family: "Microsoft YaHei", "SimHei", "PingFang SC", sans-serif;
  position: relative;
  display: inline-block;
  padding: 0 20px;
}

.hero-title::before,
.hero-title::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
}

.hero-title::before {
  right: 100%;
  margin-right: 10px;
}

.hero-title::after {
  left: 100%;
  margin-left: 10px;
}

.hero-desc {
  font-size: 15px;
  line-height: 1.8;
  margin: 0 auto;
  opacity: 0.85;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
  max-width: 700px;
  font-weight: 300;
  letter-spacing: 1px;
}

.search-container {
  background: white;
  padding: 30px 20px;
  margin: -40px 20px 30px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  position: relative;
  z-index: 10;
}

.searchbar {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 600px;
  margin: 0 auto 20px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.search-btn {
  padding: 12px 24px;
  background: #333;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.search-btn:hover {
  background: #555;
}

.filter-options {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.sort-select,
.category-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.sort-select:focus,
.category-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.data-count {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  padding: 0 20px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.person-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.person-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.person-photo {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f0f0f0;
}

.person-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.person-card:hover .person-photo img {
  transform: scale(1.05);
}

.person-info {
  padding: 15px;
  text-align: center;
}

.person-name {
  margin: 0 0 5px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.person-title {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}

.retry-btn {
  margin-top: 16px;
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #2563eb;
}

.knowledge-graph-link {
  text-align: center;
  margin: 40px 0;
}

.graph-link-btn {
  display: inline-block;
  padding: 12px 24px;
  background: #10b981;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
}

.graph-link-btn:hover {
  background: #059669;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .topbar {
    height: 70px;
    padding: 0 16px;
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
  
  .hero-banner {
    height: 300px;
  }
  
  .hero-title {
    font-size: 40px;
    letter-spacing: 6px;
    padding: 0 15px;
  }
  
  .hero-title::before,
  .hero-title::after {
    width: 40px;
  }
  
  .hero-desc {
    font-size: 14px;
    line-height: 1.7;
  }
  
  .search-container {
    margin: -30px 10px 20px;
    padding: 20px 15px;
  }
  
  .searchbar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .filter-options {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .person-photo {
    height: 160px;
  }
}

@media (max-width: 480px) {
  .grid {
    grid-template-columns: 1fr;
  }
  
  .hero-banner {
    height: 250px;
  }
  
  .hero-title {
    font-size: 32px;
    letter-spacing: 4px;
    padding: 0 10px;
  }
  
  .hero-title::before,
  .hero-title::after {
    width: 25px;
    height: 1px;
  }
  
  .hero-desc {
    font-size: 13px;
    line-height: 1.6;
    padding: 0 15px;
  }
}
</style>
