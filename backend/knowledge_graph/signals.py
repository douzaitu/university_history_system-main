from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Entity, Relationship
from .neo4j_db import Neo4jConnection

@receiver(post_save, sender=Entity)
def sync_entity_to_neo4j(sender, instance, created, **kwargs):
    """
    当 SQLite 中的 Entity 保存时，同步更新 Neo4j
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
            # 备用：如果还没有 django_id（旧数据），尝试按名称匹配
            query_fallback = """
            MATCH (n:Entity {name: $name})
            SET n.type = $type,
                n.description = $description,
                n.photo_url = $photo_url,
                n.django_id = $django_id
            """

        params = {
            "name": instance.name,
            "type": instance.entity_type,
            "description": instance.description or "",
            "photo_url": instance.photo_url or "",
            "django_id": instance.id
        }
        
        # 尝试执行
        Neo4jConnection.query(query, params)
        
    except Exception as e:
        print(f"Error syncing Entity to Neo4j: {e}")

@receiver(post_delete, sender=Entity)
def delete_entity_from_neo4j(sender, instance, **kwargs):
    """
    当 SQLite 中的 Entity 删除时，同步删除 Neo4j 节点
    """
    try:
        query = "MATCH (n:Entity {django_id: $django_id}) DETACH DELETE n"
        Neo4jConnection.query(query, {"django_id": instance.id})
        
        # 备用：按名称清理
        query_fallback = "MATCH (n:Entity {name: $name}) DETACH DELETE n"
        Neo4jConnection.query(query_fallback, {"name": instance.name})
    except Exception as e:
        print(f"Error deleting Entity from Neo4j: {e}")

@receiver(post_save, sender=Relationship)
def sync_relationship_to_neo4j(sender, instance, created, **kwargs):
    """
    当 SQLite 中的 Relationship 保存时，同步更新 Neo4j
    """
    try:
        # 无论创建还是更新，我们都先确保两个节点存在，然后创建/更新关系
        # 注意：这里简化处理，直接 MERGE 关系。如果修改了关系类型，可能需要先删除旧关系。
        # Django 的 Relationship 模型如果修改了 type，其实是同一条记录。
        # 为了简单起见，我们假设关系创建后主要修改属性。
        
        query = """
        MATCH (source:Entity {name: $source_name})
        MATCH (target:Entity {name: $target_name})
        MERGE (source)-[r:RELATION {django_id: $django_id}]->(target)
        SET r.type = $type,
            r.description = $description,
            r.confidence = $confidence
        """
        
        params = {
            "source_name": instance.source_entity.name,
            "target_name": instance.target_entity.name,
            "type": instance.relationship_type,
            "description": instance.description or "",
            "confidence": instance.confidence,
            "django_id": instance.id
        }
        
        Neo4jConnection.query(query, params)
        
    except Exception as e:
        print(f"Error syncing Relationship to Neo4j: {e}")

@receiver(post_delete, sender=Relationship)
def delete_relationship_from_neo4j(sender, instance, **kwargs):
    """
    删除关系
    """
    try:
        query = "MATCH ()-[r:RELATION {django_id: $django_id}]->() DELETE r"
        Neo4jConnection.query(query, {"django_id": instance.id})
    except Exception as e:
        print(f"Error deleting Relationship from Neo4j: {e}")
