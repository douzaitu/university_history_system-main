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
    def process_document(self, request, pk=None):
        """处理文档：提取实体和关系"""
        document = self.get_object()
        
        # 检查文件类型
        if document.file_type != 'excel' and not document.file.name.endswith(('.xlsx', '.xls')):
             return Response({"error": "目前仅支持处理Excel文件"}, status=400)

        # 更新状态为处理中
        document.status = 'processing'
        document.processing_start_time = timezone.now()
        document.save()

        try:
            from .services import DocumentProcessor
            result = DocumentProcessor.process_excel(document)
            
            if result.get("status") == "success":
                document.status = 'processed'
                document.processed_data = result
            else:
                document.status = 'error'
                document.processed_data = result
                
        except Exception as e:
            document.status = 'error'
            document.processed_data = {"error": str(e)}
        
        document.processing_end_time = timezone.now()
        document.save()
        
        return Response(DocumentDetailSerializer(document).data)
