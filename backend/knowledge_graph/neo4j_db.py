import os
from neo4j import GraphDatabase

class Neo4jConnection:
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            # Get configuration from environment variables
            NEO4J_URI = os.getenv('NEO4J_URI', "bolt://localhost:7687")
            NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', "neo4j")
            NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', "12345678")
            
            try:
                cls._driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
                # Verify connectivity
                cls._driver.verify_connectivity()
                print("Neo4j Driver initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Neo4j driver: {e}")
                return None
                
        return cls._driver

    @classmethod
    def close_driver(cls):
        if cls._driver:
            cls._driver.close()
            cls._driver = None
            print("Neo4j Driver closed")

    @classmethod
    def query(cls, query, parameters=None, db=None):
        driver = cls.get_driver()
        if not driver:
            return None
            
        with driver.session(database=db) as session:
            result = session.run(query, parameters)
            return [record for record in result]
