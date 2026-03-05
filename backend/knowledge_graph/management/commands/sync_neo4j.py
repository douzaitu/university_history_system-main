
from django.core.management.base import BaseCommand
from knowledge_graph.models import Entity, Relationship
from knowledge_graph.neo4j_db import Neo4jConnection
from knowledge_graph.tasks import sync_entity_task, sync_relationship_task
import time

class Command(BaseCommand):
    help = 'Fully synchronize SQLite data to Neo4j'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting full synchronization...'))
        
        # 1. Clear existing data
        self.stdout.write('Clearing Neo4j database...')
        Neo4jConnection.query("MATCH (n) DETACH DELETE n")
        
        # 2. Create constraints/indexes
        self.stdout.write('Creating constraints...')
        try:
            # Ensure django_id is unique for Entity
            Neo4jConnection.query("CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (n:Entity) REQUIRE n.django_id IS UNIQUE")
            # Create index for Relationship django_id for faster lookups
            Neo4jConnection.query("CREATE INDEX relationship_id_index IF NOT EXISTS FOR ()-[r:RELATION]-() ON (r.django_id)")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating constraints: {e}'))

        # 3. Sync Entities
        entities = Entity.objects.all()
        total_entities = entities.count()
        self.stdout.write(f'Syncing {total_entities} entities...')
        
        for i, entity in enumerate(entities):
            try:
                # Direct call to task logic (synchronously)
                sync_entity_task(entity.id)
                if (i + 1) % 100 == 0:
                    self.stdout.write(f'  Synced {i + 1}/{total_entities} entities')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error syncing entity {entity.name}: {e}'))

        # 4. Sync Relationships
        relationships = Relationship.objects.all()
        total_rels = relationships.count()
        self.stdout.write(f'Syncing {total_rels} relationships...')
        
        for i, rel in enumerate(relationships):
            try:
                # Direct call to task logic (synchronously)
                sync_relationship_task(rel.id)
                if (i + 1) % 100 == 0:
                    self.stdout.write(f'  Synced {i + 1}/{total_rels} relationships')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error syncing relationship {rel.id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully synced {total_entities} entities and {total_rels} relationships.'))
