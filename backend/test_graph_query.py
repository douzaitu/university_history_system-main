import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from knowledge_graph.neo4j_db import Neo4jConnection

def test_overview_query():
    limit = 50
    node_limit = limit
    rel_limit = limit * 4
    
    query = """
    MATCH (n:Entity)
    OPTIONAL MATCH (n)-[r]-()
    WITH n, count(r) as degree
    ORDER BY degree DESC
    LIMIT $node_limit
    
    // 查找这些高频节点之间的关系（包括出边和入边）
    OPTIONAL MATCH (n)-[r]-(m:Entity)
    RETURN n.name as source_name, n.type as source_type, n.django_id as source_id,
           type(r) as rel_type,
           m.name as target_name, m.type as target_type, m.django_id as target_id,
           startNode(r) = n as is_outgoing
    LIMIT $rel_limit
    """
    
    params = {"node_limit": node_limit, "rel_limit": rel_limit}
    
    print(f"Executing query with node_limit={node_limit}, rel_limit={rel_limit}...")
    try:
        result = Neo4jConnection.query(query, params)
        if not result:
            print("No results returned from query.")
            return

        print(f"Got {len(result)} rows.")
        
        nodes = {}
        edges = []
        
        for i, row in enumerate(result):
            if i < 3:
                print(f"Row {i}: {row}")

            s_name = row['source_name']
            t_name = row['target_name']
            rel_type = row['rel_type']
            
            if s_name:
                nodes[s_name] = True
            if t_name:
                nodes[t_name] = True
            
            if s_name and t_name and rel_type:
                edges.append(f"{s_name} -[{rel_type}]-> {t_name}")

        print(f"\nTotal unique nodes collected: {len(nodes)}")
        print(f"Total edges collected: {len(edges)}")
        
        if len(edges) == 0:
            print("WARNING: No edges found in the result set!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_overview_query()
