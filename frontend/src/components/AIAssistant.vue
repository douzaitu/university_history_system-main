<template>
  <div
    class="ai-assistant"
    ref="assistantRef"
    @mousedown="startDrag"
    @touchstart="startDrag"
  >
    <!-- 悬浮按钮 -->
    <div class="assistant-container">
      <button
        class="assistant-btn"
        @click="handleButtonClick"
      >
        <img src="/logo.svg" alt="成都理工大学" class="logo-icon" />
      </button>
      <span class="assistant-label">成小理</span>
    </div>

    <!-- 聊天窗口 -->
    <div v-if="showChat" class="chat-window">
      <div class="chat-header">
        <div class="header-content">
          <img src="/logo.svg" alt="成都理工大学" class="header-logo" />
          <h3>成小理</h3>
        </div>
        <button class="close-btn" @click="closeChat">×</button>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <img
            v-if="message.role === 'ai'"
            src="/logo.svg"
            alt="成都理工大学"
            class="message-logo"
          />
          <!-- 使用 v-html 渲染格式化后的内容 -->
          <span 
            class="message-content" 
            v-html="formatMessage(message.content)"
          ></span>
        </div>

        <div v-if="loading" class="message ai loading">
          <img src="/logo.svg" alt="成都理工大学" class="message-logo" />
          <span class="message-content">正在思考中...</span>
        </div>
      </div>

      <div class="chat-input">
        <input
          v-model="userInput"
          @keyup.enter="sendMessage"
          placeholder="有什么问题想问我的吗？"
          :disabled="loading"
        />
        <button @click="sendMessage" :disabled="loading || !userInput.trim()">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from "vue";
import { askAI } from "../api/ai";

const showChat = ref(false);
const userInput = ref("");
const messages = ref([]);
const loading = ref(false);
const messagesContainer = ref(null);
const assistantRef = ref(null);

// 拖拽相关状态
const isDragging = ref(false);
const hasDragged = ref(false);
const startX = ref(0);
const startY = ref(0);
const offsetX = ref(0);
const offsetY = ref(0);

// 预定义一些欢迎语
const welcomeMessages = [
  "你好！我是成小理，我可以帮你查询学校相关的信息。",
  "你可以问我关于学校历史、人物、事件等各种问题。",
  "比如：'赵仕波老师的研究方向是什么？' 或 '计算机学院有哪些老师？'",
];

// 初始化消息
messages.value = welcomeMessages.map((msg) => ({
  role: "ai",
  content: msg,
}));

// 切换聊天窗口
const toggleChat = () => {
  showChat.value = !showChat.value;
  if (showChat.value) {
    scrollToBottom();
  }
};

// 关闭聊天窗口
const closeChat = () => {
  showChat.value = false;
};

