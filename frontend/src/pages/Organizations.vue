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
          机构库 <span class="sub">dm.cdut.edu.cn</span>
        </div>
      </div>
      <!-- 视图切换 Tabs -->
      <div class="view-tabs">
        <button 
          :class="['tab-btn', { active: currentTab === 'info' }]"
          @click="currentTab = 'info'"
        >
          <span class="icon">▤</span> 知识信息
        </button>
        <button 
          :class="['tab-btn', { active: currentTab === 'graph' }]"
          @click="currentTab = 'graph'"
        >
          <span class="icon">☊</span> 关系图谱
        </button>
        <button 
          :class="['tab-btn', { active: currentTab === 'timeline' }]"
          @click="currentTab = 'timeline'"
        >
          <span class="icon">⸹</span> 时间轴
        </button>
      </div>
      <div class="actions"></div>
    </div>

    <!-- 知识信息视图 (原有内容) -->
    <div v-if="currentTab === 'info'" class="tab-content info-view">
      <HeroBanner
        image="/HomePage/机构.jpg"
        title="数字记忆 · 机构库"
        :height="320"
        description="机构库收录与计算机与网络安全学院相关的组织和机构资料，包括院系、研究中心、实验室等信息。"
      />

      <div class="searchbar">
      <input
        v-model="query"
        class="search-input"
        placeholder="搜索机构、类别…"
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
      <p>暂无机构数据</p>
      <button @click="fetchOrganizationsData" class="retry-btn">
        重新加载
      </button>
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
          >共 {{ filteredAndSortedOrganizations.length }} 条数据</span
        >
      </div>

      <div class="grid">
        <LibraryCard
          v-for="item in filteredAndSortedOrganizations"
          :key="item.id"
          :title="item.name"
          :subtitle="item.category"
          :image="item.photo"
          :count="item.readCount"
          :to="`/organizations/${item.id}`"
        />
      </div>
    </div>
    </div>

    <!-- 时间轴视图 (历史沿革图) -->
    <div v-if="currentTab === 'timeline'" class="tab-content timeline-view">
      <div 
         className="timeline-scroll-wrapper" 
         ref="timelineWrapper"
         @mousedown="startDrag"
         @mouseleave="stopDrag"
         @mouseup="stopDrag"
         @mousemove="doDrag"
      >
        <div class="evolution-chart">
           <div 
             v-for="(stage, index) in historyStages" 
             :key="index" 
             class="evolution-column"
           >
              <!-- 阶段头部 (学院/系名称) -->
              <div class="stage-header" :class="getHeaderClass(stage.title)">
                  <div class="stage-title">{{ stage.title }}</div>
                  <div class="stage-period">{{ stage.period }}</div>
              </div>

              <!-- 连线 (除了最后一列) -->
              <div v-if="index < historyStages.length - 1" class="connection-line"></div>

              <!-- 具体专业/机构列表 -->
              <div class="stage-items">
                  <div 
                    v-for="(item, idx) in stage.items" 
                    :key="idx" 
                    class="org-item"
                    :class="{ 'org-item-highlight': item.highlight }"
                  >
                      <div class="item-period">{{ item.period }}</div>
                      <div class="item-name">{{ item.name }}</div>
                  </div>
              </div>
           </div>
        </div>
      </div>
    </div>

    <!-- 关系图谱视图 -->
    <div v-if="currentTab === 'graph'" class="tab-content graph-view">
        <div ref="graphChart" class="echarts-container"></div>
    </div>

  </div>
</template>

<script setup>
import LibraryCard from "../components/LibraryCard.vue";
import HeroBanner from "../components/HeroBanner.vue";
// 添加API导入
import { getEntitiesByType, searchEntities } from "../api/knowledgeGraph";
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import * as echarts from 'echarts';

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

const currentTab = ref("info");
const query = ref("");
const sortBy = ref("name");
const categoryFilter = ref("");
const loading = ref(false);

