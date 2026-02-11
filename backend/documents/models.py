from django.db import models
from users.models import CustomUser
import os
import uuid

def document_upload_path(instance, filename):
    """生成文件上传路径"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"documents/{filename}"

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel表格'),
        ('word', 'Word文档'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '---'), # 初始状态为空白
        ('processing', '处理中'),
        ('processed', '已处理'),
        ('error', '处理错误'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to=document_upload_path)
    file_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    uploader = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_data = models.JSONField(null=True, blank=True)
    processing_start_time = models.DateTimeField(null=True, blank=True)
    processing_end_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-upload_time']