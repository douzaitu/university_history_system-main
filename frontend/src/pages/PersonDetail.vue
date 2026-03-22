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
        <a href="javascript:void(0)" @click.prevent="goBack" class="back">← 返回</a>
        <div class="site-title">
          人物详情 <span class="sub">dm.cdut.edu.cn</span>
        </div>
      </div>
      <div class="actions">
        <button class="icon" @click="toggleFavorite">
          {{ isFavorite ? "❤️" : "🤍" }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="person" class="content">
      <!-- 顶部导航标签 -->
      <div class="nav-tabs">
        <div
          class="tab"
          :class="{ active: activeTab === 'info' }"
          @click="activeTab = 'info'"
        >
          知识信息
        </div>
        <div
          class="tab"
          :class="{ active: activeTab === 'graph' }"
          @click="activeTab = 'graph'"
        >
          关系图谱
        </div>
      </div>

      <!-- 标签内容区域 -->
      <div class="tab-content">
        <!-- 知识信息标签 -->
        <div v-if="activeTab === 'info'" class="info-tab">
          <div class="header-section">
            <h1 class="name">{{ person.name }}</h1>
            <div class="meta-row">
              <span class="read-count">{{ person.readCount }} 阅读</span>
              <span class="separator">｜</span>
              <span class="update-time">{{
                formatUpdateTime(person.lastUpdated)
              }}</span>
            </div>
            <div class="actions-bar">
              <div class="formats">
                <span class="format">XML</span>
                <span class="format">JSON</span>
                <span class="format">NT</span>
              </div>
              <div class="action-buttons-small">
                <button class="btn-small" @click="toggleFavorite">
                  {{ isFavorite ? "★" : "☆" }} 收藏
                </button>
                <button class="btn-small" @click="sharePerson">分享</button>
                <button class="btn-small">标签</button>
              </div>
            </div>
          </div>

          <div class="person-info">
            <div class="info-left">
              <div class="info-item">
                <span class="info-label">姓名</span>
                <span class="info-value">{{ person.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">人物类别</span>
                <span class="info-value">{{ person.category }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">人物简介</span>
                <span class="info-value bio-content">{{
                  formattedBio.join("")
                }}</span>
              </div>
            </div>
            <div class="info-right">
              <div class="photo-section" v-if="person.photo">
                <img
                  :src="person.photo"
                  :alt="`${person.name}的照片`"
                  @error="handleImageError"
                  class="person-photo"
                />
                <div class="photo-nav">
                  <button class="nav-btn prev" @click="navigateToPrevious">
                    ‹
                  </button>
                  <button class="nav-btn next" @click="navigateToNext">
                    ›
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 关系图谱标签 -->
        <div v-if="activeTab === 'graph'" class="graph-tab">
          <div class="knowledge-graph-section">
            <h2 class="section-title">知识图谱</h2>
            <KnowledgeGraphComponent
              :teacher-name="person.name"
              :height="600"
            />
          </div>
        </div>
      </div>
    </div>

    <div v-else class="notfound">
      <div class="notfound-content">
        <h2>未找到人物信息</h2>
        <p>您访问的人物信息不存在或已被移除</p>
        <router-link to="/people" class="back-btn">返回人物库</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getEntityDetail } from "../api/entityDetail";
import KnowledgeGraphComponent from "../components/KnowledgeGraphComponent.vue";

const route = useRoute();
const router = useRouter();

const goBack = () => {
    // 尝试关闭窗口（针对新标签页打开的情况）
    window.close();
    
    // 如果窗口没有关闭，说明不是脚本打开的，执行路由回退
    if (!window.closed) {
        if (window.history.length > 1) {
            router.back();
        } else {
            // 如果没有历史记录，回退到列表页
            router.push('/people');
        }
    }
};

// 状态管理
const person = ref(null);
const loading = ref(false);
const isFavorite = ref(false);
const showDefaultPhoto = ref(false);
const activeTab = ref("info"); // 默认选中知识信息标签

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

// 从姓名中提取纯姓名，去除职位信息
const extractPureName = (name) => {
  if (!name) return name;

  // 定义常见职位关键词
  const positionKeywords = [
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
    "教授",
    "副教授",
    "讲师",
    "助教",
    "博导",
    "硕导",
  ];

  // 遍历关键词，从姓名中移除职位信息
  let pureName = name;
  for (const keyword of positionKeywords) {
    pureName = pureName.replace(keyword, "");
  }

  // 去除多余的空格
  return pureName.replace(/\s+/g, "").trim();
};

// 加载人物详情数据
const fetchPersonDetail = async (id) => {
  try {
    loading.value = true;
    console.log("加载人物详情，ID:", id);

    const response = await getEntityDetail(id);
    console.log("人物详情API返回:", response);

    if (response) {
      // 提取纯姓名，去除职位信息
      const pureName = extractPureName(response.name);

      // 优先使用后端返回的字段，如果为空则使用自动提取的
      const jobTitle = extractPosition(response.description);
      const personCategory = response.subtype || jobTitle; // 如果没有细分类型，默认显示职位或自动提取的结果

      person.value = {
        id: response.id,
        name: pureName,
        category: personCategory, // 这里对应前端显示的"人物类别"
        bio: response.description,
        // 修复这里：使用实际的photo_url，如果没有显示默认图片
        photo: response.photo_url || "/People/default.jpg",
        readCount: 0,
        lastUpdated: new Date().toISOString(),
        dataVersion: "1.0",
      };
      console.log("PersonDetail: 原始name =", response.name);
      console.log("PersonDetail: 提取纯姓名后 =", pureName);
      console.log("PersonDetail: 传递给知识图谱组件的teacherName =", pureName);

      // 检查收藏状态
      checkFavoriteStatus();

      // 增加阅读计数
      increaseReadCount();
    }
  } catch (error) {
    console.error("加载人物详情失败:", error);
    person.value = null;
  } finally {
    loading.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  if (route.params.id) {
    fetchPersonDetail(route.params.id);
  }
});

// 监听路由变化
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      fetchPersonDetail(newId);
    }
  },
);