// 图谱相关
const graphChart = ref(null);
const chartInstance = ref(null);

const initGraph = () => {
  if (!graphChart.value) return;
  
  chartInstance.value = echarts.init(graphChart.value);
  
  const option = {
    backgroundColor: '#f8fafc',
    tooltip: {},
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        type: 'graph',
        layout: 'force',
        symbolSize: 50,
        roam: 'scale', // 只允许缩放，禁止拖动背景（平移）
        label: {
          show: true,
          position: 'inside',
          fontSize: 12
        },
        edgeSymbol: ['circle', 'arrow'],
        edgeSymbolSize: [4, 10],
        draggable: true, // 允许节点拖拽回弹
        data: [
            // 中心节点
            {
                name: '计算机与\n网络安全学院',
                symbolSize: 100,
                // 去掉 x, y, fixed 属性，让布局自动居中
                itemStyle: {
                    color: '#ffffff', // 改为白色
                    borderColor: '#fecaca', // 改为淡粉色
                    borderWidth: 3,
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.1)'
                },
                label: {
                    show: true,
                    fontSize: 15,
                    fontWeight: 'bold',
                    color: '#334155', // 深灰色文字
                    lineHeight: 20
                }
            },
            // 子节点：2025年学院标准
            ...['计算机科学与技术', '网络空间安全', '软件工程', '数字媒体技术', '人工智能', '物联网工程'].map(name => ({
                name,
                symbolSize: 75,
                itemStyle: {
                    color: '#fff5f5', // 改为淡粉色
                    borderColor: '#fecaca', // 粉色边框
                    borderWidth: 1,
                    shadowBlur: 5,
                    shadowColor: 'rgba(0, 0, 0, 0.05)'
                },
                label: {
                    show: true,
                    color: '#475569',
                    fontSize: 13,
                    formatter: (params) => {
                        // 换行处理
                        return params.name.length > 5 ? params.name.slice(0, 4) + '\n' + params.name.slice(4) : params.name;
                    }
                }
            }))
        ],
        links: [
             ...['计算机科学与技术', '网络空间安全', '软件工程', '数字媒体技术', '人工智能', '物联网工程'].map(name => ({
                source: '计算机与\n网络安全学院',
                target: name,
                lineStyle: {
                    color: '#cbd5e1',
                    width: 2,
                    curveness: 0.3 // 增加曲率
                }
            }))
        ],
        force: {
            repulsion: 800,
            edgeLength: 180,
            gravity: 0.1
        }
      }
    ]
  };
  chartInstance.value.setOption(option);
};

// 监听Tab切换
watch(currentTab, (newTab) => {
    if (newTab === 'graph') {
        nextTick(() => {
            initGraph();
        });
    } else {
        if (chartInstance.value) {
            chartInstance.value.dispose();
            chartInstance.value = null;
        }
    }
});

// 窗口大小调整
const handleResize = () => {
    chartInstance.value && chartInstance.value.resize();
};

onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    if (chartInstance.value) {
        chartInstance.value.dispose();
    }
});

onMounted(() => {
    window.addEventListener('resize', handleResize);
});

// 拖拽相关逻辑
const timelineWrapper = ref(null);
const isMouseDown = ref(false);
const startX = ref(0);
const startY = ref(0);
const scrollLeft = ref(0);
const scrollTop = ref(0);

const startDrag = (e) => {
    isMouseDown.value = true;
    startX.value = e.pageX;
    startY.value = e.pageY;
    scrollLeft.value = timelineWrapper.value.scrollLeft;
    scrollTop.value = timelineWrapper.value.scrollTop;
    timelineWrapper.value.style.cursor = 'grabbing';
};

const stopDrag = () => {
    isMouseDown.value = false;
    if (timelineWrapper.value) {
        timelineWrapper.value.style.cursor = 'grab';
    }
};

