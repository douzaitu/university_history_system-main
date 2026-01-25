<template>
  <div class="knowledge-graph-container">
    <!-- 图谱容器 -->
    <div class="graph-container">
      <div
        ref="graph"
        class="graph"
        :style="{
          height: height + 'px',
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
      <div v-else-if="!hasData && teacherName" class="graph-empty">
        <p>未找到 {{ teacherName }} 的相关知识图谱数据</p>
      </div>

      <!-- 初始状态 -->
      <div v-else-if="!teacherName" class="graph-initial">
        <p>请选择教师查看知识图谱</p>
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
import { ref, onMounted, onUnmounted, watch } from "vue";

// 动态导入echarts
let echarts = null;

// Props
const props = defineProps({
  teacherName: {
    type: String,
    required: false,
    default: ""
  },
  height: {
    type: Number,
    default: 500
  }
});

// 状态管理
const graph = ref(null);
const chart = ref(null);
const loading = ref(false);
const errorMessage = ref("");

// 图谱数据
const graphData = ref({
  nodes: [],
  edges: [],
});

// 计算属性
const hasData = ref(false);

// 监听教师名称变化
watch(() => props.teacherName, (newName) => {
  console.log('KnowledgeGraphComponent: 监听到teacherName变化 =', newName);
  if (newName) {
    loadTeacherGraph(newName);
  } else {
    clearGraph();
  }
});

// 加载教师图谱数据
const loadTeacherGraph = async (teacherName) => {
  try {
    loading.value = true;
    errorMessage.value = "";
    
    const apiUrl = `http://localhost:8000/api/kg/teacher/${encodeURIComponent(teacherName)}/`;
    console.log('KnowledgeGraphComponent: 调用API =', apiUrl);
    
    const response = await fetch(apiUrl);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('KnowledgeGraphComponent: API返回数据 =', data);
    
    if (data.nodes && data.edges) {
      console.log('KnowledgeGraphComponent: 节点数量 =', data.nodes.length);
      console.log('KnowledgeGraphComponent: 边数量 =', data.edges.length);
      graphData.value = data;
      hasData.value = data.nodes.length > 0;
      
      // 渲染图谱
      renderGraph();
    } else {
      console.log('KnowledgeGraphComponent: 数据不完整，nodes或edges缺失');
      hasData.value = false;
      clearGraph();
    }
  } catch (error) {
    console.error("加载知识图谱失败:", error);
    errorMessage.value = "加载知识图谱失败，请稍后重试";
    hasData.value = false;
    clearGraph();
  } finally {
    loading.value = false;
  }
};