// 发送消息
const sendMessage = async () => {
  const question = userInput.value.trim();
  if (!question || loading.value) return;

  // 添加用户消息
  messages.value.push({
    role: "user",
    content: question,
  });

  userInput.value = "";
  loading.value = true;

  // 滚动到底部
  scrollToBottom();

  try {
    // 调用后端API
    const data = await askAI(question);

    // 添加AI回复
    messages.value.push({
      role: "ai",
      content: data.answer,
    });
  } catch (error) {
    console.error("AI助手请求失败:", error);
    let errorMsg = "抱歉，我遇到了点问题。请稍后再试。";
    if (error.response && error.response.data && error.response.data.answer) {
      errorMsg = error.response.data.answer;
    } else if (error.message) {
      errorMsg += ` (${error.message})`;
    }
    messages.value.push({
      role: "ai",
      content: errorMsg,
    });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 监听消息变化，自动滚动
watch(messages, scrollToBottom, { deep: true });

// 拖拽开始
const startDrag = (e) => {
  const target = e.target;
  
  // 检查是否是交互元素（输入框、按钮等）
  // 注意：悬浮球(.assistant-btn)虽然是按钮，但是它是拖拽手柄，需要特殊处理
  const isInteractive = 
    target.tagName === "INPUT" || 
    target.tagName === "TEXTAREA" || 
    target.tagName === "BUTTON" || 
    target.closest("button");

  // 定义可拖拽区域
  const isFloatingBtn = target.closest(".assistant-btn");
  const isHeader = target.closest(".chat-header");
  const isFooter = target.closest(".chat-input");

  // 判定逻辑
  let allowDrag = false;

  if (isFloatingBtn) {
    // 悬浮球允许拖拽
    allowDrag = true;
  } else if (isHeader) {
    // 头部：排除关闭按钮和其他交互元素
    if (!target.closest(".close-btn") && !target.closest("button")) {
      allowDrag = true;
    }
  } else if (isFooter) {
    // 底部：排除输入框和按钮
    if (!isInteractive) {
      allowDrag = true;
    }
  }

  // 如果不允许拖拽，直接返回，保持默认行为（通过输入、选择文本等）
  if (!allowDrag) {
    return;
  }

  // 以下是拖拽逻辑...
  isDragging.value = true;
  hasDragged.value = false;

  // 处理鼠标和触摸事件
  const clientX = e.type === "mousedown" ? e.clientX : e.touches[0].clientX;
  const clientY = e.type === "mousedown" ? e.clientY : e.touches[0].clientY;

  startX.value = clientX;
  startY.value = clientY;

  // 获取当前位置
  const rect = assistantRef.value.getBoundingClientRect();
  offsetX.value = clientX - rect.left;
  offsetY.value = clientY - rect.top;

  // 防止默认行为（仅在确实拖拽时）
  e.preventDefault();
};

// 拖拽中
const drag = (e) => {
  if (!isDragging.value) return;

  // 标记已经发生拖拽
  hasDragged.value = true;

  // 处理鼠标和触摸事件
  const clientX = e.type === "mousemove" ? e.clientX : e.touches[0].clientX;
  const clientY = e.type === "mousemove" ? e.clientY : e.touches[0].clientY;

  // 计算新位置
  const newX = clientX - offsetX.value;
  const newY = clientY - offsetY.value;

  // 限制在视口内
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  const elementWidth = assistantRef.value.offsetWidth;
  const elementHeight = assistantRef.value.offsetHeight;

  const clampedX = Math.max(0, Math.min(newX, viewportWidth - elementWidth));
  const clampedY = Math.max(0, Math.min(newY, viewportHeight - elementHeight));

  // 更新位置
  assistantRef.value.style.left = `${clampedX}px`;
  assistantRef.value.style.top = `${clampedY}px`;
  assistantRef.value.style.bottom = "auto";
  assistantRef.value.style.right = "auto";

  // 防止默认行为
  e.preventDefault();
};

// 拖拽结束
const stopDrag = () => {
  isDragging.value = false;
  // 延迟重置 hasDragged，确保点击事件能够正确判断
  setTimeout(() => {
    hasDragged.value = false;
  }, 100);
};

// 格式化消息内容（Markdown -> HTML）
const formatMessage = (content) => {
  if (!content) return "";
  
  // 1. 转义 HTML 特殊字符（防止 XSS）
  let text = content
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // 2. 加粗: **text**
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // 3. 标题: ### text
  text = text.replace(/^###\s+(.*$)/gm, '<h3 style="margin: 10px 0 5px; font-size: 16px;">$1</h3>');

  // 4. 列表项: - text 或 * text
  text = text.replace(/^[\-\*]\s+(.*$)/gm, '• $1');
  
  // 5. 将链接显示出来（可选，如有需要）
  // text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');

  return text;
};

// 按钮点击处理
const handleButtonClick = () => {
  // 只有在没有拖拽的情况下才触发 toggleChat
  if (!hasDragged.value) {
    toggleChat();
  }
};

// 组件挂载时添加全局事件监听器
onMounted(() => {
  window.addEventListener("mousemove", drag);
  window.addEventListener("mouseup", stopDrag);
  window.addEventListener("touchmove", drag);
  window.addEventListener("touchend", stopDrag);
});

// 组件卸载时移除全局事件监听器
onUnmounted(() => {
  window.removeEventListener("mousemove", drag);
  window.removeEventListener("mouseup", stopDrag);
  window.removeEventListener("touchmove", drag);
  window.removeEventListener("touchend", stopDrag);
});
</script>

<style scoped>
.ai-assistant {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
}

.assistant-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.assistant-label {
  font-size: 12px;
  color: #666;
  font-family: "Microsoft YaHei", sans-serif;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.assistant-container:hover .assistant-label {
  color: #4c8bf5;
  transform: translateY(-2px);
}

.assistant-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: white;
  border: 2px solid #e8e8e8;
  color: #4c8bf5;
  font-size: 24px;
  cursor: grab; /* 移动光标 */
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.assistant-btn:active {
  cursor: grabbing;
}

.assistant-btn:hover {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #4c8bf5;
}

.assistant-btn:active {
  transform: scale(0.95);
}

.chat-window {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 350px;
  height: 500px;
  background: #f0f8ff;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
  transition: all 0.3s ease;
  cursor: default; /* 恢复默认光标 */
}

.chat-window:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  transform: translateY(-5px);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-header {
  padding: 15px 20px;
  background: white;
  color: #4c8bf5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e8e8e8;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  cursor: grab; /* 顶部拖拽手柄 */
}

.chat-header:active {
   cursor: grabbing;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
}

.header-logo {
  width: 24px;
  height: 24px;
  margin-right: 8px;
}

.message-logo {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  flex-shrink: 0;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%,
  20%,
  50%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-3px);
  }
  60% {
    transform: translateY(-2px);
  }
}

.chat-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.close-btn {
  background: rgba(76, 139, 245, 0.1);
  border: 1px solid rgba(76, 139, 245, 0.2);
  color: #4c8bf5;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(76, 139, 245, 0.2);
  transform: scale(1.2) rotate(90deg);
  box-shadow: 0 2px 8px rgba(76, 139, 245, 0.3);
  border-color: #4c8bf5;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f0f8ff;
  cursor: text; /* 内容区域使用输入光标 */
}

.message {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: messageAppear 0.3s ease-out;
}

@keyframes messageAppear {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-icon {
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}

.message-content {
  padding: 14px 18px;
  border-radius: 20px;
  max-width: 80%;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap; /* 允许换行 */
  font-family: "Microsoft YaHei", sans-serif;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message.user .message-content:hover {
  background: #7986cb;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transform: translateX(-2px);
}

.message.ai .message-content:hover {
  background: #f0f8ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  transform: translateX(2px);
}

.message.user .message-content {
  background: linear-gradient(135deg, #8594d7 0%);
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 8px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.message.ai .message-content {
  background: white;
  color: #333;
  border: 1px solid #f0f0f0;
  border-bottom-left-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 消息内容中的加粗样式 */
.message-content :deep(strong) {
  font-weight: 700;
  color: #2c3e50;
}

/* 标题样式 */
.message-content :deep(h3) {
  margin: 10px 0 5px;
  font-size: 15px;
  font-weight: 700;
  color: #4c8bf5;
}

.message.loading .message-content {
  color: #666;
  font-style: italic;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.message.loading .message-content::after {
  content: "";
  width: 18px;
  height: 18px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #4c8bf5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  box-shadow: 0 0 10px rgba(76, 139, 245, 0.2);
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.chat-input {
  padding: 15px;
  background: white;
  border-top: 1px solid #e8e8e8;
  display: flex;
  gap: 10px;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  cursor: grab; /* 底部拖拽区域 */
}

.chat-input:active {
  cursor: grabbing;
}

.chat-input input {
  flex: 1;
  padding: 14px 18px;
  border: 1px solid #e8e8e8;
  border-radius: 24px;
  outline: none;
  font-size: 14px;
  transition: all 0.3s ease;
  font-family: "Microsoft YaHei", sans-serif;
  background: white;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  cursor: text; /* 输入框内使用文本光标 */
}

.chat-input input:hover {
  border-color: #4c8bf5;
  box-shadow:
    inset 0 1px 3px rgba(0, 0, 0, 0.05),
    0 0 0 2px rgba(76, 139, 245, 0.05);
}

.chat-input input:focus {
  border-color: #4c8bf5;
  box-shadow:
    inset 0 1px 3px rgba(0, 0, 0, 0.05),
    0 0 0 2px rgba(76, 139, 245, 0.1);
}

.chat-input button {
  background: none;
  border: none;
  color: #4c8bf5;
  font-size: 20px;
  cursor: pointer;
  padding: 0 10px;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-input button:hover {
  transform: scale(1.1);
}

.chat-input button:active {
  transform: scale(0.95);
}

.chat-input input::placeholder {
  color: #999;
  font-style: italic;
}

.chat-input button {
  padding: 14px 24px;
  background: white;
  color: #4c8bf5;
  border: 2px solid #4c8bf5;
  border-radius: 24px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
  font-family: "Microsoft YaHei", sans-serif;
  box-shadow: 0 4px 12px rgba(76, 139, 245, 0.1);
}

.chat-input button:hover:not(:disabled) {
  background: #4c8bf5;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 139, 245, 0.3);
}

.chat-input button:active:not(:disabled) {
  transform: translateY(0);
}

.chat-input button:disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-window {
    width: 320px;
    height: 450px;
  }

  .assistant-btn {
    width: 55px;
    height: 55px;
    font-size: 22px;
  }

  .chat-messages {
    padding: 15px;
  }

  .chat-input {
    padding: 12px;
  }
}
</style>