const doDrag = (e) => {
    if (!isMouseDown.value) return;
    e.preventDefault();
    const x = e.pageX;
    const y = e.pageY;
    const walkX = (x - startX.value) * 1.5; // 拖动速度系数
    const walkY = (y - startY.value) * 1.5;
    timelineWrapper.value.scrollLeft = scrollLeft.value - walkX;
    timelineWrapper.value.scrollTop = scrollTop.value - walkY;
};

// ============================================
// 数据修改处：机构历史沿革数据
// 请在此处修改 historyStages 的内容
// ============================================
const historyStages = [
  {
    title: "计算机工程系",
    period: "1993-1998",
    items: [
      { name: "计算机及应用", period: "1994-1998" }
    ]
  },
  {
    title: "", 
    period: "1999-2001",
    items: [
      { name: "计算机科学与技术", period: "1999-2001" },
      { name: "电子信息科学与技术", period: "2001" }
    ]
  },
  {
    title: "",
    period: "2001-2010",
    items: [
      { name: "计算机科学与技术", period: "2001-2010" },
      { name: "电子信息科学与技术", period: "2001-2010" }
    ]
  },
  {
    title: "信息科学与技术学院",
    period: "2011-2018",
    items: [
      { name: "计算机科学与技术", period: "2011-2016" },
      { name: "软件工程", period: "2005-2016" },
      { name: "数字媒体技术", period: "2011-2018" },
      { name: "物联网工程", period: "2011-2018" },
      { name: "电子信息科学与技术", period: "2011-2018" }
    ]
  },
  {
    title: "网络空间安全学院",
    period: "2017-2018",
    items: [
       { name: "计算机科学与技术", period: "2017-2018" },
       { name: "网络空间安全", period: "2018" },
       { name: "软件工程", period: "2017-2018" },
    ]
  },
  {
    title: "信息科学与技术学院(网络安全学院、牛津布鲁克斯学院)",
    period: "2019-2020",
    items: [
        { name: "计算机科学与技术", period: "2019-2020" },
        { name: "计算机科学与技术(中外合作办学)", period: "2019-2020" },
        { name: "网络空间安全", period: "2019-2020" },
        { name: "软件工程", period: "2019-2020" },
        { name: "软件工程(中外合作办学)", period: "2019-2020" },
        { name: "数字媒体技术", period: "2019-2020" },
        { name: "人工智能", period: "2020" },
        { name: "物联网工程", period: "2019-2020" },
        { name: "电子信息科学与技术", period: "2019" }
    ]
  },
  {
    title: "计算机与网络安全学院(牛津布鲁克斯学院)",
    period: "2021-2023",
    items: [
        { name: "计算机科学与技术", period: "2021-2023" },
        { name: "计算机科学与技术(中外合作办学)", period: "2021-2023" },
        { name: "网络空间安全", period: "2021-2023" },
        { name: "软件工程", period: "2021-2023" },
        { name: "软件工程(中外合作办学)", period: "2021-2023" },
        { name: "数字媒体技术", period: "2021-2023" },
        { name: "人工智能", period: "2021-2023" },
        { name: "物联网工程", period: "2021-2003" },
        { name: "智能科学与技术", period: "2021-2024", highlight: true }
    ]
  },
  {
    title: "计算机与网络安全学院(示范性软件学院)",
    period: "2024-2025",
    items: [
        { name: "计算机科学与技术", period: "2024-2025" },
        { name: "网络空间安全", period: "2024-2025" },
        { name: "软件工程", period: "2024-2025" },
        { name: "数字媒体技术", period: "2024-2025" },
        { name: "人工智能", period: "2024-2025" },
        { name: "物联网工程", period: "2024-2025" }
    ]
  }
];

const getHeaderClass = (title) => {
    if (title.includes("工程系")) return "header-engineering";
    if (title.includes("信息科学")) return "header-info-science";
    if (title.includes("网络空间")) return "header-cyber";
    return "header-default";
};



// 改为从API获取数据
const organizationsData = ref([]);

// 在组件挂载时加载数据
onMounted(async () => {
  await fetchOrganizationsData();
});

