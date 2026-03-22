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
            # Ensure driver is initialized
            driver = Neo4jConnection.get_driver()
            if driver:
                Neo4jConnection.query("MATCH (n) DETACH DELETE n")
                self.stdout.write(self.style.SUCCESS('Successfully cleared Neo4j database.'))
            else:
                self.stdout.write(self.style.WARNING('Neo4j driver could not be initialized. Check connection settings.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to clear Neo4j: {str(e)}'))

        # 2. Clear Database (Django Models)
        try:
            # Delete in order to respect foreign keys if any (though usually fine with cascade)
            Relationship.objects.all().delete()
            self.stdout.write('Deleted all Relationships')
            
            Entity.objects.all().delete()
            self.stdout.write('Deleted all Entities')
            
            Document.objects.all().delete()
            self.stdout.write('Deleted all Documents')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to clear Django models: {str(e)}'))

        # 3. Clear Media Files
        media_subdirs = ['document_images', 'entity_photos', 'documents']
        
        for subdir in media_subdirs:
            dir_path = os.path.join(settings.MEDIA_ROOT, subdir)
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    os.makedirs(dir_path, exist_ok=True)
                    self.stdout.write(f'Cleared media directory: {subdir}')
                except Exception as e:
                     self.stdout.write(self.style.WARNING(f'Failed to clear media directory {subdir}: {e}'))
            else:
                self.stdout.write(f'Media directory not found (skipped): {subdir}')
                # Create it if it doesn't exist, just in case
                os.makedirs(dir_path, exist_ok=True)

        # 4. Attempt to delete SQLite file if it exists (regardless of setting, check default location)
        # Try to delete db.sqlite3 in BASE_DIR if it exists
        potential_sqlite = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        if os.path.exists(potential_sqlite):
             try:
                 # Closing connections might be needed before deletion on Windows
                 from django.db import connections
                 connections.close_all()
                 
                 os.remove(potential_sqlite)
                 self.stdout.write(self.style.SUCCESS(f'Deleted SQLite database file: {potential_sqlite}'))
             except Exception as e:
                 self.stdout.write(self.style.WARNING(f'Could not delete db.sqlite3 (might be in use): {e}. Please delete manually.'))
        else:
             self.stdout.write('No db.sqlite3 file found in BASE_DIR.')

        self.stdout.write(self.style.SUCCESS('Successfully cleared all data and media files.'))