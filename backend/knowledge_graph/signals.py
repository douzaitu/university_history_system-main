from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from django_q.tasks import async_task
from .models import Entity, Relationship, CoreEntity, AuxiliaryEntity
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# 同时监听实体及其代理模型的保存信号
@receiver(post_save, sender=Entity)
@receiver(post_save, sender=CoreEntity)
@receiver(post_save, sender=AuxiliaryEntity)
def sync_entity_to_neo4j(sender, instance, created, **kwargs):
    """
    当 SQLite 中的 Entity 保存时，异步同步更新 Neo4j
    """
    # 使用 transaction.on_commit 确保事务提交后再执行任务，避免任务执行时数据还没提交
    transaction.on_commit(
        lambda: async_task(
            'knowledge_graph.tasks.sync_entity_task', 
            instance.id, 
            created,
            task_name=f'sync_entity_{instance.id}'
        )
    )

# 同时监听实体及其代理模型的删除信号
@receiver(post_delete, sender=Entity)
@receiver(post_delete, sender=CoreEntity)
@receiver(post_delete, sender=AuxiliaryEntity)
def delete_entity_from_neo4j(sender, instance, **kwargs):
    """
    当 SQLite 中的 Entity 删除时，异步从 Neo4j 删除
    """
    try:
        # 捕获需要的参数
        django_id = instance.id
        name = instance.name
        
        # 打印日志以确认信号触发
        print(f"收到 Entity 删除信号: ID={django_id}, Name={name}")
        logger.info(f"Received post_delete signal for Entity: {name} (ID: {django_id})")
        
        def run_deletion_task():
            async_task(
                'knowledge_graph.tasks.delete_entity_task', 
                django_id, 
                name,
                task_name=f'delete_entity_{django_id}'
            )

        # 使用 transaction.on_commit 确保事务提交后再执行任务
        transaction.on_commit(run_deletion_task)
                
    except Exception as e:
        logger.error(f"Error in delete_entity_from_neo4j signal: {e}")


@receiver(post_save, sender=Relationship)
def sync_relationship_to_neo4j(sender, instance, created, **kwargs):
    """
    当 SQLite 中的 Relationship 保存时，异步同步更新 Neo4j
    """
    transaction.on_commit(
        lambda: async_task(
            'knowledge_graph.tasks.sync_relationship_task',
            instance.id,
            created,
            task_name=f'sync_relationship_{instance.id}'
        )
    )

@receiver(post_delete, sender=Relationship)
def delete_relationship_from_neo4j(sender, instance, **kwargs):
    """
    当 SQLite 中的 Relationship 删除时，异步从 Neo4j 删除
    """
    django_id = instance.id
    
    # 尝试获取关联实体的名称用于匹配删除
    # 注意：如果关联实体也被删除，这里可能会有访问风险
    source_name = None
    target_name = None
    
    try:
        # 如果 Entity 还在还能查到
        source_name = instance.source_entity.name
    except Exception:
        pass
        
    try:
        target_name = instance.target_entity.name
    except Exception:
        pass
        
    rel_type = instance.relationship_type
    
    transaction.on_commit(
        lambda: async_task(
            'knowledge_graph.tasks.delete_relationship_task',
            django_id,
            source_name, 
            target_name, 
            rel_type,
            task_name=f'delete_relationship_{django_id}'
        )
    )

@receiver(post_delete, sender=Entity)
@receiver(post_delete, sender=CoreEntity)
@receiver(post_delete, sender=AuxiliaryEntity)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    当 Entity 被删除后，删除对应的图片文件
    """
    # 1. 删除通过 ImageField 上传的文件
    if instance.image:
        if os.path.isfile(instance.image.path):
            try:
                os.remove(instance.image.path)
                logger.info(f"Deleted image file for entity: {instance.name}")
            except Exception as e:
                logger.error(f"Error deleting image file: {e}")

    # 2. 删除 photo_url 指向的本地文件 (兼容旧数据)
    # 检查路径是否包含 teacher_photos (旧) 或 document_images (新)
    if instance.photo_url and ('teacher_photos' in instance.photo_url or 'document_images' in instance.photo_url):
        try:
            rel_path = instance.photo_url
            if rel_path.startswith('/media/'):
                rel_path = rel_path.replace('/media/', '', 1)
            elif rel_path.startswith('/'): # 处理不带 media 前缀但实际在 media 下的情况
                 rel_path = rel_path.lstrip('/')
            
            full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            
            if os.path.isfile(full_path):
                os.remove(full_path)
                logger.info(f"Deleted entity legacy photo: {full_path}")
        except Exception as e:
            logger.error(f"Error delete entity legacy photo: {e}")

@receiver(pre_save, sender=Entity)
@receiver(pre_save, sender=CoreEntity)
@receiver(pre_save, sender=AuxiliaryEntity)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    当 Entity 图片更新时，删除旧文件
    """
    if not instance.pk:
        return False

    try:
        old_obj = Entity.objects.get(pk=instance.pk)
        old_file = old_obj.image
    except Entity.DoesNotExist:
        return False

    new_file = instance.image
    
    # 如果新旧文件不同，且旧文件存在，则删除旧文件
    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
             try:
                os.remove(old_file.path)
                logger.info(f"Deleted old image file for entity: {instance.name}")
             except Exception as e:
                logger.error(f"Error deleting old image file: {e}")