// 获取机构数据的方法
const fetchOrganizationsData = async () => {
  try {
    loading.value = true;
    // 调用后端API获取机构类型实体
    const response = await getEntitiesByType("organization");
    console.log("机构API返回数据:", response);

    // 将后端数据格式转换为前端需要的格式
    organizationsData.value = response.map((entity) => ({
      id: entity.id,
      name: entity.name,
      category: entity.entity_type,
      desc: entity.description,
      photo: entity.photo_url || "/Organizations/default.jpg", // 默认图片，后续可以从实体属性中获取
      readCount: 0, // 阅读量，后续可以从实体属性中获取
      lastUpdated: new Date().toISOString(),
      dataVersion: "1.0",
    }));

    console.log("转换后机构数据:", organizationsData.value);
  } catch (error) {
    console.error("加载机构数据失败:", error);
    // 可以添加用户友好的错误提示
  } finally {
    loading.value = false;
  }
};

// 搜索功能 - 修改为调用API
const handleSearch = async () => {
  const searchTerm = query.value.trim();

  if (!searchTerm) {
    await fetchOrganizationsData(); // 如果搜索为空，重新加载所有数据
    return;
  }

  try {
    loading.value = true;
    console.log("开始搜索机构:", searchTerm);

    // 使用搜索API
    const response = await searchEntities(searchTerm);
    console.log("机构搜索API返回:", response);

    if (response && response.length > 0) {
      // 转换数据格式，并过滤只保留机构类型
      organizationsData.value = response
        .filter((entity) => entity.entity_type === "organization")
        .map((entity) => ({
          id: entity.id,
          name: entity.name,
          category: entity.entity_type,
          desc: entity.description,
          photo: entity.photo_url || "/Organizations/default.jpg",
          readCount: 0,
          lastUpdated: new Date().toISOString(),
        }));
      console.log(
        "机构搜索成功，找到数据:",
        organizationsData.value.length,
        "条",
      );
    } else {
      // 如果没有搜索结果，显示提示但不清空数据
      console.log("搜索无结果，保持原数据");
      // 可以在这里添加用户提示
    }
  } catch (error) {
    console.error("机构搜索失败:", error);
    // 搜索失败时也保持原数据不变
  } finally {
    loading.value = false;
  }
};

// 清空搜索
const clearSearch = () => {
  query.value = "";
  fetchOrganizationsData(); // 清空时重新加载所有数据
};

// 计算属性：是否有数据
const hasData = computed(
  () => organizationsData.value && organizationsData.value.length > 0,
);

// 计算属性：唯一的类别列表
const uniqueCategories = computed(() => {
  if (!organizationsData.value) return [];
  const categories = new Set(
    organizationsData.value.map((p) => p.category).filter(Boolean),
  );
  return Array.from(categories).sort();
});

