<template>
  <div class="knowledge-graph-page">
    <!-- 顶部导航 -->
    <div class="topbar">
      <div class="logo-section">
        <img src="/logo.svg" alt="成都理工大学" class="logo" />
        <div class="logo-text">
          <div class="university-name">成都理工大学</div>
          <div class="system-name">数字记忆</div>
        </div>
      </div>
      <div class="nav-section">
        <router-link to="/people" class="back">← 返回人物库</router-link>
        <div class="site-title">
          知识图谱 <span class="sub">dm.cdut.edu.cn</span>
        </div>
      </div>
      <div class="actions">
        <button class="icon" @click="handleSearch">🔍</button>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-container">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="输入教师姓名搜索知识图谱..."
          class="search-input"
          @input="handleSearchInput"
          @keyup.enter="searchTeacher"
        />
        <button @click="searchTeacher" class="search-btn">搜索</button>

        <!-- 搜索结果下拉 -->
        <div v-if="searchResults.length > 0" class="search-results">
          <div
            v-for="teacher in searchResults"
            :key="teacher"
            class="result-item"
            @click="selectTeacher(teacher)"
          >
            {{ teacher }}
          </div>
        </div>
      </div>
    </div>

    <!-- 当前查询的教师 -->
    <div v-if="currentTeacher" class="current-teacher">
      <h3>正在查看: {{ currentTeacher }}</h3>
    </div>

    <!-- 图谱容器 -->
    <div class="graph-container">
      <div
        ref="graph"
        class="graph"
        :style="{
          height: graphHeight + 'px',
          width: '100%',
          minHeight: '400px',
        }"
      ></div>

      <!-- 加载状态 -->
      <div v-if="loading" class="graph-loading">
        <div class="loading-spinner"></div>
        <p>正在加载知识图谱...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!hasData && currentTeacher" class="graph-empty">
        <p>未找到 {{ currentTeacher }} 的相关知识图谱数据</p>
      </div>

      <!-- 初始状态 -->
      <div v-else-if="!currentTeacher" class="graph-initial">
        <p>请输入教师姓名搜索知识图谱</p>
      </div>
    </div>

    <!-- 图例 -->
    <div class="legend">
      <div class="legend-item">
        <div class="legend-color teacher"></div>
        <span>教师</span>
      </div>
      <div class="legend-item">
        <div class="legend-color entity"></div>
        <span>相关实体</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { searchTeachers, getTeacherGraph } from "../api/knowledgeGraph";

// 动态导入echarts
let echarts = null;

const router = useRouter();

// 状态管理
const searchQuery = ref("");
const searchResults = ref([]);
const currentTeacher = ref("");
const loading = ref(false);
const graph = ref(null);
const graphHeight = ref(600);
const chart = ref(null);
const errorMessage = ref("");

// 图谱数据
const graphData = ref({
  nodes: [],
  edges: [],
});

// 计算属性
const hasData = ref(false);

// 搜索教师
const searchTeacher = async () => {
  const teacherName = searchQuery.value.trim();
  if (!teacherName) return;

  try {
    loading.value = true;
    await loadTeacherGraph(teacherName);
    searchResults.value = [];
  } catch (error) {
    console.error("搜索失败:", error);
    hasData.value = false;
  } finally {
    loading.value = false;
  }
};

// 处理搜索输入
const handleSearchInput = async () => {
  const query = searchQuery.value.trim();

  if (!query) {
    searchResults.value = [];
    return;
  }

  try {
    console.log("开始搜索:", query);
    
    // 使用封装的API替代直接fetch
    const data = await searchTeachers(query);
    console.log("搜索返回数据:", data);

    // axios返回的data就是响应体，不需要再.json()
    searchResults.value = data.teachers || [];
    console.log("处理后结果:", searchResults.value);
  } catch (error) {
    console.error("搜索建议失败:", error);
    searchResults.value = [];
  }
};

// 选择教师
const selectTeacher = (teacher) => {
  searchQuery.value = teacher;
  searchResults.value = [];
  searchTeacher();
};

