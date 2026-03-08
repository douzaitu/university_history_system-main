from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.http import StreamingHttpResponse
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'uploader', 'upload_time', 'status']
    list_filter = ['file_type', 'status', 'upload_time']
    search_fields = ['title', 'content']
    actions = ['process_selected_documents']
    
    # 状态字段设为只读，不应由管理员手动修改
    readonly_fields = ['status', 'processed_data', 'processing_start_time', 'processing_end_time']
    # 移除 file_size 显示 (如果之前有显示的话，但标准 Admin 中如果没有 fieldsets 就会显示所有非 exclude 的字段)
    
    def process_selected_documents(self, request, queryset):
        """处理选中的文档（使用 Django-Q 后台处理）"""
        from django_q.tasks import async_task
        from .services import process_document_task

        # 只处理选中的第一个文件
        if queryset.count() > 1:
            self.message_user(request, "为了保证系统性能，每次请只选择一个文档进行处理。", messages.WARNING)
            return

        document = queryset.first()

        # 兼容 word, pdf, excel
        allowed_extensions = ('.xlsx', '.xls', '.docx', '.doc', '.pdf')
        if not document.file.name.lower().endswith(allowed_extensions):
            self.message_user(request, "不支持的文件格式。仅支持 Excel (.xlsx, .xls), Word (.docx, .doc), PDF (.pdf)。", messages.ERROR)
            return

        # 更新状态
        document.status = 'processing'
        document.processing_start_time = timezone.now()
        document.save()

        # 提交到 Django-Q 任务队列
        task_id = async_task(process_document_task, document.id)
        
        self.message_user(request, f"文档 '{document.title}' 已加入处理队列 (Task ID: {task_id})。请确保已启动 qcluster。", messages.SUCCESS)

    process_selected_documents.short_description = "处理选中的文档 (后台任务队列)"