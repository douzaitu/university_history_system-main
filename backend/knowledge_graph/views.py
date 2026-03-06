from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from .models import Entity, Relationship
from .serializers import (
    EntitySerializer, EntitySearchSerializer, 
    RelationshipSerializer, RelationshipDetailSerializer,
    GraphNodeSerializer, GraphEdgeSerializer
)
# 引入统一的图服务
from services.graph_service import graph_service

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

        # 支持按是否核心过滤
        is_primary = self.request.query_params.get('is_primary')
        if is_primary:
            is_primary_bool = is_primary.lower() == 'true'
            queryset = queryset.filter(is_primary=is_primary_bool)
            
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'search':
            return EntitySearchSerializer
        return EntitySerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """实体搜索"""
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
            
        # 优先使用 Neo4j 搜索（更高效，支持模糊匹配）
        try:
            results = graph_service.search_entities(query)
            # 如果 Neo4j 返回了结果，直接构造 Response
            if results:
                # 兼容前端期望的格式，这里简单包装一下
                return Response(results)
        except Exception as e:
            print(f"Neo4j search failed, falling back to SQLite: {e}")
            
        # 降级方案：使用 SQLite 搜索
        queryset = self.get_queryset().filter(name__icontains=query)[:10]
        serializer = self.get_serializer(queryset, many=True)
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
        """按类型筛选关系"""
        rel_type = request.query_params.get('type')
        if rel_type:
            queryset = self.get_queryset().filter(relationship_type=rel_type)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({"error": "请提供type参数"}, status=400)
    
    @action(detail=False, methods=['get'])
    def between_entities(self, request):
        """查询两个实体之间的关系"""
        source_id = request.query_params.get('source')
        target_id = request.query_params.get('target')
        
        if source_id and target_id:
            queryset = self.get_queryset().filter(
                source_entity_id=source_id,
                target_entity_id=target_id
            )
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({"error": "请提供source和target参数"}, status=400)

# 知识图谱数据API视图 - 已优化
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def knowledge_graph_data(request):
    """
    获取知识图谱概览数据
    优化：不再返回全量数据，而是返回关键节点概览（Top N）
    """
    try:
        limit = int(request.GET.get('limit', 50))
    except ValueError:
        limit = 50
    
    try:
        data = graph_service.get_graph_overview(limit=limit)
        return Response(data)
    except Exception as e:
        # 降级：如果 Neo4j 挂了，返回空的或者少量 SQLite 数据
        print(f"Failed to get graph overview from Neo4j: {e}")
        return Response({'nodes': [], 'edges': [], 'error': 'Graph service unavailable'})

def _entity_subgraph_fallback(center_entity):
    """SQLite 降级查询方案"""
    nodes = []
    edges = []
    
    nodes.append({
        'id': center_entity.id,
        'label': center_entity.name,
        'type': center_entity.entity_type,
        'description': center_entity.description,
        'size': 25,
        'is_center': True
    })
    
    # 简单的 ORM 查询
    for rel in center_entity.outgoing_relationships.all()[:50]:
        target = rel.target_entity
        nodes.append({'id': target.id, 'label': target.name, 'type': target.entity_type, 'size': 15})
        edges.append({'source': center_entity.id, 'target': target.id, 'label': rel.get_relationship_type_display()})
        
    for rel in center_entity.incoming_relationships.all()[:50]:
        source = rel.source_entity
        nodes.append({'id': source.id, 'label': source.name, 'type': source.entity_type, 'size': 15})
        edges.append({'source': source.id, 'target': center_entity.id, 'label': rel.get_relationship_type_display()})
        
    # 去重
    unique_nodes = {str(node['id']): node for node in nodes}.values()
    
    return Response({
        'center': center_entity.name, # 保持格式一致
        'nodes': list(unique_nodes),
        'edges': edges
    })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def entity_subgraph(request, entity_id):
    """
    获取以指定实体为中心的子图
    优化：使用 Neo4j 查询以获得更好性能
    """
    try:
        # 先确认实体存在，并获取名字
        try:
            center_entity = Entity.objects.get(id=int(entity_id))
        except (Entity.DoesNotExist, ValueError):
            return Response({"error": "实体不存在"}, status=404)
            
        # 尝试从 Neo4j 获取子图
        graph_data = graph_service.get_entity_subgraph(center_entity.name)
        
        if graph_data:
            return Response(graph_data)
        else:
            # 如果 Neo4j 中没有（可能同步失败），回退到 SQLite 查询
            return _entity_subgraph_fallback(center_entity)
            
    except Exception as e:
        print(f"Error getting subgraph: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def knowledge_graph_path(request):
    """
    查询两个实体之间的最短路径
    """
    source_name = request.GET.get('source')
    target_name = request.GET.get('target')
    
    if not source_name or not target_name:
        return Response({'error': '请提供 source 和 target 参数'}, status=400)
        
    result = graph_service.get_shortest_path(source_name, target_name)
    
    if not result:
        return Response({'nodes': [], 'edges': [], 'message': '未找到路径'}, status=404)
        
    return Response(result)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def knowledge_graph_search(request):
    """搜索实体 (Neo4j)"""
    query = request.GET.get('q', '')
    if not query:
        return Response({'teachers': []}) # 保持字段名兼容前端
        
    results = graph_service.search_entities(query)
    
    # 保持兼容性，转换一下格式
    # 原来的 search_entities 返回的是 names list
    # 新的 graph_service.search_entities 返回 [{'name':..,'type':..}]
    # 这里我们只返回名字列表以保持兼容
    if results and isinstance(results[0], dict):
        names = [r['name'] for r in results]
    else:
        names = results
        
    return Response({'teachers': names})

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def knowledge_graph_teacher(request, teacher_name):
    """获取教师知识图谱数据"""
    # 复用通用的实体子图逻辑
    result = graph_service.get_entity_subgraph(teacher_name)
    if result:
        return Response(result)
    return Response({'nodes': [], 'edges': []}) 
