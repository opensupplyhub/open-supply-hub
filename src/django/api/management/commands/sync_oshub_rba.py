'''
1. What if creting updating production location takes time on OS Hub, and we need to wait for it to be created / updated before we can sync it to RBA?
2. Shall this script always run in a separate AWS job?
3. Shall we block RBA database from being updated while this script is running?
4. What if pipeline crashed while running this script?
5. How to monitor the status of this script and diffs between OS Hub and RBA?
6. Shall we have an ability to stop this script?
7. Is it possible to revert this script to the previous revision?
8. It looks like we need a separate database table to store the status of the sync process (and related information).
9. If there will be a table to store sync status, we need to apply respected UI (probably, in Django admin panel).
10. Shall it be bulc sync impicitly or it is better to check specific tables to be updated? For this, we need to apply specific pattern.
11. How to test this locally? Shall we use docker with local DB that will emulate RBA DB?
12. Need apapter class to communicate with RBA DB from OSHub Django OR listern to RBA DB events (like trigger, etc).
13. Need to Yes/No prompt to confirm sync if confict found. Highlight confilcted fields.
'''
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.apps import apps

class Command(BaseCommand):
    help = "Sync data from OS Hub (default) to RBA (rba DB) by UUID"

    def add_arguments(self, parser):
        parser.add_argument('--table', required=True, help='Model name to sync (app_label.ModelName)')
        parser.add_argument('--dry-run', action='store_true', help='Only show changes, do not apply them')

    def handle(self, *args, **options):
        table = options['table']
        dry_run = options['dry_run']

        try:
            app_label, model_name = table.split('.')
            model = apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            raise CommandError("Invalid table format. Use app_label.ModelName")

        self.stdout.write(f"Syncing table {table} from OS Hub (default) → RBA. Dry run: {dry_run}")

        # Debug: Show RBA database connection info
        from django.conf import settings
        rba_db_config = settings.DATABASES['rba']
        self.stdout.write(f"RBA DB Config: {rba_db_config}")

        # Fetch all records from OSHub (default DB)
        source_qs = model.objects.using('default').all()
        table_msg = ''
        if table:
            table_msg = f"table {table}"
        self.stdout.write(f"Fetched {source_qs.count()} records from OS Hub {table_msg}.")

        # Get UUIDs from RBA
        existing_uuids = set(
            model.objects.using('rba').values_list('uuid', flat=True)
        )
        self.stdout.write(f"Found {len(existing_uuids)} existing UUIDs in RBA.")

        # Filter only new records
        new_objs = [
            obj for obj in source_qs
            if getattr(obj, 'uuid', None) not in existing_uuids
        ]
        self.stdout.write(f"{len(new_objs)} new records to insert into RBA.")

        if dry_run:
            self.stdout.write(self.style.WARNING(f"[DRY-RUN] Would insert {len(new_objs)} records into RBA."))
            return

        # Write to RBA in transaction
        with transaction.atomic(using='rba'):
            model.objects.using('rba').bulk_create(new_objs, batch_size=500)

        self.stdout.write(self.style.SUCCESS(f"Inserted {len(new_objs)} new records into RBA."))

