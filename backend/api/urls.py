from django.urls import path, include
from rest_framework.routers import DefaultRouter
from documents.views import DocumentViewSet
from knowledge_graph import views as kg_views
from . import views

# 初始化 DRF 路由器
router = DefaultRouter()
# 注册文档相关路由
router.register(r'documents', DocumentViewSet)
# 注册知识图谱实体与关系 CRUD 路由
router.register(r'entities', kg_views.EntityViewSet)
router.register(r'relationships', kg_views.RelationshipViewSet)

urlpatterns = [
    # 包含路由器自动生成的 CRUD 路由
    path('', include(router.urls)),
    
    # 知识图谱特定功能路由
    path('knowledge-graph/', kg_views.knowledge_graph_data, name='knowledge-graph-data'), # 待确认是否仍需此全量接口
    path('entity-subgraph/<int:entity_id>/', kg_views.entity_subgraph, name='entity-subgraph'),
    path('kg/teacher/<str:teacher_name>/', kg_views.knowledge_graph_teacher, name='knowledge_graph_teacher'),
    path('kg/search/', kg_views.knowledge_graph_search, name='knowledge_graph_search'),
    
    # AI 助手功能路由
    path('ai/ask/', views.ask_ai_assistant, name='ask_ai_assistant'),
]
