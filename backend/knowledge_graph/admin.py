from django.contrib import admin
from .models import Entity, Relationship

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'entity_type', 'created_at']
    list_filter = ['entity_type']
    search_fields = ['name', 'description'] # 必须有这一行，autocomplete_fields 才能生效
    ordering = ['name'] # 搜索结果按名称排序

@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ['source_entity', 'relationship_type', 'target_entity']
    list_filter = ['relationship_type']
    
    # 列表页的搜索框，支持搜两端实体的名字
    search_fields = ['source_entity__name', 'target_entity__name']
    
    # 编辑页/新建页的搜索功能
    # 这会将默认的下拉框变成了带有搜索功能的 Select2 组件
    # 用户可以在输入框中输入名字来查找实体
    autocomplete_fields = ['source_entity', 'target_entity']
    
    list_select_related = ('source_entity', 'target_entity')
    list_per_page = 20