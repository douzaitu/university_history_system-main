from rest_framework import serializers
from documents.models import Document

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
