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
      <div class="actions"></div>
    </div>
    <HeroBanner
      image="/HomePage/peopel.jpg"
      title="数字记忆 · 人物库"
      :height="320"
      description="人物库收录与计算机与网络安全学院相关的教职工和校友，例如老师，知名校友等。"
    />

    <div class="searchbar">
      <input
        v-model="query"
        class="search-input"
        placeholder="搜索人物姓名、职位、研究方向…"
        @keyup.enter="handleSearch"
      />
      <button v-if="query" @click="clearSearch" class="clear-btn">×</button>
      <button @click="handleSearch" class="search-btn">搜索</button>
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

      <div class="grid">
        <LibraryCard
          v-for="item in filteredAndSortedPeople"
          :key="item.id"
          :title="item.name"
          :subtitle="item.category"
          :image="item.photo"
          :count="item.readCount"
          :to="`/people/${item.id}`"
        />
      </div>

      <!-- 知识图谱跳转链接 - 放在grid之后 -->
      <div class="knowledge-graph-link">
        <router-link to="/knowledge-graph" class="graph-link-btn">
          知识图谱查询
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import LibraryCard from "../components/LibraryCard.vue";
import HeroBanner from "../components/HeroBanner.vue";
// 添加API导入
import { getEntitiesByType, searchEntities } from "../api/knowledgeGraph";
import { ref, computed, onMounted } from "vue";

