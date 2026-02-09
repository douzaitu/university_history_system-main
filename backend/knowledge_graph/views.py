from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render
from .models import Entity, Relationship
from .serializers import (
    EntitySerializer, EntitySearchSerializer, 
    RelationshipSerializer, RelationshipDetailSerializer,
    GraphNodeSerializer, GraphEdgeSerializer
)
from .neo4j_db import Neo4jConnection

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

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def knowledge_graph_teacher(request, teacher_name):
    """获取教师知识图谱数据"""
    try:
        from services.graph_service import Neo4jGraphService
        
        result = Neo4jGraphService.get_teacher_subgraph(teacher_name)
        
        if result is None:
             # 如果返回None，可能是连接失败或查询错误，这里可以返回空图或错误
             # 为了保持兼容性，如果没有开启Neo4j，可能返回空
             return Response({'teacher': teacher_name, 'nodes': [], 'edges': []}, status=200)

        return Response(result)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def knowledge_graph_search(request):
    """搜索教师 - Neo4j"""
    query_param = request.GET.get('q', '')
    
    try:
        from services.graph_service import Neo4jGraphService
        
        teachers = Neo4jGraphService.search_entities(query_param)
        
        if teachers is None:
            return Response({'error': 'Neo4j connection failed'}, status=500)
            
        return Response({'teachers': teachers})
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

