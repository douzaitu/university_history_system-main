from django.contrib import admin
from .models import Entity, Relationship

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'entity_type', 'created_at']
    list_filter = ['entity_type']
    search_fields = ['name', 'description']

@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ['source_entity', 'relationship_type', 'target_entity', 'confidence']
    list_filter = ['relationship_type']