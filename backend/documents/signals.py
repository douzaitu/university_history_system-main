import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Document

@receiver(post_delete, sender=Document)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    当删除 Document 记录时，自动从硬盘删除对应的文件
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            try:
                os.remove(instance.file.path)
                print(f"File deleted: {instance.file.path}")
            except Exception as e:
                print(f"Error deleting file: {e}")