// 从人物简介中提取职位信息
const extractPosition = (bio) => {
  if (!bio) return "未知职位";

  // 定义职位关键词
  const positionKeywords = [
    "教授",
    "副教授",
    "讲师",
    "助教",
    "博导",
    "硕导",
    "研究员",
    "副研究员",
    "助理研究员",
    "院长",
    "副院长",
    "系主任",
    "副主任",
    "所长",
    "副所长",
    "主任",
    "副主任",
    "党委书记",
    "副书记",
    "党委副书记",
    "博士",
    "工学博士",
    "理学博士",
    "文学博士",
    "医学博士",
    "法学博士",
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
      photo: entity.photo_url || "/People/default.jpg",
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
        photo: entity.photo_url || "/People/default.jpg",
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

// 计算属性：是否有数据
const hasData = computed(() => peopleData.value && peopleData.value.length > 0);

// 计算属性：唯一的职位类别列表
const uniqueCategories = computed(() => {
  if (!peopleData.value) return [];
  const categories = new Set(
    peopleData.value.map((p) => p.category).filter(Boolean),
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
      (a, b) => (b.readCount || 0) - (a.readCount || 0),
    );
  }

  return result;
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
  padding: 0;
  box-sizing: border-box;
  color: #2d3748;
  position: relative;
  overflow-x: hidden;
}

/* 添加微妙的背景纹理效果 */
.page::before {
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
  margin-bottom: 24px;
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

.back {
  text-decoration: none;
  color: #64748b;
  font-size: 14px;
  transition: color 0.2s;
}

.back:hover {
  color: #3b82f6;
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

.searchbar {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 30px 0 24px;
  position: relative;
  gap: 12px;
  padding: 0 4px;
}

.search-input {
  width: 400px;
  max-width: 70vw;
  padding: 14px 20px;
  padding-right: 45px;
  border-radius: 25px;
  border: 2px solid rgba(74, 158, 255, 0.2);
  background: white;
  color: #2d3748;
  outline: none;
  font-size: 16px;
  font-family: "Microsoft YaHei", sans-serif;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
.search-input:focus {
  border-color: #4a9eff;
  background: white;
  box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
  transform: translateY(-1px);
}
.search-input::placeholder {
  color: #94a3b8;
  font-size: 16px;
  font-family: "Microsoft YaHei", sans-serif;
}

.clear-btn {
  position: absolute;
  right: 100px;
  background: rgba(74, 158, 255, 0.1);
  border: 1px solid rgba(74, 158, 255, 0.2);
  color: #64748b;
  font-size: 16px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
}
.clear-btn:hover {
  color: #4a9eff;
  background: rgba(74, 158, 255, 0.2);
  border-color: rgba(74, 158, 255, 0.3);
}

.search-btn {
  padding: 14px 28px;
  border-radius: 25px;
  border: 2px solid #4a9eff;
  background: linear-gradient(135deg, #4a9eff 0%, #2a7fff 100%);
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  font-family: "Microsoft YaHei", sans-serif;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
}
.search-btn:hover {
  background: linear-gradient(135deg, #2a7fff 0%, #1a6fff 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(74, 158, 255, 0.4);
}
.search-btn:active {
  transform: translateY(0);
}

/* 响应式搜索栏 */
@media (max-width: 768px) {
  .searchbar {
    justify-content: center;
    margin: 20px 0;
  }

  .search-input {
    width: 320px;
    max-width: 70vw;
    font-size: 14px;
    padding: 12px 16px;
    padding-right: 40px;
  }

  .search-input::placeholder {
    font-size: 14px;
  }

  .search-btn {
    font-size: 14px;
    padding: 12px 24px;
  }

  .clear-btn {
    right: 90px;
  }
}

@media (max-width: 480px) {
  .searchbar {
    flex-direction: column;
    gap: 10px;
  }

  .search-input {
    width: 100%;
    max-width: none;
  }

  .clear-btn {
    right: auto;
    position: static;
    align-self: flex-end;
  }

  .search-btn {
    width: 100%;
  }
}

.filter-options {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  padding: 0 4px;
  max-width: 1300px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 60px;
}

.filter-label {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  margin-right: 8px;
  white-space: nowrap;
}
.sort-select,
.category-select {
  padding: 10px 16px;
  border-radius: 12px;
  border: 2px solid rgba(74, 158, 255, 0.2);
  background: white;
  color: #2d3748;
  outline: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.sort-select:hover,
.category-select:hover {
  border-color: rgba(74, 158, 255, 0.3);
  background: #f8fafc;
}
.sort-select:focus,
.category-select:focus {
  border-color: #4a9eff;
  box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
}

.grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 30px;
  margin-top: 40px;
  padding: 0 60px;
  max-width: 1300px;
  margin-left: auto;
  margin-right: auto;
}

/* 响应式网格布局 */
@media (max-width: 1400px) {
  .grid {
    padding: 0 50px;
  }
}

@media (max-width: 1200px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 25px;
    padding: 0 40px;
  }
}

@media (max-width: 992px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    padding: 0 30px;
  }
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 18px;
    margin-top: 30px;
    padding: 0 20px;
  }
}

@media (max-width: 480px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    padding: 0 16px;
  }
}

.loading {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.loading-spinner {
  border: 4px solid rgba(74, 158, 255, 0.1);
  border-top: 4px solid #4a9eff;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin: 0 auto 24px;
  box-shadow: 0 0 20px rgba(74, 158, 255, 0.2);
}

@keyframes spin {
  0% {
    transform: rotate(0deg) scale(1);
  }
  50% {
    transform: rotate(180deg) scale(1.05);
  }
  100% {
    transform: rotate(360deg) scale(1);
  }
}

.loading p {
  font-size: 16px;
  margin: 0;
  opacity: 0.8;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.8;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.02);
  }
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
  font-size: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background: rgba(74, 158, 255, 0.05);
  border-radius: 16px;
  border: 2px dashed rgba(74, 158, 255, 0.2);
  margin: 0 4px;
}

.empty-state p {
  margin: 0 0 24px 0;
  font-size: 18px;
  font-weight: 500;
  color: #2d3748;
}

.retry-btn {
  margin-top: 8px;
  padding: 10px 24px;
  border-radius: 12px;
  border: 2px solid #4a9eff;
  background: linear-gradient(135deg, #4a9eff 0%, #2a7fff 100%);
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
}

.retry-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(74, 158, 255, 0.4);
  background: linear-gradient(135deg, #2a7fff 0%, #1a6fff 100%);
}

.retry-btn:active {
  transform: translateY(0);
}

.data-count {
  margin-left: auto;
  color: #cbd3d6;
  font-size: 14px;
  font-weight: 600;
  background: rgba(74, 158, 255, 0.2);
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(74, 158, 255, 0.3);
}

/* 响应式过滤选项 */
@media (max-width: 768px) {
  .filter-options {
    gap: 16px;
    padding: 12px 16px;
    margin-bottom: 16px;
  }

  .filter-label {
    font-size: 13px;
  }

  .sort-select,
  .category-select {
    padding: 8px 12px;
    font-size: 13px;
    min-width: 100px;
  }
}

@media (max-width: 480px) {
  .filter-options {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .filter-label {
    margin-right: 0;
    margin-bottom: 4px;
  }

  .sort-select,
  .category-select {
    min-width: unset;
  }

  .data-count {
    margin-left: 0;
    text-align: center;
  }
}

/* 知识图谱链接样式 */
.knowledge-graph-link {
  text-align: center;
  margin-top: 40px;
  margin-bottom: 60px;
  padding: 0 4px;
}

.graph-link-btn {
  display: inline-block;
  padding: 14px 32px;
  background: linear-gradient(135deg, #4a9eff 0%, #2a7fff 100%);
  color: white;
  text-decoration: none;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 6px 16px rgba(74, 158, 255, 0.3);
  border: 2px solid rgba(74, 158, 255, 0.2);
}

.graph-link-btn:hover {
  background: linear-gradient(135deg, #2a7fff 0%, #1a6fff 100%);
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(74, 158, 255, 0.4);
  border-color: rgba(74, 158, 255, 0.4);
}

.graph-link-btn:active {
  transform: translateY(0);
}

/* 响应式知识图谱链接 */
@media (max-width: 768px) {
  .knowledge-graph-link {
    margin-top: 30px;
    margin-bottom: 40px;
  }

  .graph-link-btn {
    padding: 12px 28px;
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .graph-link-btn {
    padding: 12px 24px;
    font-size: 14px;
    width: 100%;
    max-width: 280px;
  }
}

/* 响应式topbar */
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
