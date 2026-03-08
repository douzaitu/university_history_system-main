from django.db import models

class Entity(models.Model):
    ENTITY_TYPES = [
        ('person', '人物'),
        ('location', '地点'),
        ('event', '事件'),
        ('organization', '机构'),
        ('subject', '学科'),  
    ]
    
    name = models.CharField(max_length=100, verbose_name="名称")
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES, verbose_name="实体类型")
    description = models.TextField(blank=True, verbose_name="描述/简介")
    
    # 新增字段：用于精确控制前端展示
    # 职务字段已废弃，统一合并到 subtype
    subtype = models.CharField(max_length=100, blank=True, null=True, verbose_name="细分类型/人物类别", help_text="例如：教职工、学生、杰出校友")

    # 也可以手动上传本地图片
    image = models.ImageField(upload_to='entity_photos/', blank=True, null=True, verbose_name="上传照片")
    # 旧字段保留，用于兼容网络图片或自动抓取的路径
    photo_url = models.URLField(blank=True, verbose_name="网络照片URL")
    
    # 新增：是否为核心实体（用于前端列表展示筛选）
    # True: 在对应类型的列表页显示（如“人物库”）
    # False: 仅作为关系节点存在（如“毕业院校”），不显示在列表页
    is_primary = models.BooleanField(default=False, verbose_name="是否核心实体")
    
    source_documents = models.ManyToManyField('documents.Document', blank=True, verbose_name="来源文档")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"
        
    @property
    def photo(self):
        """返回照片的最佳访问地址（优先本地图片，其次网络图片）"""
        if self.image:
            return self.image.url
        return self.photo_url
    
    class Meta:
        verbose_name = "所有实体"
        verbose_name_plural = verbose_name

# 代理模型：核心实体（用于Admin后台分类显示）
class CoreEntity(Entity):
    class Meta:
        proxy = True
        verbose_name = "核心实体(前端展示)"
        verbose_name_plural = "核心实体(前端展示)"

# 代理模型：辅助实体（用于Admin后台分类显示）
class AuxiliaryEntity(Entity):
    class Meta:
        proxy = True
        verbose_name = "辅助实体(仅图谱)"
        verbose_name_plural = "辅助实体(仅图谱)"

class Relationship(models.Model):
    RELATIONSHIP_TYPES = [
        ('属于', '属于'),
        ('拥有', '拥有'),
        ('研究', '研究'),
        ('主讲', '主讲'),
        ('毕业于', '毕业于'), 
        ('获得', '获得'),
        ('负责', '负责'),
        ('相关于', '相关于'), # 保留一个通用类型
    ]
    
    source_entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='outgoing_relationships', verbose_name="源实体")
    target_entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='incoming_relationships', verbose_name="目标实体")
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES, verbose_name="关系类型")
    
    def __str__(self):
        return f"{self.source_entity} - {self.relationship_type} - {self.target_entity}"

    class Meta:
        verbose_name = "关系"
        verbose_name_plural = verbose_name