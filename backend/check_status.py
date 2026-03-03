import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from knowledge_graph.neo4j_db import Neo4jConnection

def check():
    try:
        # Check for node distribution
        res = Neo4jConnection.query("MATCH (n:Entity) RETURN n.name as name, count(*) as c ORDER BY c DESC LIMIT 10")
        print("Top 10 most frequent node names:")
        for r in res:
            print(f"{r['name']}: {r['c']}")
            
        # Check for relationship count
        res = Neo4jConnection.query("MATCH ()-[r]->() RETURN count(r) as c")
        print(f"Total relationships: {res[0]['c'] if res else 0}")
        
    except Exception as e:
        print(f"Neo4j Error: {e}")

if __name__ == "__main__":
    check()
