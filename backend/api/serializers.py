from rest_framework import serializers
from documents.models import Document
from knowledge_graph.models import Entity, Relationship
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'created_at']

# 文档相关的序列化器
class DocumentUploadSerializer(serializers.ModelSerializer):
    """文档上传专用的序列化器"""
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'file_type']
    
    def validate_file(self, value):
        """验证上传的文件"""
        # 检查文件大小（限制为50MB）
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("文件大小不能超过50MB")
        
        # 检查文件类型
        allowed_types = ['txt', 'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_types:
            raise serializers.ValidationError(f"不支持的文件类型: {ext}")
        
        return value

class DocumentDetailSerializer(serializers.ModelSerializer):
    """文档详情序列化器"""
    uploader_name = serializers.CharField(source='uploader.username', read_only=True)
    processing_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'file_type', 'uploader', 'uploader_name',
                 'upload_time', 'status', 'processed_data', 'file_size',
                 'processing_start_time', 'processing_end_time', 'processing_duration']
    
    def get_processing_duration(self, obj):
        """计算处理时长"""
        if obj.processing_start_time and obj.processing_end_time:
            duration = obj.processing_end_time - obj.processing_start_time
            return str(duration)
        return None

# 为了向后兼容，保留原有的DocumentSerializer
class DocumentSerializer(serializers.ModelSerializer):
    uploader_name = serializers.CharField(source='uploader.username', read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'file_type', 'uploader', 'uploader_name', 
                 'upload_time', 'status', 'processed_data']

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
                 'target_entity_name', 'relationship_type', 'description', 'confidence']

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