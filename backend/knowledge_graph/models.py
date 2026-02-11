from django.db import models

class Entity(models.Model):
    ENTITY_TYPES = [
        ('person', '人物'),
        ('location', '地点'),
        ('event', '事件'),
        ('organization', '机构'),
        ('subject', '学科'),  
    ]
    
    name = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    description = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)  # 新增照片URL字段
    source_documents = models.ManyToManyField('documents.Document', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"

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
    
    source_entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='outgoing_relationships')
    target_entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='incoming_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    
    def __str__(self):
        return f"{self.source_entity} - {self.relationship_type} - {self.target_entity}"