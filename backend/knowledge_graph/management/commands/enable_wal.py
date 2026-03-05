from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Enable SQLite WAL mode for better concurrency'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check current mode
            cursor.execute("PRAGMA journal_mode;")
            current_mode = cursor.fetchone()[0]
            self.stdout.write(f"Current journal mode: {current_mode}")
            
            if current_mode.upper() != 'WAL':
                self.stdout.write("Enabling WAL mode...")
                cursor.execute("PRAGMA journal_mode=WAL;")
                new_mode = cursor.fetchone()[0]
                if new_mode.upper() == 'WAL':
                    self.stdout.write(self.style.SUCCESS("Successfully enabled WAL mode."))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to enable WAL mode. Current mode: {new_mode}"))
            else:
                self.stdout.write(self.style.SUCCESS("WAL mode is already enabled."))