// 渲染图谱
const renderGraph = async () => {
  if (!graph.value) return;

  // 动态导入echarts
  if (!echarts) {
    try {
      echarts = await import("echarts");
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
  } catch (error) {
    console.error("ECharts初始化失败:", error);
    return;
  }

  // 如果没有数据，显示空状态
  if (graphData.value.nodes.length === 0) {
    chart.value.clear();
    return;
  }

  // 构建图谱选项
  const option = {
    tooltip: {
      formatter: (params) => {
        if (params.dataType === "edge") {
          return `${params.data.sourceName} → ${params.data.targetName}<br/>关系: ${params.data.label}`;
        } else {
          return `${params.data.name}<br/>类型: ${params.data.type}`;
        }
      },
    },
    animationDuration: 1500,
    animationEasingUpdate: "quinticInOut",
    series: [
      {
        type: "graph",
        layout: "force",
        data: graphData.value.nodes.map((node) => {
          // 根据节点类型设置不同样式
          const nodeSize = node.size || (node.type === "teacher" ? 40 : 30);
          const nodeColors = {
            teacher: "#5470c6",
            person: "#5470c6",
            entity: "#91cc75",
            school: "#fac858",
            organization: "#fac858",
            research: "#ee6666",
            paper: "#73c0de",
            award: "#3ba272",
            default: "#9a60b4",
          };
          // 强制所有节点使用圆形
          const symbolType = "circle";
          const symbolSize = nodeSize;
          
          return {
            id: node.id,
            name: node.label,
            symbolSize: symbolSize,
            symbol: "circle",
            type: node.type,
            x: node.x,
            y: node.y,
            value: node.value,
            itemStyle: {
              color: nodeColors[node.type] || nodeColors.default,
              borderColor: "#fff",
              borderWidth: 2,
              shadowBlur: 15,
              shadowColor: "rgba(0, 0, 0, 0.4)",
              shadowOffsetX: 0,
              shadowOffsetY: 2,
              borderRadius: 50,
            },
            label: {
              show: true,
              position: "right",
              distance: 12,
              formatter: (params) => {
                // 自动截断过长的标签
                const label = params.data.name;
                if (label.length > 10) {
                  return label.substring(0, 10) + "...";
                }
                return label;
              },
              fontSize: 14,
              fontWeight: "500",
              color: "#333",
              backgroundColor: "rgba(255, 255, 255, 0.9)",
              borderColor: "#ddd",
              borderWidth: 1,
              borderRadius: 6,
              padding: [4, 8, 4, 8],
              boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
            },
            emphasis: {
              itemStyle: {
                borderColor: "#ff7875",
                borderWidth: 3,
              },
              label: {
                fontSize: 14,
                color: "#ff7875",
              },
              scale: true,
            },
          };
        }),
        links: graphData.value.edges.map((edge) => {
          // 根据关系类型设置不同颜色
          const edgeColors = {
            "毕业于": "#1890ff",
            "任职于": "#52c41a",
            "研究方向": "#fa8c16",
            "发表论文": "#f5222d",
            "获得奖项": "#722ed1",
            "指导学生": "#13c2c2",
            "合作项目": "#eb2f96",
            default: "#8c8c8c",
          };
          
          return {
            source: edge.source,
            target: edge.target,
            sourceName: graphData.value.nodes.find((n) => n.id === edge.source)?.label || "",
            targetName: graphData.value.nodes.find((n) => n.id === edge.target)?.label || "",
            label: edge.label,
            lineStyle: {
              color: edgeColors[edge.label] || edgeColors.default,
              width: 2,
              curveness: 0.3,
            },
            symbol: ["circle", "arrow"],
            symbolSize: [4, 10],
            emphasis: {
              lineStyle: {
                width: 4,
                color: "#ff7875",
              },
            },
          };
        }),
        roam: true,
        scaleLimit: {
          min: 0.2,
          max: 3,
        },
        force: {
          repulsion: 1000,
          edgeLength: [120, 250],
          gravity: 0.05,
          friction: 0.6,
        },
        label: {
          show: true,
          position: "right",
          distance: 10,
        },
        edgeLabel: {
          show: true,
          fontSize: 10,
          formatter: (params) => params.data.label,
          backgroundColor: "rgba(255, 255, 255, 0.8)",
          borderColor: "#333",
          borderWidth: 1,
          borderRadius: 4,
          padding: [2, 4, 2, 4],
        },
      },
    ],
  };

  // 设置图表选项
  chart.value.setOption(option);
};

// 清除图谱
const clearGraph = () => {
  if (chart.value) {
    chart.value.clear();
  }
};

// 窗口大小变化时重绘
const handleResize = () => {
  if (chart.value) {
    chart.value.resize();
  }
};

onMounted(() => {
  window.addEventListener("resize", handleResize);
  
  // 如果初始时有教师名称，加载图谱
  if (props.teacherName) {
    loadTeacherGraph(props.teacherName);
  }
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  
  if (chart.value) {
    chart.value.dispose();
    chart.value = null;
  }
});
</script>

<style scoped>
.knowledge-graph-container {
  width: 100%;
}

.graph-container {
  position: relative;
  margin-bottom: 20px;
}

.graph {
  width: 100%;
  height: 500px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.graph-loading,
.graph-empty,
.graph-initial {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(249, 249, 249, 0.8);
  border-radius: 8px;
}

.loading-spinner {
  border: 3px solid rgba(84, 112, 198, 0.3);
  border-top: 3px solid #5470c6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legend {
  display: flex;
  gap: 20px;
  padding: 10px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-color.teacher {
  background-color: #5470c6;
}

.legend-color.entity {
  background-color: #91cc75;
}
</style>