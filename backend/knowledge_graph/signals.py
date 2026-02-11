from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Entity, Relationship
from .neo4j_db import Neo4jConnection
import os
from django.conf import settings

def _sync_entity_logic(django_id, name, entity_type, description, photo_url, created):
    """
    Neo4j 同步的具体逻辑，用于在事务提交后执行
    """
    try:
        if created:
            # 创建节点
            query = """
            MERGE (n:Entity {name: $name})
            SET n.type = $type, 
                n.description = $description,
                n.photo_url = $photo_url,
                n.django_id = $django_id
            """
        else:
            # 更新节点
            query = """
            MATCH (n:Entity {django_id: $django_id})
            SET n.name = $name,
                n.type = $type,
                n.description = $description,
                n.photo_url = $photo_url
            """
        
        params = {
            "name": name,
            "type": entity_type,
            "description": description or "",
            "photo_url": photo_url or "",
            "django_id": django_id
        }
        
        Neo4jConnection.query(query, params)
        print(f"Synced Entity to Neo4j: {name} (ID: {django_id})")
        
    except Exception as e:
        print(f"Error syncing Entity to Neo4j: {e}")

@receiver(post_save, sender=Entity)
def sync_entity_to_neo4j(sender, instance, created, **kwargs):
    """
    当 SQLite 中的 Entity 保存时，注册事务提交后的回调以同步更新 Neo4j
    """
    # 捕获当前需要的参数值（闭包）
    django_id = instance.id
    name = instance.name
    entity_type = instance.entity_type
    description = instance.description
    photo_url = instance.photo_url
    
    transaction.on_commit(
        lambda: _sync_entity_logic(django_id, name, entity_type, description, photo_url, created)
    )

def _delete_entity_logic(django_id, name):
    try:
        query = "MATCH (n:Entity {django_id: $django_id}) DETACH DELETE n"
        Neo4jConnection.query(query, {"django_id": django_id})
        
        # 备用：按名称清理
        query_fallback = "MATCH (n:Entity {name: $name}) DETACH DELETE n"
        Neo4jConnection.query(query_fallback, {"name": name})
        print(f"Deleted Entity from Neo4j: {name} (ID: {django_id})")
    except Exception as e:
        print(f"Error deleting Entity from Neo4j: {e}")

@receiver(post_delete, sender=Entity)
def delete_entity_from_neo4j(sender, instance, **kwargs):
    """
    当 SQLite 中的 Entity 删除时
    """
    # Neo4j 删除逻辑放入 on_commit
    transaction.on_commit(
        lambda: _delete_entity_logic(instance.id, instance.name)
    )

    # 本地文件删除逻辑主要涉及文件系统，通常不需要严格的数据库事务一致性（或者说很难回滚），
    # 但为了逻辑统一，也可以放在之后，不过这里保持直接执行也无大碍，
    # 稍微优化一下路径处理逻辑
    if instance.photo_url and 'teacher_photos' in instance.photo_url:
        try:
            rel_path = instance.photo_url
            if rel_path.startswith('/media/'):
                rel_path = rel_path.replace('/media/', '', 1)
                
            full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            
            if os.path.isfile(full_path):
                os.remove(full_path)
                print(f"Deleted teacher photo: {full_path}")
        except Exception as e:
            print(f"Error delete teacher photo: {e}")

def _sync_relationship_logic(django_id, source_name, target_name, rel_type):
    try:
        # 1. 删除旧关系
        delete_query = "MATCH ()-[r:RELATION {django_id: $django_id}]->() DELETE r"
        Neo4jConnection.query(delete_query, {"django_id": django_id})
        
        # 2. 重新创建关系
        create_query = """
        MATCH (source:Entity {name: $source_name})
        MATCH (target:Entity {name: $target_name})
        MERGE (source)-[r:RELATION {django_id: $django_id}]->(target)
        SET r.type = $type
        """
        
        params = {
            "source_name": source_name,
            "target_name": target_name,
            "type": rel_type,
            "django_id": django_id
        }
        
        Neo4jConnection.query(create_query, params)
        print(f"Synced relationship to Neo4j: {source_name} - {rel_type} -> {target_name}")
        
    except Exception as e:
        print(f"Error syncing Relationship to Neo4j: {e}")

@receiver(post_save, sender=Relationship)
def sync_relationship_to_neo4j(sender, instance, created, **kwargs):
    """
    当 SQLite 中的 Relationship 保存时，同步更新 Neo4j
    """
    django_id = instance.id
    source_name = instance.source_entity.name
    target_name = instance.target_entity.name
    rel_type = instance.relationship_type
    
    transaction.on_commit(
        lambda: _sync_relationship_logic(django_id, source_name, target_name, rel_type)
    )

def _delete_relationship_logic(django_id, source_name, target_name, rel_type):
    try:
        # 1. 优先尝试通过精准的 django_id 删除
        query_id = "MATCH ()-[r:RELATION {django_id: $django_id}]->() DELETE r"
        Neo4jConnection.query(query_id, {"django_id": django_id})
        
        # 2. 兜底方案：通过内容匹配删除 (如果老的id没同步过去，这个能救命)
        if source_name and target_name:
            query_content = """
            MATCH (s:Entity {name: $source_name})-[r:RELATION]->(t:Entity {name: $target_name})
            WHERE r.type = $type
            DELETE r
            """
            Neo4jConnection.query(query_content, {
                "source_name": source_name,
                "target_name": target_name,
                "type": rel_type
            })
            
        print(f"Deleted Relationship from Neo4j: {source_name} - {rel_type} -> {target_name} (ID: {django_id})")
    except Exception as e:
        print(f"Error deleting Relationship from Neo4j: {e}")

@receiver(post_delete, sender=Relationship)
def delete_relationship_from_neo4j(sender, instance, **kwargs):
    """
    删除关系
    """
    d_id = instance.id
    try:
        s_name = instance.source_entity.name
        t_name = instance.target_entity.name
    except Exception:
        s_name = None
        t_name = None
        
    r_type = instance.relationship_type

    transaction.on_commit(
        lambda: _delete_relationship_logic(d_id, s_name, t_name, r_type)
    )
