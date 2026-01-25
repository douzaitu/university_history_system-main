from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'uploader', 'upload_time', 'status']
    list_filter = ['file_type', 'status', 'upload_time']
    search_fields = ['title', 'content']