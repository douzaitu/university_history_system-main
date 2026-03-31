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
        <a href="javascript:void(0)" @click.prevent="goBack" class="back">← 返回首页</a>
        <div class="site-title">
          学科库 <span class="sub">dm.cdut.edu.cn</span>
        </div>
      </div>
      <div class="actions"></div>
    </div>
    <HeroBanner
      image="/HomePage/subject.gif"
      title="数字记忆 · 学科库"
      :height="320"
      description="学科库为用户提供了解计算机与网络安全学院学科的信息，包括学科发展、研究方向、课程体系等。"
    />

    <div class="searchbar">
      <input
        v-model="query"
        class="search-input"
        placeholder="搜索学科、方向…"
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
      <p>暂无学科数据</p>
      <button @click="fetchSubjectsData" class="retry-btn">重新加载</button>
    </div>

    <!-- 数据展示 -->
    <div v-else>
      <div class="filter-options">
        <label class="filter-label">排序方式:</label>
        <select v-model="sortBy" class="sort-select">
          <option value="name">按名称</option>
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
          >共 {{ filteredAndSortedSubjects.length }} 条数据</span
        >
      </div>

      <div class="grid">
        <LibraryCard
          v-for="item in filteredAndSortedSubjects"
          :key="item.id"
          :title="item.name"
          :subtitle="item.category"
          :image="item.photo"
          :count="item.readCount"
          :to="`/subjects/${item.id}`"
        />
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
import { useRouter } from "vue-router";

const router = useRouter();

const goBack = () => {
    // 尝试关闭窗口（针对新标签页打开的情况）
    window.close();
    
    // 如果窗口没有关闭，说明不是脚本打开的，执行路由回退
    if (!window.closed) {
        if (window.history.length > 1) {
            router.back();
        } else {
            // 如果没有历史记录，回退到首页
            router.push('/');
        }
    }
};

const query = ref("");
const sortBy = ref("name");
const categoryFilter = ref("");
const loading = ref(false);
// 改为从API获取数据
const subjectsData = ref([]);

// 在组件挂载时加载数据
onMounted(async () => {
  await fetchSubjectsData();
});

// 获取学科数据的方法
const fetchSubjectsData = async () => {
  try {
    loading.value = true;
    // 调用后端API获取学科类型实体
    const response = await getEntitiesByType("subject");
    console.log("学科API返回数据:", response);

    // 将后端数据格式转换为前端需要的格式
    subjectsData.value = response.map((entity) => ({
      id: entity.id,
      name: entity.name,
      category: entity.entity_type_display || entity.entity_type,
      desc: entity.description,
      photo: entity.photo_url || "/Subjects/default.jpg", // 默认图片，后续可以从实体属性中获取
      readCount: 0, // 阅读量，后续可以从实体属性中获取
      lastUpdated: new Date().toISOString(),
      dataVersion: "1.0",
    }));

    console.log("转换后学科数据:", subjectsData.value);
  } catch (error) {
    console.error("加载学科数据失败:", error);
    // 可以添加用户友好的错误提示
  } finally {
    loading.value = false;
  }
};

// 搜索功能 - 修改为调用API
const handleSearch = async () => {
  const searchTerm = query.value.trim();

  if (!searchTerm) {
    await fetchSubjectsData(); // 如果搜索为空，重新加载所有数据
    return;
  }

  try {
    loading.value = true;
    console.log("开始搜索学科:", searchTerm);

    // 使用搜索API
    const response = await searchEntities(searchTerm);
    console.log("学科搜索API返回:", response);

    if (response && response.length > 0) {
      // 转换数据格式，并过滤只保留学科类型
      subjectsData.value = response
        .filter((entity) => entity.entity_type === "subject")
        .map((entity) => ({
          id: entity.id,
          name: entity.name,
          category: entity.entity_type_display || entity.entity_type,
          desc: entity.description,
          photo: entity.photo_url || "/Subjects/default.jpg",
          readCount: 0,
          lastUpdated: new Date().toISOString(),
        }));
      console.log("学科搜索成功，找到数据:", subjectsData.value.length, "条");
    } else {
      // 如果没有搜索结果，显示提示但不清空数据
      console.log("搜索无结果，保持原数据");
      // 可以在这里添加用户提示
    }
  } catch (error) {
    console.error("学科搜索失败:", error);
    // 搜索失败时也保持原数据不变
  } finally {
    loading.value = false;
  }
};

// 清空搜索
const clearSearch = () => {
  query.value = "";
  fetchSubjectsData(); // 清空时重新加载所有数据
};

// 计算属性：是否有数据
const hasData = computed(
  () => subjectsData.value && subjectsData.value.length > 0,
);

// 计算属性：唯一的类别列表
const uniqueCategories = computed(() => {
  if (!subjectsData.value) return [];
  const categories = new Set(
    subjectsData.value.map((p) => p.category).filter(Boolean),
  );
  return Array.from(categories).sort();
});

// 计算属性：过滤和排序后的学科列表
const filteredAndSortedSubjects = computed(() => {
  let result = subjectsData.value;

  // 类别过滤
  if (categoryFilter.value) {
    result = result.filter((p) => p.category === categoryFilter.value);
  }

  // 关键词搜索（本地过滤，因为已经调用了搜索API）
  const q = query.value.trim().toLowerCase();
  if (q) {
    result = result.filter((subject) => {
      const searchFields = [subject.name, subject.category, subject.desc]
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
  background: #f8fafc;
  padding: 0;
  box-sizing: border-box;
  color: #2d3748;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 80px;
  background: white;
  border-bottom: 1px solid rgba(74, 158, 255, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
  color: #4a9eff;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
  font-weight: 500;
}

.back:hover {
  color: #2a7fff;
  text-decoration: underline;
}

.site-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
}

.site-title .sub {
  font-size: 12px;
  font-weight: 400;
  color: #94a3b8;
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
  color: #4a9eff;
  background: rgba(74, 158, 255, 0.1);
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
  gap: 16px;
}

.loading-spinner {
  border: 3px solid #f1f5f9;
  border-top: 3px solid #4a9eff;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
  box-shadow: 0 2px 8px rgba(74, 158, 255, 0.2);
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
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
  gap: 20px;
}

.retry-btn {
  margin-top: 8px;
  padding: 12px 24px;
  border-radius: 12px;
  border: 2px solid #4a9eff;
  background: white;
  color: #4a9eff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.retry-btn:hover {
  background: #4a9eff;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
}

.data-count {
  margin-left: auto;
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
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

  .filter-options {
    padding: 12px 16px;
  }
}

@media (max-width: 768px) {
  .topbar {
    padding: 0 16px;
    height: 60px;
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

  .filter-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;
  }

  .sort-select,
  .category-select {
    width: 100%;
  }

  .data-count {
    margin-left: 0;
    width: 100%;
    text-align: right;
  }
}

@media (max-width: 480px) {
  .topbar {
    padding: 0 16px;
  }

  .nav-section {
    gap: 12px;
  }

  .back {
    font-size: 13px;
  }

  .site-title {
    font-size: 13px;
  }

  .filter-options {
    padding: 10px 14px;
  }

  .filter-label {
    font-size: 13px;
  }

  .sort-select,
  .category-select {
    font-size: 13px;
    padding: 8px 12px;
  }
}
</style>
