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
        ('text', '文本'),
        ('pdf', 'PDF'),
        ('image', '图片'),
        ('video', '视频'),
    ]
    
    STATUS_CHOICES = [
        ('uploaded', '已上传'),
        ('processing', '处理中'),
        ('processed', '已处理'),
        ('analyzed', '已分析'),
        ('error', '处理错误'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to=document_upload_path)
    file_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    uploader = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    processed_data = models.JSONField(null=True, blank=True)
    file_size = models.BigIntegerField(default=0)  # 文件大小（字节）
    processing_start_time = models.DateTimeField(null=True, blank=True)
    processing_end_time = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """重写save方法，自动计算文件大小"""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-upload_time']