// 计算属性：过滤和排序后的机构列表
const filteredAndSortedOrganizations = computed(() => {
  let result = organizationsData.value;

  // 类别过滤
  if (categoryFilter.value) {
    result = result.filter((p) => p.category === categoryFilter.value);
  }

  // 关键词搜索（本地过滤，因为已经调用了搜索API）
  const q = query.value.trim().toLowerCase();
  if (q) {
    result = result.filter((organization) => {
      const searchFields = [
        organization.name,
        organization.category,
        organization.desc,
      ]
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

/* Tab Navigation */
.view-tabs {
  display: flex;
  justify-content: center;
  gap: 32px;
  padding: 0 24px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.tab-btn {
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 500;
  color: #64748b;
  padding: 16px 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  border-bottom: 3px solid transparent;
  margin-bottom: -1px;
}

.tab-btn:hover {
  color: #4a9eff;
}

.tab-btn.active {
  color: #4a9eff;
  border-bottom-color: #4a9eff;
  font-weight: 600;
}

/* Timeline/Evolution Chart View */
.timeline-view {
  background: white;
  height: calc(100vh - 120px);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.timeline-scroll-wrapper {
  flex: 1;
  overflow: auto; /* 允许双向滚动 */
  position: relative;
  padding: 40px;
  background-color: #f8fafc;
  cursor: grab; /* 显示抓手光标 */
  user-select: none; /* 防止拖动时选中文字 */
}

.timeline-scroll-wrapper:active {
  cursor: grabbing;
}

.timeline-scroll-wrapper::-webkit-scrollbar {
  height: 12px;
  width: 12px; /* 垂直滚动条宽度 */
}
.timeline-scroll-wrapper::-webkit-scrollbar-track {
  background: #f1f5f9;
}
.timeline-scroll-wrapper::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 6px;
}

.evolution-chart {
  display: flex; /* Flex布局实现多个列并排 */
  gap: 50px; /* 增加列间距 */
  min-height: 100%; /* 确保高度撑满 */
  min-width: max-content; /* 确保内容不换行 */
  padding-bottom: 20px;
}

.evolution-column {
  display: flex;
  flex-direction: column;
  width: 200px; 
  min-width: 200px;
  position: relative;
  align-items: center;
}

/* 阶段连线 */
.connection-line {
  position: absolute;
  top: 130px; /* 连接线高度，位于Header下方 */
  right: -50px; /* 调整连接线延伸距离，匹配 gap */
  width: 50px; /* 调整连接线长度，匹配 gap */
  height: 2px;
  background-color: #cbd5e1;
  z-index: 1;
}

/* 阶段头部样式 */
.stage-header {
  width: 90%;
  min-height: 80px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
  padding: 12px;
  text-align: center;
  margin-bottom: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* 顶部竖线 - 连接Header和下面的Items */
.stage-header::after {
  content: '';
  position: absolute;
  bottom: -40px;
  left: 50%;
  width: 2px;
  height: 40px;
  background-color: #e2e8f0;
}

.header-engineering {
   border-top: 3px solid #64748b;
}

.header-info-science {
   border-top: 3px solid #4a9eff;
}

.header-cyber {
    border-top: 3px solid #ec4899;
}

.header-default {
    border-top: 3px solid #94a3b8;
}

.stage-title {
  font-weight: 600;
  font-size: 14px;
  color: #334155;
  margin-bottom: 4px;
  line-height: 1.4;
}

.stage-period {
  font-size: 12px;
  color: #64748b;
  font-family: Consolas, monospace;
}

.stage-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  align-items: center;
  padding: 0 10px;
  position: relative;
}

/* 贯穿所有Items的竖线 */
.stage-items::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 50%;
    width: 2px;
    background-color: #e2e8f0;
    z-index: 0;
}

.org-item {
  width: 100%;
  background: #fff5f5; /* 默认浅粉色背景 */
  border: 1px solid #fecaca;
  padding: 10px;
  border-radius: 2px;
  text-align: center;
  position: relative;
  z-index: 1;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  transition: all 0.2s;
}

.org-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

/* 连接线节点的横向连接线 - 这是一个视觉trick */
.evolution-column:not(:last-child) .org-item::after {
    content: '';
    position: absolute;
    top: 50%;
    right: -50px; /* 调整延伸距离 匹配 gap */
    width: 50px;
    height: 1px;
    border-top: 1px dashed #cbd5e1;
    z-index: -1;
}

.org-item-highlight {
    background-color: #fef3c7; /* 黄色高亮 */
    border-color: #fcd34d;
}

.item-period {
    font-size: 11px;
    color: #94a3b8;
    margin-bottom: 2px;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    padding-bottom: 2px;
    display: inline-block;
}

.item-name {
    font-size: 13px;
    font-weight: 500;
    color: #475569;
}

/* Graph View */
.graph-view {
  height: calc(100vh - 120px);
  position: relative;
  background: #f8fafc;
  overflow: hidden;
}

.echarts-container {
    width: 100%;
    height: 100%;
}

</style>