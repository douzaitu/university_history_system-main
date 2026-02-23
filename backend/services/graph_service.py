from knowledge_graph.neo4j_db import Neo4jConnection
import logging

logger = logging.getLogger(__name__)

class Neo4jGraphService:
    """
    Neo4j图数据库服务
    """
    
    @staticmethod
    def _to_str_id(val):
        """将ID转换为字符串，以适应前端可视化库的要求"""
        if val is None:
            return None
        return str(val)

    @staticmethod
    def get_entity_subgraph(entity_name, limit=50):
        """
        获取实体相关子图 (1-hop)
        :param entity_name: 实体名称
        :param limit: 限制返回的邻居节点数量
        """
        query = """
        MATCH (center:Entity {name: $name})
        
        // 获取出边，携带目标节点信息
        OPTIONAL MATCH (center)-[r1]->(target:Entity)
        WITH center, collect({
            source: center.name, 
            target: target.name, 
            source_id: center.django_id, 
            target_id: target.django_id,
            relation: r1.type, 
            target_type: target.type
        })[..$limit] as outgoing
        
        // 获取入边，携带源节点信息
        OPTIONAL MATCH (source:Entity)-[r2]->(center)
        WITH center, outgoing, collect({
            source: source.name, 
            target: center.name, 
            source_id: source.django_id,
            target_id: center.django_id,
            relation: r2.type, 
            source_type: source.type
        })[..$limit] as incoming
        
        RETURN center.name as name, center.type as type, center.django_id as django_id, outgoing, incoming
        """
        
        try:
            result = Neo4jConnection.query(query, {"name": entity_name, "limit": limit})
            
            if not result:
                return None
            
            record = result[0]
            center_name = record['name']
            center_type = record['type']
            center_id = record['django_id']
            
            if not center_name:
                return None
                
            nodes = {}
            edges = []
            
            # 添加中心节点
            c_id = Neo4jGraphService._to_str_id(center_id) or center_name
            nodes[center_name] = {
                'id': c_id, 
                'label': center_name,
                'type': center_type,
                'size': 25,
                'is_center': True
            }
            
            # 处理出边
            for item in record['outgoing']:
                if not item or item['target'] is None: continue
                target_name = item['target']
                target_id = item['target_id']
                t_id = Neo4jGraphService._to_str_id(target_id) or target_name
                
                if target_name not in nodes:
                    nodes[target_name] = {
                        'id': t_id,
                        'label': target_name, 
                        'type': item['target_type'], 
                        'size': 15
                    }
                
                edges.append({
                    'source': nodes[center_name]['id'],
                    'target': nodes[target_name]['id'],
                    'label': item['relation'],
                    'description': '' 
                })

            # 处理入边
            for item in record['incoming']:
                if not item or item['source'] is None: continue
                source_name = item['source']
                source_id = item['source_id']
                s_id = Neo4jGraphService._to_str_id(source_id) or source_name
                
                if source_name not in nodes:
                    nodes[source_name] = {
                        'id': s_id,
                        'label': source_name, 
                        'type': item['source_type'], 
                        'size': 15
                    }
                
                edges.append({
                    'source': nodes[source_name]['id'],
                    'target': nodes[center_name]['id'],
                    'label': item['relation'],
                    'description': ''
                })
                
            return {
                'center': center_name,
                'nodes': list(nodes.values()),
                'edges': edges
            }
        except Exception as e:
            logger.error(f"Error in get_entity_subgraph: {e}")
            return None

    @staticmethod
    def get_teacher_subgraph(teacher_name):
        """兼容旧接口"""
        return Neo4jGraphService.get_entity_subgraph(teacher_name)

    @staticmethod
    def search_entities(query_text, limit=10):
        """在图谱中搜索实体"""
        query = """
        MATCH (n:Entity) 
        WHERE toLower(n.name) CONTAINS toLower($query) 
        RETURN n.name as name, n.type as type, n.django_id as id
        LIMIT $limit
        """
        try:
            result = Neo4jConnection.query(query, {"query": query_text, "limit": limit})
            
            if result is None:
                return []
            
            entities = []
            for r in result:
                entities.append({
                    'id': Neo4jGraphService._to_str_id(r['id']), 
                    'name': r['name'],
                    'type': r['type']
                })
            return entities
        except Exception as e:
            logger.error(f"Error in search_entities: {e}")
            return []

    @staticmethod
    def get_graph_overview(limit=50):
        """获取图谱概览"""
        query_simplified = """
        MATCH (n:Entity)
        WITH n, rand() as r
        ORDER BY r 
        LIMIT $node_limit
        
        OPTIONAL MATCH (n)-[r]->(m:Entity)
        RETURN n.name as source_name, n.type as source_type, n.django_id as source_id,
               r.type as rel_type,
               m.name as target_name, m.type as target_type, m.django_id as target_id
        LIMIT $rel_limit
        """
        
        params = {"node_limit": limit, "rel_limit": limit * 2}
        try:
            result = Neo4jConnection.query(query_simplified, params)
            if not result:
                return {'nodes': [], 'edges': []}
                
            nodes = {}
            edges = []
            
            for row in result:
                s_name = row['source_name']
                s_id = row['source_id']
                t_name = row['target_name']
                t_id = row['target_id']
                
                final_s_id = Neo4jGraphService._to_str_id(s_id) or s_name
                
                # 添加源节点
                if s_name and s_name not in nodes:
                    nodes[s_name] = {
                        'id': final_s_id, 
                        'label': s_name, 
                        'type': row['source_type'], 
                        'size': 10 + (2 if row['rel_type'] else 0)
                    }
                
                # 添加目标节点和边
                if t_name and row['rel_type']: 
                    final_t_id = Neo4jGraphService._to_str_id(t_id) or t_name
                    
                    if t_name not in nodes:
                         nodes[t_name] = {
                             'id': final_t_id, 
                             'label': t_name, 
                             'type': row['target_type'], 
                             'size': 10
                         }
                    
                    edges.append({
                        'source': nodes[s_name]['id'],
                        'target': nodes[t_name]['id'],
                        'label': row['rel_type']
                    })
            
            return {
                'nodes': list(nodes.values()),
                'edges': edges
            }
        except Exception as e:
            logger.error(f"Error in get_graph_overview: {e}")
            return {'nodes': [], 'edges': []}

    @staticmethod
    def get_shortest_path(source_name, target_name):
        """查询两个实体之间的最短路径"""
        query = """
        MATCH (p1:Entity {name: $source}), (p2:Entity {name: $target})
        MATCH p = shortestPath((p1)-[*..10]-(p2))
        RETURN p
        """
        try:
            result = Neo4jConnection.query(query, {"source": source_name, "target": target_name})
            
            if not result:
                return None
            
            path_record = result[0]['p']
            
            nodes = {}
            edges = []
            
            for node in path_record.nodes:
                name = node['name']
                django_id = node.get('django_id')
                final_id = Neo4jGraphService._to_str_id(django_id) or name
                
                if name not in nodes:
                    nodes[name] = {
                        'id': final_id,
                        'label': name,
                        'type': node.get('type', 'unknown'),
                        'size': 15
                    }
            
            for rel in path_record.relationships:
                start_name = rel.start_node['name']
                end_name = rel.end_node['name']
                
                start_id = nodes[start_name]['id']
                end_id = nodes[end_name]['id']
                
                edges.append({
                    'source': start_id,
                    'target': end_id,
                    'label': rel.get('type', rel.type)
                })
                
            return {'nodes': list(nodes.values()), 'edges': edges}
            
        except Exception as e:
            logger.error(f"Error in get_shortest_path: {e}")
            return None

# 全局服务实例
graph_service = Neo4jGraphService()
