from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('researcher', '研究人员'),
        ('viewer', '普通用户'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username