// 格式化简介内容，按句号分段并智能去重（保持原始顺序）
const formattedBio = computed(() => {
  if (!person.value?.bio) return ["暂无简介"];

  // 预处理：将邮箱等特殊格式的文本中的句号替换为临时标记，避免被错误分割
  let processedBio = person.value.bio;

  // 匹配邮箱地址，将其中的句号替换为临时标记
  const emailRegex = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
  const emails = [];
  processedBio = processedBio.replace(emailRegex, (match) => {
    emails.push(match);
    return `_EMAIL_${emails.length - 1}_`;
  });

  // 将长文本按句号分段
  const paragraphs = processedBio
    .split(/[。.]/)
    .map((p) => p.trim())
    .filter((p) => p.length > 0);

  // 智能处理：合并零散的短句，特别是邮箱相关的部分
  const mergedParagraphs = [];
  let currentPara = "";

  paragraphs.forEach((para, index) => {
    // 检查当前段落是否是邮箱的一部分（包含邮箱标记）
    if (para.includes("_EMAIL_")) {
      // 如果当前段落包含邮箱标记，直接添加
      if (currentPara) {
        mergedParagraphs.push(currentPara);
        currentPara = "";
      }
      mergedParagraphs.push(para);
    }
    // 检查当前段落是否是可能的邮箱后缀（如 edu, cn 等）
    else if (
      (para === "edu" || para === "cn" || para === "com" || para === "net") &&
      index > 0 &&
      paragraphs[index - 1].includes("@")
    ) {
      // 如果上一段包含 @ 符号，且当前段是常见域名后缀，则合并到上一段
      if (mergedParagraphs.length > 0) {
        mergedParagraphs[mergedParagraphs.length - 1] += "." + para;
      }
    }
    // 检查当前段落是否太短（可能是被错误分割的）
    else if (para.length < 10) {
      // 如果当前段落很短，尝试与下一段合并
      if (currentPara) {
        currentPara += " " + para;
      } else {
        currentPara = para;
      }
    } else {
      // 否则，正常处理
      if (currentPara) {
        mergedParagraphs.push(currentPara);
        currentPara = "";
      }
      mergedParagraphs.push(para);
    }
  });

  // 添加最后一个段落
  if (currentPara) {
    mergedParagraphs.push(currentPara);
  }

  // 智能去重：去除重复和被包含的段落，同时保持原始顺序
  const uniqueParagraphs = [];
  const paragraphsToKeep = new Array(mergedParagraphs.length).fill(true);

  // 第一遍：标记所有应该被删除的段落
  for (let i = 0; i < mergedParagraphs.length; i++) {
    if (!paragraphsToKeep[i]) continue; // 跳过已经被标记为删除的段落

    const currentPara = mergedParagraphs[i];

    for (let j = i + 1; j < mergedParagraphs.length; j++) {
      if (!paragraphsToKeep[j]) continue; // 跳过已经被标记为删除的段落

      const nextPara = mergedParagraphs[j];

      // 检查两个段落是否有包含关系或完全相同
      if (currentPara === nextPara) {
        // 如果完全相同，删除后面的段落
        paragraphsToKeep[j] = false;
      } else if (currentPara.includes(nextPara)) {
        // 如果当前段落包含下一个段落，删除下一个段落
        paragraphsToKeep[j] = false;
      } else if (nextPara.includes(currentPara)) {
        // 如果下一个段落包含当前段落，删除当前段落
        paragraphsToKeep[i] = false;
        break; // 当前段落已被标记为删除，无需再检查
      }
    }
  }

  // 第二遍：收集所有应该保留的段落
  for (let i = 0; i < mergedParagraphs.length; i++) {
    if (paragraphsToKeep[i]) {
      uniqueParagraphs.push(mergedParagraphs[i]);
    }
  }

  // 恢复邮箱中的句号
  return uniqueParagraphs
    .map((p) => {
      // 恢复邮箱地址
      return p.replace(/_EMAIL_(\d+)_/g, (match, index) => {
        return emails[parseInt(index)] || match;
      });
    })
    .map((p) => p + "。");
});

