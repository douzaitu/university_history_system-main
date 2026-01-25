<template>
  <div id="app">
    <RouterView />
    <!-- 页脚组件 -->
    <footer class="app-footer">
      <div class="footer-content">
        <div class="footer-left">
          <div class="footer-links">
          </div>
          <div class="footer-links">
            <span class="footer-link">友情链接</span>
            <a href="https://www.cdut.edu.cn" target="_blank" class="footer-link">成都理工大学官网</a>
            <a href="https://cist.cdut.edu.cn" target="_blank" class="footer-link">计算机与网络安全学院</a>
            <a href="https://www.720yun.com/vr/76ejO5ka5a6" target="_blank" class="footer-link">成都理工大学校史馆漫游</a>
          </div>
          <div class="footer-copyright">
            <span>版权所有</span>
            <span>成都理工大学</span>
            <span>成都市成华区二仙桥东三路1号</span>
            <span>邮编610059</span>
          </div>
        </div>
        <div class="footer-right">
          <div class="footer-info">
            <span>策划团队</span>
            <span>成都理工大学"数字记忆"团队</span>
          </div>
          <div class="footer-info">
            <span>技术支持</span>
            <span>成都理工大学计算机与网络安全学院</span>
          </div>
          <div class="footer-info">
            <span>问题反馈</span>
            <span>电话: 028-84078999</span>
          </div>
          <div class="footer-social">
            <div class="social-item">
              <a href="#" class="social-link">
                <img src="/微信.png" alt="官方微信" class="social-icon-img" />
                <span>官方微信</span>
              </a>
              <div class="wechat-qrcode">
                <img src="/微信二维码.jpg" alt="微信二维码" style="width: 100%; height: 100%; object-fit: contain;" />
              </div>
            </div>
            <div class="social-item">
              <a href="#" class="social-link">
                <img src="/微博.png" alt="官方微博" class="social-icon-img" />
                <span>官方微博</span>
              </a>
              <div class="wechat-qrcode">
                <img src="/微博二维码.jpg" alt="微博二维码" style="width: 100%; height: 100%; object-fit: contain;" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
    <!-- AI助手组件 -->
    <AIAssistant />
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";
import AIAssistant from "./components/AIAssistant.vue";
</script>

<style>
body {
  margin: 0;
  font-family: "Microsoft YaHei", sans-serif;
  background-color: #f5f6f7;
}

/* 页脚样式 */
.app-footer {
  background-color: #2b2b2b;
  color: #fff;
  padding: 30px 0;
  margin-top: 50px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-left {
  flex: 1;
}

.footer-right {
  flex: 1;
  text-align: right;
}

.footer-links {
  margin-bottom: 20px;
}

.footer-link {
  color: #b8c2cc;
  text-decoration: none;
  margin-right: 20px;
  font-size: 14px;
  transition: color 0.2s;
}

.footer-link:hover {
  color: #4a9eff;
}

.footer-copyright {
  font-size: 14px;
  color: #b8c2cc;
  line-height: 1.6;
}

.footer-copyright span {
  margin-right: 15px;
}

.footer-info {
  margin-bottom: 15px;
  font-size: 14px;
  line-height: 1.6;
  color: #b8c2cc;
}

.footer-info span {
  margin-right: 15px;
}

.footer-social {
  display: flex;
  justify-content: flex-end;
  gap: 30px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.social-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.social-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #b8c2cc;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
  padding: 8px;
  border-radius: 4px;
}

.social-link:hover {
  color: #4a9eff;
  background: rgba(255, 255, 255, 0.05);
}

.social-icon-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  transition: transform 0.2s;
}

.social-link:hover .social-icon-img {
  transform: scale(1.1);
}

/* 微信二维码悬停效果 */
.wechat-qrcode {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 10px;
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  z-index: 100;
  padding: 8px;
}

.social-item:hover .wechat-qrcode {
  opacity: 1;
  visibility: visible;
}

/* 二维码占位符 */
.qrcode-placeholder {
  width: 100%;
  height: 100%;
  position: relative;
}

.qrcode-grid {
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    45deg,
    #f0f0f0 0px,
    #f0f0f0 2px,
    #ffffff 2px,
    #ffffff 4px
  );
  border-radius: 4px;
}

.qrcode-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 30%;
  height: 30%;
  background: #333;
  border-radius: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .footer-social {
    justify-content: center;
  }
  
  .wechat-qrcode {
    bottom: auto;
    top: 100%;
    margin-top: 10px;
    margin-bottom: 0;
  }
}

.footer-left {
  flex: 1;
  text-align: left;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .footer-content {
    flex-direction: column;
    gap: 30px;
  }
  
  .footer-right {
    text-align: left;
  }
}

@media (max-width: 768px) {
  .app-footer {
    padding: 20px 0;
  }
  
  .footer-content {
    padding: 0 16px;
  }
  
  .footer-links {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .footer-link {
    margin-right: 10px;
  }
  
  .footer-copyright span {
    display: block;
    margin-right: 0;
    margin-bottom: 5px;
  }
  
  .footer-info span {
    display: block;
    margin-right: 0;
    margin-bottom: 5px;
  }
}
</style>
