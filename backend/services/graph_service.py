from knowledge_graph.neo4j_db import Neo4jConnection
import logging

logger = logging.getLogger(__name__)

class Neo4jGraphService:
    """
    Neo4j图数据库服务
    """
    
    @staticmethod
    def get_entity_subgraph(entity_name, limit=50):
        """
        获取实体相关子图 (1-hop)
        :param entity_name: 实体名称
        :param limit: 限制返回的邻居节点数量
        """
        # 1. 查找中心节点
        # 2. 查找出边关系 (outgoing)
        # 3. 查找入边关系 (incoming)
        
        query = """
        MATCH (center:Entity {name: $name})
        
        // 获取出边，携带目标节点信息
        OPTIONAL MATCH (center)-[r1]->(target:Entity)
        WITH center, collect({
            source: center.name, 
            target: target.name, 
            source_id: center.django_id,
            target_id: target.django_id,
            relation: coalesce(r1.type, type(r1)), 
            target_type: target.type
        })[..$limit] as outgoing
        
        // 获取入边，携带源节点信息
        OPTIONAL MATCH (source:Entity)-[r2]->(center)
        WITH center, outgoing, collect({
            source: source.name, 
            target: center.name, 
            source_id: source.django_id,
            target_id: center.django_id,
            relation: coalesce(r2.type, type(r2)), 
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
            nodes[center_name] = {
                'id': str(center_id) if center_id else center_name, # 优先使用 ID，兼容旧数据用 name
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
                
                if target_name not in nodes:
                    nodes[target_name] = {
                        'id': str(target_id) if target_id else target_name,
                        'label': target_name, 
                        'type': item['target_type'], 
                        'size': 15
                    }
                
                edges.append({
                    'source': nodes[center_name]['id'],
                    'target': nodes[target_name]['id'],
                    'label': item['relation'],
                    'description': '' # Neo4j 关系属性中如果有描述可加上
                })

            # 处理入边
            for item in record['incoming']:
                if not item or item['source'] is None: continue
                source_name = item['source']
                source_id = item['source_id']
                
                if source_name not in nodes:
                    nodes[source_name] = {
                        'id': str(source_id) if source_id else source_name,
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
                    'id': r['id'],
                    'name': r['name'],
                    'type': r['type']
                })
            return entities
        except Exception as e:
            logger.error(f"Error in search_entities: {e}")
            return []

    @staticmethod
    def get_graph_overview(limit=50):
        """
        获取图谱概览（仅返回重要节点，例如度数最高的节点）
        不再返回全量数据，避免浏览器卡死
        """
        # 修改查询策略：
        # 1. 优先选择连接数多（度数高）的节点，而不是随机节点，这样更有可能看到关系
        # 2. 同时查找入边和出边，不仅仅是出边
        
        query = """
        MATCH (n:Entity)
        OPTIONAL MATCH (n)-[r]-()
        WITH n, count(r) as degree
        ORDER BY degree DESC
        LIMIT $node_limit
        
        // 查找这些高频节点之间的关系（包括出边和入边，避免方向问题遗漏）
        OPTIONAL MATCH (n)-[r]-(m:Entity)
        RETURN n.name as source_name, n.type as source_type, n.django_id as source_id,
               coalesce(r.type, type(r)) as rel_type,
               m.name as target_name, m.type as target_type, m.django_id as target_id,
               startNode(r) = n as is_outgoing
        LIMIT $rel_limit
        """
        
        params = {"node_limit": limit, "rel_limit": limit * 4} # 增加关系限制
        try:
            result = Neo4jConnection.query(query, params)
            if not result:
                return {'nodes': [], 'edges': []}
                
            nodes = {}
            edges = []
            
            for row in result:
                s_name = row['source_name']
                s_id = row['source_id']
                t_name = row['target_name']
                t_id = row['target_id']
                rel_type = row['rel_type']
                is_outgoing = row['is_outgoing']
                
                # 添加当前中心节点 (n)
                if s_name and s_name not in nodes:
                    nodes[s_name] = {
                        'id': str(s_id) if s_id else s_name, 
                        'label': s_name, 
                        'type': row['source_type'], 
                        'size': 20
                    }
                
                # 添加由于关系连接到的节点 (m) 和边
                if t_name and rel_type: 
                    if t_name not in nodes:
                         nodes[t_name] = {
                             'id': str(t_id) if t_id else t_name, 
                             'label': t_name, 
                             'type': row['target_type'], 
                             'size': 15
                         }
                    
                    # 只有当 n 是起始点时才添加边，避免 (A)-(B) 和 (B)-(A) 造成重复边
                    # 或者我们依靠 distinct 也可以，这里为了简单，我们全部添加，由前端处理或这里去重
                    # 这里逻辑优化：始终以 source -> target 添加边
                    
                    source_node_id = nodes[s_name]['id']
                    target_node_id = nodes[t_name]['id']
                    
                    # 确定边的真正方向
                    if is_outgoing:
                        # n -> m
                        edge = {
                            'source': source_node_id,
                            'target': target_node_id,
                            'label': rel_type
                        }
                    else:
                        # m -> n
                        edge = {
                            'source': target_node_id,
                            'target': source_node_id,
                            'label': rel_type
                        }

                    # 防止重复添加边 (简单去重)
                    edge_key = f"{edge['source']}_{edge['target']}_{edge['label']}"
                    # 这里用一个简单的检查，实际上 edges 是 list，效率略低但数据量小没关系
                    if not any(e['source'] == edge['source'] and e['target'] == edge['target'] and e['label'] == edge['label'] for e in edges):
                        edges.append(edge)
            
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
        # 使用 shortestPath 函数
        query = """
        MATCH (p1:Entity {name: $source}), (p2:Entity {name: $target})
        MATCH p = shortestPath((p1)-[*..10]-(p2))
        RETURN p
        """
        try:
            result = Neo4jConnection.query(query, {"source": source_name, "target": target_name})
            
            if not result:
                return None
            
            # Neo4j Driver 返回的 Path 对象需要特殊处理
            # 但如果你用 simple json result，可能拿到的是复杂的结构
            # 假设 Neo4jConnection 处理了 session.run 的结果
            
            # 由于 python neo4j driver 返回的是 Path 对象，包含 nodes 和 relationships
            path_record = result[0]['p']
            
            nodes = {}
            edges = []
            
            for node in path_record.nodes:
                name = node['name']
                django_id = node.get('django_id')
                if name not in nodes:
                    nodes[name] = {
                        'id': django_id if django_id else name,
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
