import os
import django
import time

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from knowledge_graph.models import Entity, Relationship
from knowledge_graph.neo4j_db import Neo4jConnection
from django_q.tasks import async_task
from django_q.models import OrmQ, Task

def rebuild_graph():
    print("=== 开始重建知识图谱 ===")
    
    # 1. 清空 Neo4j 数据库
    print("1.正在清空 Neo4j 数据库...")
    try:
        Neo4jConnection.query("MATCH (n) DETACH DELETE n")
        print("  - Neo4j 已清空")
    except Exception as e:
        print(f"  - 清空 Neo4j 失败: {e}")
        return

    # 2. 清空任务队列 (防止积压的旧任务干扰)
    print("2.正在清空 Django Q 任务队列...")
    OrmQ.objects.all().delete()
    Task.objects.all().delete()
    print("  - 任务队列已清空")

    # 3. 重新发布实体同步任务
    entities = Entity.objects.all()
    total_entities = entities.count()
    print(f"3.正在重新发布 {total_entities} 个实体同步任务...")
    
    for i, entity in enumerate(entities):
        async_task('knowledge_graph.tasks.sync_entity_task', entity.id, False, task_name=f'sync_entity_{entity.id}')
        if (i + 1) % 100 == 0:
            print(f"  - 已发布 {i + 1}/{total_entities} 个实体任务")
    
    # 4. 重新发布关系同步任务
    relationships = Relationship.objects.all()
    total_rels = relationships.count()
    print(f"4.正在重新发布 {total_rels} 个关系同步任务...")
    
    for i, rel in enumerate(relationships):
        async_task('knowledge_graph.tasks.sync_relationship_task', rel.id, False, task_name=f'sync_relationship_{rel.id}')
        if (i + 1) % 100 == 0:
            print(f"  - 已发布 {i + 1}/{total_rels} 个关系任务")

    print("\n=== 重建任务发布完成 ===")
    print("请确保 'python manage.py qcluster' 正在运行以处理这些任务。")
    print("您可以观察 qcluster 的日志，等待所有任务执行完毕。")

if __name__ == "__main__":
    rebuild_graph()
