from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Document
from .serializers import DocumentUploadSerializer, DocumentDetailSerializer, DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    # 根据需要调整权限，这里示例为 AllowAny，实际项目建议 IsAuthenticated
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
        # 注意：如果允许匿名上传，request.user 可能是 AnonymousUser，需要做校验
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(uploader=self.request.user)
        else:
            serializer.save()
    
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
        
        # 注意：这里需要 Document.STATUS_CHOICES 可用
        # 如果 Document 模型定义了 STATUS_CHOICES，则可以直接使用
        if hasattr(Document, 'STATUS_CHOICES') and new_status not in dict(Document.STATUS_CHOICES):
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
