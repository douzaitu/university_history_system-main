## 项目说明

校史知识图谱管理系统是一个集成了知识图谱数据管理、可视化展示和AI智能助手功能的现代化Web应用系统。该系统采用前后端分离架构，后端基于Django REST Framework构建，前端使用Vue 3开发，通过Neo4j存储和管理知识图谱数据，并集成DeepSeek AI提供智能问答服务。

## 核心功能

知识图谱管理：实体和关系的CRUD操作
可视化展示：交互式知识图谱可视化
智能搜索：基于知识图谱的智能查询
AI助手：集成了DeepSeek的智能问答系统
后台管理：完整的后台管理界面

## 环境要求

必需软件
Python 3.8+
Node.js 14+
Neo4j Desktop
Git

## 安装依赖

后端依赖：

# backend/requirements.txt

# 核心框架

Django==5.2.8
djangorestframework==3.16.1
django-cors-headers==4.9.0

# 数据库和外部服务

neo4j==6.0.3
requests==2.32.5
python-dotenv==1.1.0

# 数据处理

pandas==2.3.3
openpyxl==3.1.5
ollama==0.6.1

# 图像处理

Pillow==12.0.0

# Django基础依赖（通常会自动安装）

asgiref==3.10.0
sqlparse==0.5.3
tzdata==2025.2

前端依赖：

# 核心框架：

Vue 3 (vue@3.5.26)
Vue Router 4 (vue-router@4.6.4)

# 构建工具：

Vite (vite@7.3.0)
@vitejs/plugin-vue (@vitejs/plugin-vue@6.0.3)

# 主要库：

Axios (axios@1.13.2)
ECharts (echarts@6.0.0)

## 项目结构

university_history_system/
├── backend/ # Django后端
├── frontend/ # Vue前端
├── reg5.py # 知识图谱导入脚本
└── README.md # 本文档

## 后端启动

1.进入后端目录 cd backend 2.激活虚拟环境 代码下载目录\university_history_system-main\venv\Scripts\activate 3.启动后端 python manage.py runserver

## 前端启动

1.进入前端目录 cd frontend 2.启动前端 npm run dev

## Neo4j数据库配置

1.启动Neo4j
打开Neo4j Desktop
创建一个新的数据库实例
设置数据库名称（如：school-history）
设置密码为：12345678
启动数据库2.验证连接
打开浏览器访问：http://localhost:7474
用户名：neo4j
密码：12345678
成功登录后表示Neo4j已正常启动

## 启动顺序

1.启动Neo4j数据库2.启动Django后端服务器3.启动Vue前端服务器

## 网站访问

前端访问：http://localhost:5173
后端访问：http://localhost:8000/api/management/
后端管理员身份信息：
用户名：admin
密码admin123456
Neo4j访问：http://localhost:7474/
