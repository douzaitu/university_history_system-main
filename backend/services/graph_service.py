from knowledge_graph.neo4j_db import Neo4jConnection

class Neo4jGraphService:
    """Neo4j图数据库服务"""
    
    @staticmethod
    def get_teacher_subgraph(teacher_name):
        """获取教师相关子图"""
        query = """
        MATCH (teacher:Entity {name: $teacher_name})-[r:RELATION]->(target:Entity)
        RETURN teacher.name as source, r.type as relation, target.name as target, 'outgoing' as direction
        UNION
        MATCH (source:Entity)-[r:RELATION]->(teacher:Entity {name: $teacher_name})
        RETURN source.name as source, r.type as relation, teacher.name as target, 'incoming' as direction
        """
        
        try:
            result = Neo4jConnection.query(query, {"teacher_name": teacher_name})
            
            if result is None:
                return None
                
            nodes = []
            edges = []
            node_set = set()
            
            # 添加中心节点（教师）
            nodes.append({
                'id': teacher_name,
                'label': teacher_name,
                'type': 'teacher',
                'size': 25
            })
            node_set.add(teacher_name)
            
            for record in result:
                source = record['source']
                target = record['target']
                relation = record['relation']
                direction = record['direction']
                
                # 添加源节点
                if source not in node_set:
                    nodes.append({
                        'id': source,
                        'label': source,
                        'type': 'entity',
                        'size': 15
                    })
                    node_set.add(source)
                
                # 添加目标节点
                if target not in node_set:
                    nodes.append({
                        'id': target,
                        'label': target,
                        'type': 'entity',
                        'size': 15
                    })
                    node_set.add(target)
                
                # 添加边
                edges.append({
                    'source': source,
                    'target': target,
                    'label': relation,
                    'direction': direction
                })
                
            return {
                'teacher': teacher_name,
                'nodes': nodes,
                'edges': edges
            }
        except Exception as e:
            print(f"Error in get_teacher_subgraph: {e}")
            return None

    @staticmethod
    def search_entities(query_text, limit=10):
        """在图谱中搜索实体"""
        query = "MATCH (n:Entity) WHERE n.name CONTAINS $query RETURN n.name as name LIMIT $limit"
        try:
            result = Neo4jConnection.query(query, {"query": query_text, "limit": limit})
            
            if result is None:
                return None
                
            return [record['name'] for record in result]
        except Exception as e:
            print(f"Error in search_entities: {e}")
            return None

# 全局服务实例
graph_service = Neo4jGraphService()