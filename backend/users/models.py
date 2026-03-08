from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('researcher', '研究人员'),
        ('viewer', '普通用户'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer', verbose_name="角色")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name