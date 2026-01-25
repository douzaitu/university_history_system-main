from django.db import models

class Entity(models.Model):
    ENTITY_TYPES = [
        ('person', '人物'),
        ('location', '地点'),
        ('event', '事件'),
        ('organization', '机构'),
        ('subject', '学科'),  # 新增学科类型
        # 移除了 'time' 类型，因为重庆大学的分类中没有时间类型
    ]
    
    name = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    description = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)  # 新增照片URL字段
    source_documents = models.ManyToManyField('documents.Document')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"

class Relationship(models.Model):
    RELATIONSHIP_TYPES = [
        ('belongs_to', '属于'),
        ('participated_in', '参与'),
        ('located_in', '位于'),
        ('happened_at', '发生于'),
        ('related_to', '相关于'),
        ('studied', '学习'),  # 新增：人物学习学科
        ('teaches', '教授'),  # 新增：人物教授学科
    ]
    
    source_entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='outgoing_relationships')
    target_entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='incoming_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    description = models.TextField(blank=True)
    confidence = models.FloatField(default=1.0)  # 关系置信度
    
    def __str__(self):
        return f"{self.source_entity} - {self.get_relationship_type_display()} - {self.target_entity}"