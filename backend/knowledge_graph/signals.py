from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django_q.tasks import async_task
from .models import Entity, Relationship
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Entity)
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

@receiver(post_delete, sender=Entity)
def delete_entity_from_neo4j(sender, instance, **kwargs):
    """
    当 SQLite 中的 Entity 删除时，异步从 Neo4j 删除
    """
    # 捕获需要的参数
    django_id = instance.id
    name = instance.name
    
    transaction.on_commit(
        lambda: async_task(
            'knowledge_graph.tasks.delete_entity_task', 
            django_id, 
            name,
            task_name=f'delete_entity_{django_id}'
        )
    )

    # 简单的本地文件清理逻辑保留在这里
    if instance.photo_url and 'teacher_photos' in instance.photo_url:
        try:
            rel_path = instance.photo_url
            if rel_path.startswith('/media/'):
                rel_path = rel_path.replace('/media/', '', 1)
                
            full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            
            if os.path.isfile(full_path):
                os.remove(full_path)
                logger.info(f"Deleted teacher photo: {full_path}")
        except Exception as e:
            logger.error(f"Error delete teacher photo: {e}")

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
