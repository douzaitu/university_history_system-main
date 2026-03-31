## 项目说明

校史知识图谱管理系统是一个集成了知识图谱数据管理、可视化展示和AI智能助手功能的现代化Web应用系统。该系统采用前后端分离架构，后端基于Django REST Framework构建，前端使用Vue 3开发，通过Neo4j和PostgreSQL存储和管理知识图谱数据，并集成DeepSeek AI提供智能问答服务。

## 核心功能

1.文档管理与处理
支持上传文档并进行结构化处理，提取实体与关系。
2.知识图谱管理
支持实体与关系的增删改查，并可按类型筛选。
3.图谱可视化
支持图谱概览、实体子图、查询。
4.AI 问答
支持基于图谱数据上下文的智能问答。
5.后台管理
支持通过 Django Admin 管理用户、文档、实体和关系数据

## 技术栈

1.后端
Django、Django REST Framework、Django Q、Neo4j Driver
2.前端
Vue 3、Vue Router、Axios、ECharts、Vite
3.数据层
PostgreSQL（业务数据）
Neo4j（图数据）
ollama（模型）
本地媒体文件（上传文档与图片）

## 项目结构

university_history_system-main/ # 项目根目录
├── backend/ # Django后端服务、数据模型、API、异步任务、图数据库同步逻辑
├── frontend/ # Vue前端页面、路由、接口封装、可视化组件
└── README.md # 项目总说明文档

# 环境要求

1.Python 3.8 及以上
2.Node.js 14 及以上
3.PostgreSQL
4.Neo4j
5.Git
6.ollama（下载qwen2:7b模型）

# 环境变量配置

在 backend 目录下创建 .env 文件，并按需填写：

DJANGO_SECRET_KEY=请填写
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.postgresql
DB_NAME=school_history_db
DB_USER=postgres
DB_PASSWORD=请填写
DB_HOST=localhost
DB_PORT=5432

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=请填写

DEEPSEEK_API_KEY=请填写

说明：

不建议在代码中硬编码数据库和图数据库密码。
不要提交真实 .env 到仓库。

## PostgreSQL数据库配置

1. 安装PostgreSQL 17+
2. 创建数据库 `school_history_db`

## Neo4j数据库配置

1.启动Neo4j
打开Neo4j Desktop
创建一个新的数据库实例
设置数据库名称（如：school-history）
设置密码
启动数据库
2.验证连接
打开浏览器访问：http://localhost:7474
输入用户名和密码
成功登录后表示Neo4j已正常启动

# 启动顺序建议

1.启动 PostgreSQL 与 Neo4j、ollama
2.启动后端 Django
3.启动 Django Q 异步任务
4.启动前端 Vite

# 后端启动

1.进入后端目录
cd backend
2.安装依赖
pip install -r requirements.txt
3.执行数据库迁移
python manage.py makemigrations
python manage.py migrate
4.创建管理员
python manage.py createsuperuser
5.启动 Django 服务
python manage.py runserver
6.启动异步任务进程（另开终端）
python manage.py qcluster

# 前端启动

1.进入前端目录
cd frontend
2.安装依赖
npm install
3.启动开发服务
npm run dev

# 常用访问地址

1.前端
http://localhost:5173
2.后端管理后台
http://127.0.0.1:8000/admin/
3.Neo4j Browser
http://localhost:7474

# 数据流说明

1.用户上传文档后进入文档处理流程
2.系统提取实体与关系并写入业务数据库
3.通过异步任务将数据同步到 Neo4j
4.前端图谱查询优先读取 Neo4j 数据
5.AI 问答基于图谱检索上下文进行回答

# 常见问题排查

1.图谱为空
检查 Neo4j 是否启动、连接参数是否正确、qcluster 是否运行。
2.文档上传后无处理结果
检查异步任务进程是否启动，查看后端日志。
3.前端请求失败
检查后端是否启动、跨域配置是否包含前端地址。
4.AI 无法回答
检查 DEEPSEEK_API_KEY 是否有效。