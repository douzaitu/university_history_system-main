from django.contrib import admin
from .models import Entity, Relationship, CoreEntity, AuxiliaryEntity

class Neo4jSyncAdminMixin:
    """
    Mixin 用于确保 Django Admin 的批量删除操作能触发 post_delete 信号，
    从而同步删除 Neo4j 中的数据。
    """
    def delete_queryset(self, request, queryset):
        # 逐个删除对象以触发信号
        for obj in queryset:
            obj.delete()

@admin.register(Entity)
class EntityAdmin(Neo4jSyncAdminMixin, admin.ModelAdmin):
    # 在列表页显示图片是否已上传，方便管理
    list_display = ['name', 'entity_type', 'subtype', 'is_primary', 'has_image', 'created_at']
    list_filter = ['is_primary', 'entity_type', 'subtype']
    search_fields = ['name', 'description'] # 必须有这一行，autocomplete_fields 才能生效
    ordering = ['-created_at'] # 搜索结果按创建时间排序
    
    # 允许在列表页直接编辑核心实体状态
    list_editable = ['is_primary']
    
    # 详情页字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'entity_type', 'description', 'is_primary')
        }),
        ('类型与分类', {
            'fields': ('subtype',),
            'description': '如果不填写，前端会自动从简介中提取（但可能不准确）。填写后将优先显示此处的内容。'
        }),
        ('图片信息', {
            'fields': ('image', 'photo_url'),
            'classes': ('collapse',),
        }),
        ('关联文档', {
            'fields': ('source_documents',),
            'classes': ('collapse',),
        }),
    )

    def has_image(self, obj):
        return bool(obj.image or obj.photo_url)
    has_image.boolean = True
    has_image.short_description = "有照片"

# 核心实体的管理界面
@admin.register(CoreEntity)
class CoreEntityAdmin(Neo4jSyncAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'entity_type', 'subtype', 'description', 'has_image', 'created_at']
    list_filter = ['entity_type', 'subtype']
    search_fields = ['name', 'description']
    
    # 详情页字段分组 - 保持与主实体一致的编辑体验
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'entity_type', 'description', 'is_primary')
        }),
        ('类型与分类', {
            'fields': ('subtype',),
            'description': '如果不填写，前端会自动从简介中提取（但可能不准确）。填写后将优先显示此处的内容。'
        }),
        ('图片信息', {
            'fields': ('image', 'photo_url'),
            'classes': ('collapse',),
        }),
        ('关联文档', {
            'fields': ('source_documents',),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_primary=True)
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['is_primary'] = True
        return initial

    def has_image(self, obj):
        return bool(obj.image or obj.photo_url)
    has_image.boolean = True
    has_image.short_description = "有照片"

# 辅助实体的管理界面
@admin.register(AuxiliaryEntity)
class AuxiliaryEntityAdmin(Neo4jSyncAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'entity_type', 'subtype', 'description', 'has_image', 'created_at']
    list_filter = ['entity_type', 'subtype']
    search_fields = ['name', 'description']
    
    # 详情页字段分组 - 保持与主实体一致的编辑体验
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'entity_type', 'description', 'is_primary')
        }),
        ('类型与分类', {
            'fields': ('subtype',),
            'description': '如果不填写，前端会自动从简介中提取（但可能不准确）。填写后将优先显示此处的内容。'
        }),
        ('图片信息', {
            'fields': ('image', 'photo_url'),
            'classes': ('collapse',),
        }),
        ('关联文档', {
            'fields': ('source_documents',),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_primary=False)
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['is_primary'] = False
        return initial

    def has_image(self, obj):
        return bool(obj.image or obj.photo_url)
    has_image.boolean = True
    has_image.short_description = "有照片"

@admin.register(Relationship)
class RelationshipAdmin(Neo4jSyncAdminMixin, admin.ModelAdmin):
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