// 相关人物（暂时设为空，因为需要额外API支持）
const relatedPeople = computed(() => {
  return [];
});

// 图片加载错误处理
const handleImageError = (event) => {
  // 图片加载失败时，显示默认图片
  if (person.value) {
    person.value.photo = "/People/default.jpg";
  }
};

// 格式化更新时间
const formatUpdateTime = (timestamp) => {
  if (!timestamp) return "未知";

  const date = new Date(timestamp);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
    2,
    "0",
  )}-${String(date.getDate()).padStart(2, "0")}`;
};

// 切换收藏状态
const toggleFavorite = () => {
  isFavorite.value = !isFavorite.value;

  // 保存收藏状态到localStorage
  const favorites = JSON.parse(localStorage.getItem("favoritePeople") || "[]");
  if (isFavorite.value && person.value) {
    if (!favorites.includes(person.value.id)) {
      favorites.push(person.value.id);
    }
  } else if (person.value) {
    const index = favorites.indexOf(person.value.id);
    if (index > -1) {
      favorites.splice(index, 1);
    }
  }
  localStorage.setItem("favoritePeople", JSON.stringify(favorites));
};

// 检查收藏状态
const checkFavoriteStatus = () => {
  if (!person.value) return;

  const favorites = JSON.parse(localStorage.getItem("favoritePeople") || "[]");
  isFavorite.value = favorites.includes(person.value.id);
};

// 增加阅读计数
const increaseReadCount = () => {
  if (!person.value) return;

  // 简单的内存中增加计数
  person.value.readCount = (person.value.readCount || 0) + 1;

  // 如果需要持久化，可以保存到localStorage
  const readCounts = JSON.parse(
    localStorage.getItem("personReadCounts") || "{}",
  );
  readCounts[person.value.id] = (readCounts[person.value.id] || 0) + 1;
  localStorage.setItem("personReadCounts", JSON.stringify(readCounts));
};

// 分享功能（占位）
const sharePerson = () => {
  if (!person.value) return;

  const shareText = `查看${person.value.name}的详细信息 - 数字记忆系统`;
  const shareUrl = window.location.href;

  // 简单的复制到剪贴板
  navigator.clipboard
    .writeText(`${shareText}: ${shareUrl}`)
    .then(() => alert("分享链接已复制到剪贴板"))
    .catch((err) => console.error("复制失败:", err));
};

// 搜索功能（占位）
const handleSearch = () => {
  // 可以实现简单的搜索界面或跳转到搜索页面
  alert("搜索功能即将推出");
};

// 导航到上一个人物
const navigateToPrevious = async () => {
  try {
    // 获取所有人物列表
    const response = await fetch(
      "http://localhost:8000/api/entities/?type=person",
    );
    const people = await response.json();

    if (people && people.length > 0) {
      // 找到当前人物的索引
      const currentIndex = people.findIndex((p) => p.id === person.value.id);

      if (currentIndex > 0) {
        // 导航到上一个人物
        const previousPerson = people[currentIndex - 1];
        router.push(`/people/${previousPerson.id}`);
      } else {
        // 如果是第一个人物，则导航到最后一个人物
        const lastPerson = people[people.length - 1];
        router.push(`/people/${lastPerson.id}`);
      }
    }
  } catch (error) {
    console.error("获取人物列表失败:", error);
    alert("获取人物列表失败");
  }
};

// 导航到下一个人物
const navigateToNext = async () => {
  try {
    // 获取所有人物列表
    const response = await fetch(
      "http://localhost:8000/api/entities/?type=person",
    );
    const people = await response.json();

    if (people && people.length > 0) {
      // 找到当前人物的索引
      const currentIndex = people.findIndex((p) => p.id === person.value.id);

      if (currentIndex < people.length - 1) {
        // 导航到下一个人物
        const nextPerson = people[currentIndex + 1];
        router.push(`/people/${nextPerson.id}`);
      } else {
        // 如果是最后一个人物，则导航到第一个人物
        const firstPerson = people[0];
        router.push(`/people/${firstPerson.id}`);
      }
    }
  } catch (error) {
    console.error("获取人物列表失败:", error);
    alert("获取人物列表失败");
  }
};
</script>

<style scoped>
/* 知识图谱区域样式 */
.knowledge-graph-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.section-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #2d3748;
  border-bottom: 2px solid #4a9eff;
  padding-bottom: 10px;
  font-weight: 700;
}

/* 主页面样式 */
.detail-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
  color: #2d3748;
}

/* 顶部导航栏 */
.topbar {
  height: 80px;
  background: white;
  color: #2d3748;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-sizing: border-box;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Logo部分 */
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

/* 导航部分 */
.nav-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.back {
  color: #4a9eff;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.back:hover {
  color: #3366cc;
}

.site-title {
  font-weight: 700;
  font-size: 18px;
}

.site-title .sub {
  font-weight: 400;
  font-size: 12px;
  color: #94a3b8;
  margin-left: 8px;
}

/* 操作部分 */
.actions {
  display: flex;
  align-items: center;
}

.actions .icon {
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 18px;
  margin-left: 20px;
  cursor: pointer;
  transition:
    color 0.2s ease,
    transform 0.2s ease;
}

.actions .icon:hover {
  color: #4a9eff;
  transform: scale(1.1);
}

/* 内容区域 */
.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* 顶部导航标签 */
.nav-tabs {
  display: flex;
  background: white;
  border-radius: 8px 8px 0 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.tab {
  flex: 1;
  padding: 16px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.tab:hover {
  background: #f8fafc;
}

.tab.active {
  background: #f0f9ff;
  color: #3b82f6;
  border-bottom-color: #3b82f6;
  font-weight: 600;
}

/* 标签内容区域 */
.tab-content {
  background: white;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 32px;
  min-height: 600px;
}

/* 知识信息标签 */
.header-section {
  margin-bottom: 32px;
}

.name {
  font-size: 36px;
  margin: 0 0 12px;
  color: #1a202c;
  font-weight: 700;
  line-height: 1.2;
}

.meta-row {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 16px;
}

.read-count {
  font-weight: 500;
}

.separator {
  margin: 0 8px;
  color: #cbd5e1;
}

/* 操作栏 */
.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.formats {
  display: flex;
  gap: 12px;
}

.format {
  padding: 4px 8px;
  background: #f1f5f9;
  border-radius: 4px;
  font-size: 12px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.format:hover {
  background: #e2e8f0;
}

.action-buttons-small {
  display: flex;
  gap: 8px;
}

.btn-small {
  padding: 6px 12px;
  background: #f1f5f9;
  color: #64748b;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-small:hover {
  background: #e2e8f0;
  color: #475569;
}

/* 人物信息布局 */
.person-info {
  display: flex;
  gap: 48px;
}

.info-left {
  flex: 1;
}

.info-item {
  display: flex;
  margin-bottom: 24px;
  align-items: flex-start;
  flex-wrap: wrap;
  word-break: break-word;
}

.info-label {
  width: 120px;
  color: #64748b;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.info-value {
  color: #2d3748;
  font-size: 15px;
  font-weight: 500;
  flex: 1;
  word-wrap: break-word;
  white-space: normal;
  overflow-wrap: break-word;
}

.bio-content {
  line-height: 1.8;
  text-align: justify;
  word-wrap: break-word;
  white-space: normal;
  overflow-wrap: break-word;
  overflow: hidden;
}

/* 照片区域 */
.info-right {
  width: 240px;
  flex-shrink: 0;
}

.photo-section {
  position: relative;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  height: 320px;
}

.person-photo {
  width: 100%;
  height: 320px;
  object-fit: cover;
  display: block;
  object-position: top;
}

/* 照片导航按钮 */
.photo-nav {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  transform: translateY(-50%);
  padding: 0 8px;
}

.nav-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 16px;
  font-weight: 600;
}

.nav-btn:hover {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 关系图谱标签 */
.graph-tab {
  padding: 0;
}

/* 时间轴标签 */
.timeline-section {
  padding: 20px;
}

.timeline-content {
  margin-top: 20px;
  line-height: 1.8;
  color: #64748b;
}

/* 未找到页面 */
.notfound {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  padding: 24px;
}

.notfound-content {
  background: white;
  border-radius: 12px;
  padding: 48px;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.notfound-content h2 {
  margin: 0 0 16px;
  font-size: 28px;
  color: #2d3748;
}

.notfound-content p {
  margin: 0 0 32px;
  color: #64748b;
  font-size: 16px;
}

.back-btn {
  display: inline-block;
  padding: 12px 24px;
  background: #4a9eff;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #3366cc;
  transform: translateY(-2px);
}

/* 加载状态 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  gap: 16px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4a9eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
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

  .content {
    padding: 24px 20px;
  }

  .person-info {
    gap: 32px;
  }

  .info-right {
    width: 200px;
  }

  .photo-section,
  .person-photo {
    height: 280px;
  }

  .person-photo {
    object-fit: cover;
    object-position: top;
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

  .content {
    padding: 20px 16px;
  }

  .tab-content {
    padding: 24px;
  }

  .name {
    font-size: 28px;
  }

  /* 在平板设备上，保持左侧文字右侧图片的布局 */
  .person-info {
    flex-direction: row;
    gap: 24px;
    flex-wrap: wrap;
  }

  .info-right {
    width: 200px;
    flex-shrink: 0;
  }

  .photo-section,
  .person-photo {
    height: 240px;
  }

  .person-photo {
    object-fit: cover;
    object-position: top;
  }

  /* 操作栏在平板设备上垂直排列 */
  .actions-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .formats {
    width: 100%;
    justify-content: flex-start;
  }

  .action-buttons-small {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .content {
    padding: 16px 12px;
  }

  .tab-content {
    padding: 16px;
  }

  .name {
    font-size: 24px;
  }

  /* 在手机设备上，信息和照片垂直排列 */
  .person-info {
    flex-direction: column;
    gap: 24px;
  }

  .info-right {
    width: 100%;
    max-width: 240px;
    margin: 0 auto;
  }

  .info-item {
    flex-direction: column;
    gap: 8px;
  }

  .info-label {
    width: auto;
  }
}
</style>
