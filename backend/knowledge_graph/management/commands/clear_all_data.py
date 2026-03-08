from django.core.management.base import BaseCommand
from django.conf import settings
from knowledge_graph.models import Entity, Relationship
from knowledge_graph.neo4j_db import Neo4jConnection
from documents.models import Document
import os
import shutil

class Command(BaseCommand):
    help = 'Clear all data from database (Entity, Relationship, Document) and media files, and Neo4j'

    def handle(self, *args, **options):
        self.stdout.write('Starting data cleanup...')

        # 1. Clear Neo4j Database directly (Detached Delete)
        try:
            self.stdout.write('Clearing Neo4j database...')
            Neo4jConnection.query("MATCH (n) DETACH DELETE n")
            self.stdout.write(self.style.SUCCESS('Successfully cleared Neo4j database.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to clear Neo4j: {str(e)}'))

        # 2. Clear Database (Django)
        Relationship.objects.all().delete()
        self.stdout.write('Deleted all Relationships')
        
        Entity.objects.all().delete()
        self.stdout.write('Deleted all Entities')
        
        Document.objects.all().delete()
        self.stdout.write('Deleted all Documents')

        # 2. Clear Media Files
        media_subdirs = ['document_images', 'entity_photos', 'documents']
        
        for subdir in media_subdirs:
            dir_path = os.path.join(settings.MEDIA_ROOT, subdir)
            if os.path.exists(dir_path):
                # Delete the entire directory and recreate it
                shutil.rmtree(dir_path)
                os.makedirs(dir_path, exist_ok=True)
                self.stdout.write(f'Cleared media directory: {subdir}')
            else:
                self.stdout.write(f'Media directory not found (skipped): {subdir}')
                # Create it if it doesn't exist, just in case
                os.makedirs(dir_path, exist_ok=True)

        self.stdout.write(self.style.SUCCESS('Successfully cleared all data and media files.'))