from .models import Entity, Relationship
from .neo4j_db import Neo4jConnection
import logging

logger = logging.getLogger(__name__)

def sync_entity_task(entity_id, created=False):
    """
    异步任务：同步实体到 Neo4j
    """
    try:
        # 重新从数据库获取最新状态，确保数据一致性
        entity = Entity.objects.get(id=entity_id)
        
        django_id = entity.id
        name = entity.name
        entity_type = entity.entity_type
        description = entity.description or ""
        photo_url = entity.photo_url or ""
        
        # 构建 Cypher 查询
        # 使用 MERGE 更加稳健，既能处理新建也能处理更新
        # 这里的逻辑稍微优化一下：总是以 django_id 为主键来 MERGE
        query = """
        MERGE (n:Entity {django_id: $django_id})
        SET n.name = $name, 
            n.type = $type, 
            n.description = $description,
            n.photo_url = $photo_url
        """
            
        params = {
            "django_id": django_id,
            "name": name,
            "type": entity_type,
            "description": description,
            "photo_url": photo_url
        }
        
        Neo4jConnection.query(query, params)
        logger.info(f"Async synced Entity to Neo4j: {name} (ID: {django_id})")
        
    except Entity.DoesNotExist:
        logger.warning(f"Entity {entity_id} not found during sync task. It might have been deleted.")
    except Exception as e:
        logger.error(f"Error syncing Entity to Neo4j: {e}")
        # 抛出异常以便 Django Q 重试（如果配置了重试）
        raise e

def delete_entity_task(django_id, name):
    """
    异步任务：从 Neo4j 删除实体
    """
    try:
        # 优先通过 ID 删除
        query = "MATCH (n:Entity {django_id: $django_id}) DETACH DELETE n"
        Neo4jConnection.query(query, {"django_id": django_id})
        
        # 备用：按名称清理 (防止旧数据没有 django_id)
        if name:
            query_fallback = "MATCH (n:Entity {name: $name}) WHERE not exists(n.django_id) DETACH DELETE n"
            Neo4jConnection.query(query_fallback, {"name": name})
            
        logger.info(f"Async deleted Entity from Neo4j: {name} (ID: {django_id})")
    except Exception as e:
        logger.error(f"Error deleting Entity from Neo4j: {e}")
        raise e

def sync_relationship_task(relationship_id, created=False):
    """
    异步任务：同步关系到 Neo4j
    """
    try:
        rel = Relationship.objects.select_related('source_entity', 'target_entity').get(id=relationship_id)
        
        django_id = rel.id
        source_name = rel.source_entity.name
        target_name = rel.target_entity.name
        rel_type = rel.relationship_type
        
        # 1. 确保两端节点存在 (虽然通常由 Entity 同步保证，但为了鲁棒性，这里可以再 MERGE 一次，或者假设它们存在)
        # 这里为了简化，我们假设 Entity 已经同步了。如果 Entity 还没同步，Match 可能会失败。
        # 更稳健的做法是 MERGE 节点。但这里我们主要关注关系。
        
        # 2. 删除旧的同 ID 关系 (如果是更新操作)
        delete_query = "MATCH ()-[r:RELATION {django_id: $django_id}]->() DELETE r"
        Neo4jConnection.query(delete_query, {"django_id": django_id})
        
        # 3. 创建新关系
        # 注意：这里假设节点已经通过 name 或者 django_id 存在了。
        # 之前的逻辑是用 name 匹配的。为了兼容旧数据，继续沿用 name 匹配，但也尝试匹配 django_id
        
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
        logger.info(f"Async synced relationship to Neo4j: {source_name} - {rel_type} -> {target_name}")
        
    except Relationship.DoesNotExist:
        logger.warning(f"Relationship {relationship_id} not found during sync task.")
    except Exception as e:
        logger.error(f"Error syncing Relationship to Neo4j: {e}")
        raise e

def delete_relationship_task(django_id, source_name, target_name, rel_type):
    """
    异步任务：从 Neo4j 删除关系
    """
    try:
        # 1. 优先尝试通过精准的 django_id 删除
        query_id = "MATCH ()-[r:RELATION {django_id: $django_id}]->() DELETE r"
        Neo4jConnection.query(query_id, {"django_id": django_id})
        
        # 2. 兜底方案：通过内容匹配删除
        if source_name and target_name:
            query_content = """
            MATCH (s:Entity {name: $source_name})-[r:RELATION]->(t:Entity {name: $target_name})
            WHERE r.type = $type AND not exists(r.django_id)
            DELETE r
            """
            Neo4jConnection.query(query_content, {
                "source_name": source_name,
                "target_name": target_name,
                "type": rel_type
            })
            
        logger.info(f"Async deleted Relationship from Neo4j: {source_name} - {rel_type} -> {target_name} (ID: {django_id})")
    except Exception as e:
        logger.error(f"Error deleting Relationship from Neo4j: {e}")
        raise e
