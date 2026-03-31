校史知识图谱系统后端文档
1. 项目说明
本后端基于 Django + Django REST Framework 实现，负责文档管理、实体关系管理、图谱查询接口、AI 问答接口，以及业务数据与 Neo4j 图数据库同步。

2. 目录说明
api：统一 API 路由与接口入口
documents：文档上传、状态管理、文档处理
knowledge_graph：实体关系模型、图谱查询、Neo4j 同步
services：AI 服务、图查询服务、LLM 抽取桥接
users：自定义用户模型与角色字段
3. 运行环境
Python 3.8+
PostgreSQL
Neo4j
Ollama（用于本地抽取模型）
4. 环境变量
在 backend 目录准备 .env，示例：
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

5. 启动步骤
安装依赖
pip install -r requirements.txt
执行迁移
python manage.py makemigrations
python manage.py migrate
创建管理员
python manage.py createsuperuser
启动服务
python manage.py runserver
启动异步任务（另开终端）
python manage.py qcluster

6. API 概览
接口路由入口见 urls.py。

6.1 资源类接口
实体 CRUD：/api/entities/
关系 CRUD：/api/relationships/
文档 CRUD：/api/documents/
6.2 图谱查询接口
图谱概览：/api/knowledge-graph/
子图查询：/api/entity-subgraph/{entity_id}/
教师图谱：/api/kg/teacher/{teacher_name}/
图谱搜索：/api/kg/search/?q=关键词
最短路径：/api/kg/path/?source=源实体&target=目标实体
6.3 AI 接口
AI 问答：/api/ai/ask/（POST）

7. 权限说明
全局 REST 默认需认证（IsAuthenticated）
部分图谱查询与 AI 接口为允许匿名访问
具体以视图配置为准，参考 settings.py 与 views.py

8. 文档处理与图谱同步流程
上传文档后进入 documents 流程
提取实体关系并保存业务数据
通过信号 + Django Q 异步同步到 Neo4j
前端图谱查询优先从 Neo4j 返回
相关代码：

views.py
services.py
signals.py
tasks.py

9. 管理命令
全量同步到 Neo4j
python manage.py sync_neo4j

清理任务队列
python manage.py clear_django_q_tasks --all

清理全量数据
python manage.py clear_all_data

管理命令实现位于：

sync_neo4j.py
clear_django_q_tasks.py
clear_all_data.py

10. 常见问题
图谱查不到数据：检查 Neo4j 配置和 qcluster 是否运行
文档状态长期 processing：检查异步任务与日志
AI 回答失败：检查 DEEPSEEK_API_KEY 与外网连通性

11. 安全建议
不提交真实 .env
生产环境关闭 DEBUG
不在文档中放固定管理员密码
收敛跨域来源白名单