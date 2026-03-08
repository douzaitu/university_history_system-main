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
    
    # 新增：文档内容分类（决定提取的主要实体类型）
    CONTENT_CATEGORY_CHOICES = [
        ('general', '通用文档'), # 默认，不特殊标记任何实体
        ('person', '人物档案'),
        ('event', '校史事件'),
        ('organization', '机构介绍'),
        ('location', '校园地图'),
        ('subject', '学科建设'),
    ]

    STATUS_CHOICES = [
        ('pending', '---'), # 初始状态为空白
        ('processing', '处理中'),
        ('processed', '已处理'),
        ('error', '处理错误'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="文档标题")
    content = models.TextField(blank=True, verbose_name="文档内容")
    file = models.FileField(upload_to=document_upload_path, verbose_name="文件")
    file_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES, verbose_name="文件类型")
    # 新增字段：文档内容分类
    content_category = models.CharField(max_length=20, choices=CONTENT_CATEGORY_CHOICES, default='general', verbose_name="内容分类")
    
    uploader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="上传者")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="处理状态")
    processed_data = models.JSONField(null=True, blank=True, verbose_name="处理结果数据")
    processing_start_time = models.DateTimeField(null=True, blank=True, verbose_name="处理开始时间")
    processing_end_time = models.DateTimeField(null=True, blank=True, verbose_name="处理结束时间")
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-upload_time']
        verbose_name = "文档"
        verbose_name_plural = verbose_name