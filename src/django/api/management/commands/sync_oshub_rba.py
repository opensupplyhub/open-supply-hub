import logging
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Sync data from OS Hub (default) to RBA (rba DB) by UUID"

    def add_arguments(self, parser):
        parser.add_argument(
            '--table',
            required=False,
            help='Model name to sync (app_label.ModelName). If not provided, syncs all models.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only show changes, do not apply them'
        )

    def __update_sequence(self, model, using='rba'):
        """Update the sequence for a model's primary key to prevent ID conflicts"""
        try:
            # Get the table name
            table_name = model._meta.db_table
            
            # Get the primary key field name
            pk_field = model._meta.pk.name
            
            # Construct sequence name (PostgreSQL convention)
            sequence_name = f"{table_name}_{pk_field}_seq"
            
            # Update the sequence to the maximum ID value
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT setval('{sequence_name}', 
                        COALESCE((SELECT MAX({pk_field}) FROM {table_name}), 1)
                    );
                """)

            logger.info(f"Updated sequence {sequence_name} for {table_name}")

        except Exception as e:
            logger.warning(f"Failed to update sequence for {model._meta.db_table}: {e}")

    def __prepare_objects_for_sync(self, objects, model):
        """Prepare objects for sync by removing ID to avoid conflicts"""
        prepared_objects = []
        
        for obj in objects:
            # Create a new instance without the ID to let the target DB generate a new one
            obj_data = {}

            # Copy all fields except the primary key
            for field in model._meta.fields:
                if field.primary_key:
                    continue  # Skip the primary key field

                value = getattr(obj, field.name)
                obj_data[field.name] = value

            # Create a new model instance with the copied data
            new_obj = model(**obj_data)
            prepared_objects.append(new_obj)

        return prepared_objects

    def __sync_objects_to_rba(self, model, prepared_objs):
        """Sync prepared objects to RBA database"""
        model.objects.using('rba').bulk_create(prepared_objs, batch_size=500)

        # Update the sequence after bulk insert to prevent ID conflicts
        if prepared_objs:
            self.__update_sequence(model, using='rba')

    def __sync_single_model(self, model, dry_run=False):
        """Sync a single model from OS Hub to RBA"""
        logger.info(f"Syncing model {model._meta.app_label}.{model._meta.model_name}")

        # Get UUIDs from both databases in batches to avoid memory issues
        batch_size = 10000
        
        # Get all UUIDs from RBA (target database)
        rba_uuids = set()
        rba_qs = model.objects.using('rba').values_list('uuid', flat=True)
        
        for batch_start in range(0, rba_qs.count(), batch_size):
            batch_uuids = list(rba_qs[batch_start:batch_start + batch_size])
            rba_uuids.update(batch_uuids)
        
        logger.info(
            f"Found {len(rba_uuids)} existing UUIDs in RBA for "
            f"{model._meta.app_label}.{model._meta.model_name}."
        )

        # Get UUIDs from OS Hub (source database) and find missing ones
        missing_uuids = set()
        source_qs = model.objects.using('default').values_list('uuid', flat=True)
        
        for batch_start in range(0, source_qs.count(), batch_size):
            batch_uuids = list(source_qs[batch_start:batch_start + batch_size])
            missing_uuids.update(uuid for uuid in batch_uuids if uuid not in rba_uuids)
        
        logger.info(
            f"Found {len(missing_uuids)} missing UUIDs to sync for "
            f"{model._meta.app_label}.{model._meta.model_name}."
        )

        if dry_run:
            logger.warning(
                f"[DRY-RUN] Would insert {len(missing_uuids)} records into RBA for "
                f"{model._meta.app_label}.{model._meta.model_name}."
            )
            return

        # Process missing records in batches
        if missing_uuids:
            self.__sync_missing_records(model, missing_uuids, batch_size)
        else:
            logger.info(
                f"No new records to sync for "
                f"{model._meta.app_label}.{model._meta.model_name}."
            )

    def __sync_missing_records(self, model, missing_uuids, batch_size=1000):
        """Sync missing records in batches to avoid memory issues"""
        total_synced = 0
        
        # Process UUIDs in batches
        uuids_list = list(missing_uuids)
        for i in range(0, len(uuids_list), batch_size):
            batch_uuids = uuids_list[i:i + batch_size]
            
            # Fetch only the records we need from OS Hub
            batch_objects = list(
                model.objects.using('default').filter(uuid__in=batch_uuids)
            )
            
            # Prepare objects for sync (remove IDs to avoid conflicts)
            prepared_objs = self.__prepare_objects_for_sync(batch_objects, model)
            
            # Write batch to RBA
            self.__sync_objects_to_rba(model, prepared_objs)
            
            total_synced += len(prepared_objs)
            
            logger.info(
                f"Synced batch {i//batch_size + 1}: {len(prepared_objs)} records "
                f"({total_synced}/{len(missing_uuids)} total)"
            )
        
        logger.info(
            f"Successfully inserted {total_synced} new records into RBA for "
            f"{model._meta.app_label}.{model._meta.model_name}."
        )

    def __get_all_models(self):
        """Get all models that have a UUID field and exist in both databases"""
        all_models = []
        
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                # Check if model has UUID field
                try:
                    model._meta.get_field('uuid')
                    # Check if model exists in both databases
                    try:
                        # Test if model exists in default DB
                        model.objects.using('default').count()
                        # Test if model exists in RBA DB
                        model.objects.using('rba').count()
                        all_models.append(model)
                    except Exception as e:
                        logger.debug(
                            f"Skipping {model._meta.app_label}.{model._meta.model_name}: {e}"
                        )
                except:
                    # Model doesn't have a UUID field, skip it
                    continue
        
        return all_models

    def __validate_model_has_uuid(self, model):
        """Validate that a model has a UUID field"""
        try:
            model._meta.get_field('uuid')
            return True
        except:
            return False

    @transaction.atomic(using='rba')
    def handle(self, *args, **options):
        table = options['table']
        dry_run = options['dry_run']

        logger.info(f"Starting sync from OS Hub (default) → RBA. Dry run: {dry_run}")

        if table:
            # Sync single table
            try:
                app_label, model_name = table.split('.')
                model = apps.get_model(app_label, model_name)
            except (ValueError, LookupError):
                raise CommandError("Invalid table format. Use app_label.ModelName")
            
            # Validate that the model has a UUID field
            if not self.__validate_model_has_uuid(model):
                raise CommandError(
                    f"Model {table} does not have a UUID field. Only models with UUID fields can be synced."
                )

            self.__sync_single_model(model, dry_run)
        else:
            # Full synchronization
            logger.info(
                "No table specified. Performing full synchronization of all models with UUID fields."
            )
            
            all_models = self.__get_all_models()
            logger.info(
                f"Found {len(all_models)} models with UUID fields for synchronization."
            )
            
            for model in all_models:
                try:
                    self.__sync_single_model(model, dry_run)
                except Exception as e:
                    logger.error(
                        f"Failed to sync {model._meta.app_label}.{model._meta.model_name}: {e}"
                    )
                    continue
            
            logger.info("Full synchronization completed.")

