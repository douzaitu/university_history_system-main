from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser

# 隐藏不需要的 Group 模块
admin.site.unregister(Group)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    fieldsets = UserAdmin.fieldsets + (
        ('角色信息', {'fields': ('role',)}),
    )