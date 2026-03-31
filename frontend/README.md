校史知识图谱系统前端文档
1. 项目说明
前端基于 Vue 3 + Vite，提供首页、人物/地点/机构/学科/事件库、详情页、知识图谱可视化与 AI 助手交互界面。

2. 技术栈
Vue 3
Vue Router
Axios
ECharts
Vite
依赖与脚本见 package.json。

3. 目录说明
src/router：路由配置
src/pages：各业务页面
src/components：通用组件与 AI 助手组件
src/api：接口请求封装

4. 本地启动
安装依赖
npm install
启动开发
npm run dev

5. 路由说明
路由定义见 index.js。

主要页面：
/：首页
/people 与 /people/:id
/places 与 /places/:id
/organizations 与 /organizations/:id
/subjects 与 /subjects/:id
/events 与 /events/:id
/knowledge-graph

6. 接口对接说明
请求封装入口见 request.js。
当前默认后端地址为本地 8000 端口，建议后续改为环境变量管理，避免写死地址。

接口模块：
图谱接口：knowledgeGraph.js
详情接口：entityDetail.js
AI 接口：ai.js

7. 页面与接口映射
人物/地点/机构/学科/事件列表页：实体类型筛选接口
详情页：实体详情接口
图谱页：搜索、教师图谱、子图相关接口
AI 助手组件：问答接口
页面参考：
People.vue
KnowledgeGraph.vue
AIAssistant.vue

8. 联调注意事项
后端和前端端口要一致（默认 8000 与 5173）
后端需开启跨域白名单并包含前端地址
图谱相关功能依赖后端图数据库数据同步

9. 常见问题
页面空数据：后端接口无返回或类型筛选条件不匹配
图谱不显示：接口返回 nodes/edges 为空或字段不符合渲染要求
AI 无响应：后端 AI 接口错误或密钥缺失
