from django.core.management.base import BaseCommand
from django_q.models import Failure, Success, OrmQ
from django.db import transaction

class Command(BaseCommand):
    help = 'Clear Django Q tasks (failed, successful, or queued)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--failed',
            action='store_true',
            help='Clear all failed tasks',
        )
        parser.add_argument(
            '--success',
            action='store_true',
            help='Clear all successful tasks',
        )
        parser.add_argument(
            '--queued',
            action='store_true',
            help='Clear all queued tasks',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all tasks (failed, successful, and queued)',
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options['all'] or options['failed']:
                count, _ = Failure.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {count} failed tasks'))
            
            if options['all'] or options['success']:
                count, _ = Success.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {count} successful tasks'))

            if options['all'] or options['queued']:
                count, _ = OrmQ.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {count} queued tasks'))

        if not any([options['all'], options['failed'], options['success'], options['queued']]):
            self.stdout.write(self.style.WARNING('No action specified. Use --failed, --success, --queued, or --all to clear tasks.'))