// 加载教师图谱数据
const loadTeacherGraph = async (teacherName) => {
  try {
    loading.value = true;
    errorMessage.value = "";
    console.log("开始加载教师图谱:", teacherName);

    // 使用封装的API替代直接fetch
    const data = await getTeacherGraph(teacherName);
    console.log("图谱数据:", data);

    // 处理数据 (axios自动处理了JSON解析)
    if (data.nodes && data.edges) {
      graphData.value = data;
      currentTeacher.value = teacherName;
      hasData.value = data.nodes.length > 0;
      console.log("图谱数据有效，节点数量:", data.nodes.length);

      // 直接渲染图谱
      renderGraph();
    } else {
      console.log("图谱数据无效");
      hasData.value = false;
      errorMessage.value = "未找到相关图谱数据";
    }
  } catch (error) {
    console.error("加载图谱数据失败:", error);
    hasData.value = false;
    errorMessage.value = "加载知识图谱失败: " + error.message;
  } finally {
    loading.value = false;
  }
};

// 渲染图谱
const renderGraph = async () => {
  if (!graph.value) {
    console.error("图谱容器未找到");
    return;
  }

  console.log("开始渲染图谱...");

  // 动态导入echarts
  if (!echarts) {
    try {
      echarts = await import("echarts");
      console.log("ECharts加载成功");
    } catch (error) {
      console.error("ECharts加载失败:", error);
      return;
    }
  }

  // 销毁旧图表
  if (chart.value) {
    chart.value.dispose();
    chart.value = null;
  }

  // 初始化图表
  try {
    chart.value = echarts.init(graph.value);
    console.log("ECharts初始化成功");
  } catch (error) {
    console.error("ECharts初始化失败:", error);
    return;
  }

  // 准备图表数据
  const nodes = graphData.value.nodes.map((node) => {
    const nodeSize = node.size || (node.type === "teacher" ? 30 : 20);
    // 丰富颜色方案
    const nodeColors = {
      teacher: "#5470c6",
      entity: "#91cc75",
      school: "#fac858",
      subject: "#ee6666",
      award: "#73c0de",
      paper: "#3ba272",
      default: "#91cc75",
    };
    // 使用不同形状
    const symbolType = node.type === "teacher" ? "circle" : "circle";

    return {
      id: node.id,
      name: node.label,
      symbolSize: nodeSize,
      symbol: symbolType,
      itemStyle: {
        color: nodeColors[node.type] || nodeColors.default,
        borderColor: "#333",
        borderWidth: 2,
        shadowBlur: 10,
        shadowColor: "rgba(0, 0, 0, 0.3)",
        shadowOffsetX: 2,
        shadowOffsetY: 2,
      },
      label: {
        show: true,
        position: "right",
        formatter: "{b}",
        backgroundColor: "rgba(255, 255, 255, 0.85)",
        padding: [3, 8, 3, 8],
        borderColor: "#ddd",
        borderWidth: 1,
        borderRadius: 4,
        fontSize: 12,
        fontWeight: "normal",
        color: "#333",
        distance: 10,
        // 避免标签重叠
        overflow: "truncate",
        width: 40,
      },
      // 鼠标悬停效果
      emphasis: {
        itemStyle: {
          borderColor: "#ff7875",
          borderWidth: 3,
          shadowBlur: 15,
          shadowColor: "rgba(255, 120, 117, 0.5)",
          shadowOffsetX: 3,
          shadowOffsetY: 3,
        },
        label: {
          fontSize: 14,
          fontWeight: "bold",
          color: "#ff7875",
        },
        scale: true,
        scaleSize: 5,
      },
      category: node.type,
    };
  });

  const edges = graphData.value.edges.map((edge) => {
    // 根据关系类型设置不同颜色
    const relationColors = {
      毕业于: "#5470c6",
      任职于: "#91cc75",
      研究方向: "#fac858",
      获得奖项: "#ee6666",
      发表论文: "#73c0de",
      指导学生: "#3ba272",
      合作: "#fc8452",
      默认: "#888",
    };
    // 根据关系类型设置线宽
    const lineWidth = edge.label && relationColors[edge.label] ? 2.5 : 2;

    return {
      source: edge.source,
      target: edge.target,
      label: {
        show: true,
        formatter: edge.label || "关系",
        backgroundColor: "#fff",
        padding: [2, 6, 2, 6],
        borderColor: "#ccc",
        borderWidth: 1,
        borderRadius: 3,
        fontSize: 10,
        color: "#666",
        fontWeight: "normal",
      },
      lineStyle: {
        width: lineWidth,
        color: relationColors[edge.label] || relationColors.default,
        curveness: 0.15,
        type: "solid",
      },
      // 鼠标悬停效果
      emphasis: {
        lineStyle: {
          width: 4,
          color: "#ff7875",
          type: "solid",
        },
        label: {
          fontSize: 12,
          fontWeight: "bold",
          color: "#ff7875",
        },
      },
      symbol: ["none", "arrow"],
      symbolSize: [8, 14],
      // 设置边的z值，确保边显示在节点下方
      z: -1,
    };
  });

  console.log("准备渲染的节点:", nodes);
  console.log("准备渲染的边:", edges);

  // 配置图表选项
  const option = {
    tooltip: {
      trigger: "item",
      formatter: function (params) {
        if (params.dataType === "node") {
          return `${params.name}<br/>类型: ${params.data.category || "实体"}`;
        } else {
          return `关系: ${params.data.label}<br/>${params.data.source} → ${params.data.target}`;
        }
      },
      backgroundColor: "rgba(0, 0, 0, 0.7)",
      borderColor: "#fff",
      borderWidth: 1,
      textStyle: {
        color: "#fff",
      },
      padding: [8, 12],
      borderRadius: 6,
    },
    series: [
      {
        type: "graph",
        layout: "force",
        data: nodes,
        links: edges,
        roam: true,
        // 优化拖拽交互
        draggable: true,
        // 优化节点选择行为
        focusNodeAdjacency: true,
        // 优化节点高亮行为
        emphasis: {
          focus: "adjacency",
        },
        label: {
          show: true,
        },
        force: {
          // 优化力导向布局参数
          repulsion: 500,
          gravity: 0.1,
          edgeLength: 100,
          friction: 0.6,
          // 迭代次数
          iterations: 100,
        },
        // 配置缩放限制
        scaleLimit: {
          min: 0.2,
          max: 3,
        },
      },
    ],
  };

  try {
    chart.value.setOption(option);
    console.log("图表渲染成功");

    // 确保图表正确调整大小
    setTimeout(() => {
      if (chart.value) {
        chart.value.resize();
      }
    }, 100);
  } catch (error) {
    console.error("图表渲染失败:", error);
  }

  // 响应窗口大小变化
  window.addEventListener("resize", handleResize);
};

