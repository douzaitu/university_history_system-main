<template>
  <div class="ai-assistant">
    <!-- 悬浮按钮 -->
    <div class="assistant-container">
      <button class="assistant-btn" @click="toggleChat">
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
          <span class="message-content">{{ message.content }}</span>
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
import { ref, watch, nextTick } from "vue";
import { askAI } from "../api/ai";

const showChat = ref(false);
const userInput = ref("");
const messages = ref([]);
const loading = ref(false);
const messagesContainer = ref(null);

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
    messages.value.push({
      role: "ai",
      content: "抱歉，我遇到了点问题。请稍后再试。",
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
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
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
  line-height: 1.5;
  word-wrap: break-word;
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
