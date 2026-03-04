from rest_framework import serializers
from .models import Entity, Relationship

# 实体相关的序列化器
class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'name', 'entity_type', 'description', 'photo_url', 'source_documents']

class EntitySearchSerializer(serializers.ModelSerializer):
    """实体搜索序列化器"""
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Entity
        fields = ['id', 'name', 'entity_type', 'description', 'photo_url', 'document_count']  # 确保有photo_url
    
    def get_document_count(self, obj):
        """获取关联的文档数量"""
        return obj.source_documents.count()

# 关系相关的序列化器
class RelationshipSerializer(serializers.ModelSerializer):
    source_entity_name = serializers.CharField(source='source_entity.name', read_only=True)
    target_entity_name = serializers.CharField(source='target_entity.name', read_only=True)
    
    class Meta:
        model = Relationship
        fields = ['id', 'source_entity', 'source_entity_name', 'target_entity', 
                 'target_entity_name', 'relationship_type']

class RelationshipDetailSerializer(serializers.ModelSerializer):
    """关系详情序列化器"""
    source_entity_name = serializers.CharField(source='source_entity.name', read_only=True)
    source_entity_type = serializers.CharField(source='source_entity.entity_type', read_only=True)
    target_entity_name = serializers.CharField(source='target_entity.name', read_only=True)
    target_entity_type = serializers.CharField(source='target_entity.entity_type', read_only=True)
    
    class Meta:
        model = Relationship
        fields = ['id', 'source_entity', 'source_entity_name', 'source_entity_type',
                 'target_entity', 'target_entity_name', 'target_entity_type',
                 'relationship_type', 'description', 'confidence']

# 图谱数据序列化器
class GraphNodeSerializer(serializers.Serializer):
    """图谱节点序列化器"""
    id = serializers.IntegerField()
    label = serializers.CharField()
    type = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    size = serializers.IntegerField(default=1)

class GraphEdgeSerializer(serializers.Serializer):
    """图谱边序列化器"""
    source = serializers.IntegerField()
    target = serializers.IntegerField()
    label = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    confidence = serializers.FloatField(default=1.0)

class GraphDataSerializer(serializers.Serializer):
    """图谱数据序列化器"""
    nodes = GraphNodeSerializer(many=True)
    edges = GraphEdgeSerializer(many=True)
