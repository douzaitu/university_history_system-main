from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from neo4j import GraphDatabase  # 确保这行存在
from documents.models import Document
from knowledge_graph.models import Entity, Relationship
from .serializers import *
import os
import requests

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        """根据动作选择不同的序列化器"""
        if self.action == 'create':
            return DocumentUploadSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return DocumentDetailSerializer
        return DocumentSerializer  # 默认使用原来的序列化器保持兼容
    
    def perform_create(self, serializer):
        """创建文档时设置上传者"""
        serializer.save(uploader=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """按文件类型筛选文档"""
        file_type = request.query_params.get('type')
        if file_type:
            documents = Document.objects.filter(file_type=file_type)
            serializer = self.get_serializer(documents, many=True)
            return Response(serializer.data)
        return Response({"error": "请提供type参数"}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """按状态筛选文档"""
        status_param = request.query_params.get('status')
        if status_param:
            documents = Document.objects.filter(status=status_param)
            serializer = self.get_serializer(documents, many=True)
            return Response(serializer.data)
        return Response({"error": "请提供status参数"}, status=400)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新文档状态"""
        document = self.get_object()
        new_status = request.data.get('status')
        processed_data = request.data.get('processed_data')
        
        if new_status not in dict(Document.STATUS_CHOICES):
            return Response({"error": "无效的状态"}, status=400)
        
        # 更新状态
        document.status = new_status
        
        # 如果是开始处理，记录开始时间
        if new_status == 'processing' and not document.processing_start_time:
            document.processing_start_time = timezone.now()
        
        # 如果是处理完成，记录结束时间
        if new_status in ['processed', 'analyzed', 'error'] and not document.processing_end_time:
            document.processing_end_time = timezone.now()
        
        # 更新处理后的数据
        if processed_data is not None:
            document.processed_data = processed_data
        
        document.save()
        
        serializer = DocumentDetailSerializer(document)
        return Response(serializer.data)

class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """重写get_queryset以支持按类型过滤"""
        queryset = Entity.objects.all()
        
        # 支持按类型过滤
        entity_type = self.request.query_params.get('type')
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
            
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'search':
            return EntitySearchSerializer
        return EntitySerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索实体"""
        query = request.query_params.get('q', '')
        entity_type = request.query_params.get('type', '')
        
        entities = Entity.objects.all()
        
        # 按名称搜索
        if query:
            entities = entities.filter(name__icontains=query)
        
        # 按类型筛选
        if entity_type:
            entities = entities.filter(entity_type=entity_type)
        
        # 按创建时间排序
        entities = entities.order_by('-created_at')
        
        page = self.paginate_queryset(entities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(entities, many=True)
        return Response(serializer.data)

class RelationshipViewSet(viewsets.ModelViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RelationshipDetailSerializer
        return RelationshipSerializer
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """按关系类型筛选"""
        relationship_type = request.query_params.get('type')
        if relationship_type:
            relationships = Relationship.objects.filter(relationship_type=relationship_type)
            serializer = self.get_serializer(relationships, many=True)
            return Response(serializer.data)
        return Response({"error": "请提供type参数"}, status=400)
    
    @action(detail=False, methods=['get'])
    def between_entities(self, request):
        """获取两个实体之间的关系"""
        source_id = request.query_params.get('source_id')
        target_id = request.query_params.get('target_id')
        
        if not source_id or not target_id:
            return Response({"error": "请提供source_id和target_id参数"}, status=400)
        
        relationships = Relationship.objects.filter(
            source_entity_id=source_id,
            target_entity_id=target_id
        )
        
        serializer = self.get_serializer(relationships, many=True)
        return Response(serializer.data)

# 知识图谱数据API视图
@api_view(['GET'])
def knowledge_graph_data(request):
    """获取知识图谱数据（节点和边）"""
    # 获取所有实体作为节点
    entities = Entity.objects.all()
    
    nodes = []
    for entity in entities:
        # 根据实体类型设置不同的大小
        size_map = {
            'person': 3,
            'organization': 2,
            'event': 2,
            'location': 2,
            'time': 1
        }
        
        nodes.append({
            'id': entity.id,
            'label': entity.name,
            'type': entity.entity_type,
            'description': entity.description,
            'size': size_map.get(entity.entity_type, 1)
        })
    
    # 获取所有关系作为边
    relationships = Relationship.objects.all()
    
    edges = []
    for relationship in relationships:
        edges.append({
            'source': relationship.source_entity.id,
            'target': relationship.target_entity.id,
            'label': relationship.get_relationship_type_display(),
            'description': relationship.description,
            'confidence': relationship.confidence
        })
    
    return Response({
        'nodes': nodes,
        'edges': edges
    })

@api_view(['GET'])
def entity_subgraph(request, entity_id):
    """获取以指定实体为中心的子图"""
    try:
        center_entity = Entity.objects.get(id=entity_id)
    except Entity.DoesNotExist:
        return Response({"error": "实体不存在"}, status=404)
    
    nodes = []
    edges = []
    
    # 添加中心节点
    nodes.append({
        'id': center_entity.id,
        'label': center_entity.name,
        'type': center_entity.entity_type,
        'description': center_entity.description,
        'size': 3,  # 中心节点较大
        'center': True
    })
    
    # 获取直接关系（一度关系）
    outgoing_rels = center_entity.outgoing_relationships.all()
    incoming_rels = center_entity.incoming_relationships.all()
    
    # 处理出边关系
    for rel in outgoing_rels:
        target = rel.target_entity
        nodes.append({
            'id': target.id,
            'label': target.name,
            'type': target.entity_type,
            'description': target.description,
            'size': 2
        })
        edges.append({
            'source': center_entity.id,
            'target': target.id,
            'label': rel.get_relationship_type_display(),
            'description': rel.description,
            'confidence': rel.confidence,
            'direction': 'outgoing'
        })
    
    # 处理入边关系
    for rel in incoming_rels:
        source = rel.source_entity
        nodes.append({
            'id': source.id,
            'label': source.name,
            'type': source.entity_type,
            'description': source.description,
            'size': 2
        })
        edges.append({
            'source': source.id,
            'target': center_entity.id,
            'label': rel.get_relationship_type_display(),
            'description': rel.description,
            'confidence': rel.confidence,
            'direction': 'incoming'
        })
    
    # 去重节点
    unique_nodes = {node['id']: node for node in nodes}.values()
    
    return Response({
        'center_entity': {
            'id': center_entity.id,
            'name': center_entity.name,
            'type': center_entity.entity_type
        },
        'nodes': list(unique_nodes),
        'edges': edges
    })


def api_management_panel(request):
    """API管理面板"""
    return render(request, 'api/management_panel.html')


def entity_management(request):
    """实体管理界面"""
    entities = Entity.objects.all()
    return render(request, 'api/entity_management.html', {'entities': entities})


def relationship_management(request):
    """关系管理界面"""
    relationships = Relationship.objects.all()
    return render(request, 'api/relationship_management.html', {'relationships': relationships})

# 在 views.py 末尾添加以下代码

@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # 添加权限装饰器
def knowledge_graph_teacher(request, teacher_name):
    """获取教师知识图谱数据 - 新功能"""
    try:
        from .neo4j_db import Neo4jConnection
        
        # 查询教师的关系网络
        query = """
        MATCH (teacher:Entity {name: $teacher_name})-[r:RELATION]->(target:Entity)
        RETURN teacher.name as source, r.type as relation, target.name as target, 'outgoing' as direction
        UNION
        MATCH (source:Entity)-[r:RELATION]->(teacher:Entity {name: $teacher_name})
        RETURN source.name as source, r.type as relation, teacher.name as target, 'incoming' as direction
        """
        
        result = Neo4jConnection.query(query, {"teacher_name": teacher_name})
        
        if result is None:
             return Response({'error': 'Neo4j connection failed'}, status=500)

        nodes = []
        edges = []
        node_set = set()
        
        # 添加中心节点（教师）
        nodes.append({
            'id': teacher_name,
            'label': teacher_name,
            'type': 'teacher',
            'size': 25
        })
        node_set.add(teacher_name)
        
        for record in result:
            source = record['source']
            target = record['target']
            relation = record['relation']
            direction = record['direction']
            
            # 添加源节点
            if source not in node_set:
                nodes.append({
                    'id': source,
                    'label': source,
                    'type': 'entity',
                    'size': 15
                })
                node_set.add(source)
            
            # 添加目标节点
            if target not in node_set:
                nodes.append({
                    'id': target,
                    'label': target,
                    'type': 'entity',
                    'size': 15
                })
                node_set.add(target)
            
            # 添加边
            edges.append({
                'source': source,
                'target': target,
                'label': relation,
                'direction': direction
            })
        
        return Response({
            'teacher': teacher_name,
            'nodes': nodes,
            'edges': edges
        })
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def knowledge_graph_search(request):
    """搜索教师 - 新功能"""
    query_param = request.GET.get('q', '')  # 重命名变量避免冲突
    
    try:
        from .neo4j_db import Neo4jConnection
        
        result = Neo4jConnection.query(
            "MATCH (n:Entity) WHERE n.name CONTAINS $query RETURN n.name as name LIMIT 10",
            {"query": query_param}
        )
        
        if result is None:
            return Response({'error': 'Neo4j connection failed'}, status=500)
            
        teachers = [record['name'] for record in result]
        
        return Response({'teachers': teachers})
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
# AI助手相关视图函数
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def ask_ai_assistant(request):
    """AI助手问答接口"""
    try:
        question = request.data.get('question', '').strip()
        
        if not question:
            return Response({'error': '问题不能为空'}, status=400)
        
        # 从settings获取DeepSeek API密钥
        from django.conf import settings
        api_key = settings.DEEPSEEK_API_KEY
        
        if not api_key or api_key == 'sk-test12345678901234567890':
            return Response({
                'answer': 'AI助手正在配置中，请稍后再试。如需立即使用，请配置正确的DeepSeek API密钥。'
            })
        
        # DeepSeek API配置
        DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
        
        # 构建系统提示词
        system_prompt = """你是一个校史知识图谱AI助手。你的任务是：
        1. 回答关于学校历史、人物、事件、机构等问题
        2. 帮助用户理解知识图谱数据
        3. 提供友好的帮助和指导
        4. 如果不知道答案，可以引导用户到相关页面查看
        
        当前系统包含教师信息、学院机构、历史事件等数据。
        你可以根据用户的问题提供相关信息和指导。"""
        
        # 准备请求数据
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "stream": False,
            "max_tokens": 1000
        }
        
        # 调用DeepSeek API
        import requests
        response = requests.post(
            DEEPSEEK_API_URL, 
            headers=headers, 
            json=data, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            return Response({'answer': answer})
        else:
            # 如果API调用失败，返回一个友好的提示
            error_msg = f"API请求失败: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', error_msg)
                except:
                    pass
            return Response({
                'answer': f'抱歉，AI助手暂时无法回答。错误信息: {error_msg}。请检查API密钥是否正确。'
            })
            
    except Exception as e:
        return Response({
            'answer': f'AI助手遇到问题: {str(e)}。请稍后再试。'
        }, status=500)