// 处理窗口大小变化
const handleResize = () => {
  if (chart.value) {
    chart.value.resize();
  }
};

// 组件挂载
onMounted(() => {
  // 设置图谱高度
  graphHeight.value = window.innerHeight - 200;
});

// 组件卸载
onUnmounted(() => {
  if (chart.value) {
    chart.value.dispose();
  }
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
.knowledge-graph-page {
  min-height: 100vh;
  background: #f7f4f3;
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

.search-section {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.search-container {
  position: relative;
  max-width: 290px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
  font-size: 16px;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: #4a9eff;
}

.search-btn {
  position: absolute;
  right: 4px;
  top: 4px;
  padding: 8px 16px;
  background: #4a9eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-btn:hover {
  background: #2a7fff;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-item {
  padding: 10px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.result-item:hover {
  background: #f5f5f5;
}

.result-item:last-child {
  border-bottom: none;
}

.current-teacher {
  padding: 10px 20px;
  text-align: center;
  background: white;
  margin: 0 20px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.graph-container {
  position: relative;
  margin: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  min-height: 600px;
  width: 100%;
}

.graph {
  width: 100%;
  height: 600px;
  min-height: 600px;
}

.graph-loading,
.graph-empty,
.graph-initial {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #666;
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

.legend {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: white;
  padding: 10px 16px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.legend-color.teacher {
  background: #5470c6;
}

.legend-color.entity {
  background: #91cc75;
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
