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
        subtype = entity.subtype or ""
        
        # 使用新属性获取图片链接 (兼容本地上传和网络链接)
        photo_url = entity.photo if entity.photo else ""
        
        is_primary = entity.is_primary  # 获取新增是否核心字段
        
        # 构建 Cypher 查询
        # 使用 MERGE 更加稳健，既能处理新建也能处理更新
        # 这里的逻辑稍微优化一下：总是以 django_id 为主键来 MERGE
        query = """
        MERGE (n:Entity {django_id: $django_id})
        SET n.name = $name, 
            n.type = $type, 
            n.description = $description,
            n.subtype = $subtype,
            n.photo_url = $photo_url,
            n.is_primary = $is_primary
        """
            
        params = {
            "django_id": django_id,
            "name": name,
            "type": entity_type,
            "description": description,
            "subtype": subtype,
            "photo_url": photo_url,
            "is_primary": is_primary
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
        logger.info(f"Starting delete_entity_task for ID: {django_id}, Name: {name}")
        
        # 1. 尝试通过 ID (Integer) 删除
        query = "MATCH (n:Entity {django_id: $django_id}) DETACH DELETE n"
        Neo4jConnection.query(query, {"django_id": django_id})
        
        # 2. 尝试通过 ID (String) 删除 - 防止类型不匹配
        # 注意：如果 ID 是整数，转为字符串再试一次
        query_str_id = "MATCH (n:Entity {django_id: $django_id_str}) DETACH DELETE n"
        Neo4jConnection.query(query_str_id, {"django_id_str": str(django_id)})
        
        # 3. 备用：按名称清理 (防止旧数据没有 django_id)
        if name:
            query_fallback = "MATCH (n:Entity {name: $name}) WHERE n.django_id IS NULL DETACH DELETE n"
            Neo4jConnection.query(query_fallback, {"name": name})
            
        logger.info(f"Async deleted Entity from Neo4j: {name} (ID: {django_id})")
    except Exception as e:
        logger.error(f"Error deleting Entity from Neo4j: {e}")
        print(f"Error deleting Entity from Neo4j: {e}") # 打印到控制台以便调试
        raise e

def sync_relationship_task(relationship_id, created=False):
    """
    异步任务：同步关系到 Neo4j
    """
    try:
        rel = Relationship.objects.select_related('source_entity', 'target_entity').get(id=relationship_id)
        
        rel_django_id = rel.id
        rel_type = rel.relationship_type
        
        # 获取源实体信息
        source = rel.source_entity
        source_django_id = source.id
        source_name = source.name
        source_type = source.entity_type
        
        # 获取目标实体信息
        target = rel.target_entity
        target_django_id = target.id
        target_name = target.name
        target_type = target.entity_type
        
        # 构建更健壮的 Cypher 查询
        # 1. 确保源实体存在 (MERGE by django_id)
        # 2. 确保目标实体存在 (MERGE by django_id)
        # 3. 创建/更新关系 (MERGE by django_id)
        
        query = """
        MERGE (source:Entity {django_id: $source_id})
        ON CREATE SET source.name = $source_name, source.type = $source_type
        
        MERGE (target:Entity {django_id: $target_id})
        ON CREATE SET target.name = $target_name, target.type = $target_type
        
        MERGE (source)-[r:RELATION {django_id: $rel_id}]->(target)
        SET r.type = $rel_type
        """
        
        params = {
            "source_id": source_django_id,
            "source_name": source_name,
            "source_type": source_type,
            "target_id": target_django_id,
            "target_name": target_name,
            "target_type": target_type,
            "rel_id": rel_django_id,
            "rel_type": rel_type
        }
        
        Neo4jConnection.query(query, params)
        logger.info(f"Async synced relationship to Neo4j: {source_name} - {rel_type} -> {target_name} (Rel ID: {rel_django_id})")
        
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
            WHERE r.type = $type AND r.django_id IS NULL
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
