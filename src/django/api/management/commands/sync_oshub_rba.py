import logging
import time
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Sync data from OS Hub (default) to RBA (rba DB) by UUID"

    def __init__(self):
        super().__init__()
        self.sync_stats = {}
        self.start_time = None
        self.syncing_models = set()  # Track models currently being synced to prevent cycles
        self.cached_missing_refs = {}  # Cache missing references to avoid repeated queries

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
            # Continue without updating sequence - this is not critical

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

    def __sync_objects_to_rba(self, model, prepared_objs, dry_run=False):
        """Sync prepared objects to RBA database"""
        try:
            # Try bulk_create first (faster)
            model.objects.using('rba').bulk_create(prepared_objs, batch_size=500)
            logger.info(f"Successfully bulk created {len(prepared_objs)} objects for {model._meta.app_label}.{model._meta.model_name}")
            # Update the sequence after bulk insert to prevent ID conflicts
            if prepared_objs:
                self.__update_sequence(model, using='rba')
        except Exception as e:
            if "Adapter" in str(e) or "DatabaseOperations" in str(e):
                logger.warning(f"Bulk create failed due to database adapter issue, falling back to individual inserts: {e}")
                self.__sync_objects_individually(model, prepared_objs)
            elif "foreign key" in str(e).lower() or "constraint" in str(e).lower():
                logger.warning(f"Bulk create failed due to foreign key constraints, falling back to dependency-aware individual inserts: {e}")
                self.__sync_objects_individually_with_dependencies(model, prepared_objs, dry_run)
            else:
                logger.error(f"Failed to sync objects for {model._meta.app_label}.{model._meta.model_name}: {e}")
                raise

    def __sync_objects_individually(self, model, prepared_objs):
        """Fallback method: sync objects individually when bulk_create fails"""
        logger.info(f"Syncing {len(prepared_objs)} objects individually for {model._meta.app_label}.{model._meta.model_name}")
        successful_inserts = 0
        failed_inserts = 0
        for i, obj in enumerate(prepared_objs):
            try:
                obj.save(using='rba')
                successful_inserts += 1
                # Log progress every 100 objects
                if (i + 1) % 100 == 0:
                    logger.info(f"Individual sync progress: {i + 1}/{len(prepared_objs)} objects processed")
            except Exception as e:
                failed_inserts += 1
                logger.warning(f"Failed to insert object {i + 1} for {model._meta.app_label}.{model._meta.model_name}: {e}")
                continue
        logger.info(f"Individual sync completed: {successful_inserts} successful, {failed_inserts} failed")
        # Update the sequence after individual inserts
        if successful_inserts > 0:
            self.__update_sequence(model, using='rba')

    def __get_model_foreign_key_dependencies(self, model):
        """Dynamically detect foreign key dependencies for a model"""
        dependencies = []
        for field in model._meta.fields:
            if hasattr(field, 'related_model') and field.related_model:
                # This is a foreign key field
                related_model = field.related_model
                try:
                    related_model._meta.get_field('uuid')
                    # Only include models that have UUID fields (syncable models)
                    dependency_key = f"{related_model._meta.app_label}.{related_model._meta.model_name}"
                    if dependency_key not in dependencies:
                        dependencies.append(dependency_key)
                except:
                    # Model doesn't have a UUID field, skip it
                    continue
        return dependencies

    def __get_models_to_sync(self, target_model=None):
        """Get all models that need to be synced, including dependencies"""
        if target_model:
            # Single table sync - get the model and all its dependencies
            models_to_sync = self.__get_dependency_chain(target_model)
            logger.info(f"Single table sync requested for {target_model._meta.app_label}.{target_model._meta.model_name}")
            logger.info(f"Will sync dependency chain: {[f'{m._meta.app_label}.{m._meta.model_name}' for m in models_to_sync]}")
        else:
            # Full sync - get all models with dependency resolution
            all_models = self.__get_all_models()
            models_to_sync = self.__build_full_dependency_chain(all_models)
            logger.info(f"Full sync requested for {len(models_to_sync)} models")

        return models_to_sync

    def __get_dependency_chain(self, target_model):
        """Get the complete dependency chain for a single model"""
        dependency_chain = []
        processed = set()

        def add_model_with_dependencies(model):
            model_key = f"{model._meta.app_label}.{model._meta.model_name}"
            if model_key in processed:
                return
            processed.add(model_key)
            # Get dependencies for this model
            dependencies = self.__get_model_foreign_key_dependencies(model)
            # Recursively add dependencies first
            for dep_key in dependencies:
                try:
                    app_label, model_name = dep_key.split('.')
                    dep_model = apps.get_model(app_label, model_name)
                    if self.__validate_model_has_uuid(dep_model):
                        add_model_with_dependencies(dep_model)
                except (ValueError, LookupError):
                    logger.warning(f"Could not resolve dependency {dep_key} for {model_key}")
            # Add this model after its dependencies
            if model not in dependency_chain:
                dependency_chain.append(model)

        add_model_with_dependencies(target_model)

        # Always ensure User model is synced first if it's in the dependency chain
        return self.__prioritize_user_model(dependency_chain)

    def __prioritize_user_model(self, models_list):
        """Ensure User model is always synced first if present in the list"""
        try:
            # Try to get the User model
            user_model = apps.get_model('auth', 'User')

            # Check if User model is in the list and has UUID field
            if user_model in models_list and self.__validate_model_has_uuid(user_model):
                # Remove User model from its current position
                models_list = [m for m in models_list if m != user_model]
                # Add User model at the beginning
                models_list.insert(0, user_model)
                logger.info("User model prioritized to sync first")
        except (ValueError, LookupError):
            # User model not found or doesn't have UUID field, continue as normal
            pass

        return models_list

    def __validate_foreign_key_constraints(self, model, dry_run=False):
        """Validate that all foreign key references exist in target database"""
        if dry_run:
            # In dry-run mode, just check if foreign key constraints would be violated
            missing_refs = []

            for field in model._meta.fields:
                if hasattr(field, 'related_model') and field.related_model:
                    related_model = field.related_model
                    try:
                        related_model._meta.get_field('uuid')
                        # Check if this foreign key field has any references to non-existent records
                        source_uuids = set(model.objects.using('default').values_list(field.name, flat=True).distinct())
                        target_uuids = set(related_model.objects.using('rba').values_list('uuid', flat=True))
                        
                        missing_uuids = source_uuids - target_uuids
                        if missing_uuids:
                            missing_refs.append({
                                'field': field.name,
                                'related_model': f"{related_model._meta.app_label}.{related_model._meta.model_name}",
                                'missing_count': len(missing_uuids)
                            })
                    except:
                        # Model doesn't have a UUID field, skip it
                        continue

            if missing_refs:
                logger.warning(f"Foreign key constraint violations would occur for {model._meta.app_label}.{model._meta.model_name} (will be handled on-demand during real sync):")
                for ref in missing_refs:
                    logger.warning(f"  • {ref['field']} → {ref['related_model']}: {ref['missing_count']} missing references")
                return False

            return True
        else:
            # In real sync mode, skip validation - we'll handle missing references on-demand
            return True

    def __sync_single_model(self, model, dry_run=False):
        """Sync a single model from OS Hub to RBA"""
        model_key = f"{model._meta.app_label}.{model._meta.model_name}"
        logger.info(f"Syncing model {model_key}")

        # Validate foreign key constraints in dry-run mode (but don't fail, just warn)
        if dry_run:
            self.__validate_foreign_key_constraints(model, dry_run=True)

        # Get UUIDs from both databases in batches to avoid memory issues
        batch_size = 10000

        # Get all UUIDs from RBA (target database)
        rba_uuids = set()
        rba_qs = model.objects.using('rba').values_list('uuid', flat=True)

        for batch_start in range(0, rba_qs.count(), batch_size):
            batch_uuids = set(rba_qs[batch_start:batch_start + batch_size])
            rba_uuids.update(batch_uuids)

        logger.info(
            f"Found {len(rba_uuids)} existing UUIDs in RBA for "
            f"{model_key}."
        )

        # Get UUIDs from OS Hub (source database) and find missing ones
        missing_uuids = set()
        source_qs = model.objects.using('default').values_list('uuid', flat=True)

        for batch_start in range(0, source_qs.count(), batch_size):
            batch_uuids = set(source_qs[batch_start:batch_start + batch_size])
            missing_uuids.update(batch_uuids)

        missing_uuids.difference_update(rba_uuids)

        logger.info(
            f"Found {len(missing_uuids)} missing UUIDs to sync for "
            f"{model_key}."
        )

        self.sync_stats[model_key] = {
            'total_source': source_qs.count(),
            'total_target': len(rba_uuids),
            'to_sync': len(missing_uuids)
        }

        if dry_run:
            logger.warning(
                f"[DRY-RUN] Would insert {len(missing_uuids)} records into RBA for "
                f"{model_key}."
            )
            return

        # Process missing records in batches within a transaction for this model only
        if missing_uuids:
            with transaction.atomic(using='rba'):
                self.__sync_missing_records(model, missing_uuids, batch_size, dry_run)
                logger.info(f"Successfully committed changes for {model_key}")
        else:
            logger.info(
                f"No new records to sync for "
                f"{model_key}."
            )

    def __sync_missing_records(self, model, missing_uuids, batch_size=1000, dry_run=False):
        """Sync missing records in batches to avoid memory issues"""
        total_synced = 0

        # Process UUIDs in batches
        uuids_list = list(missing_uuids)
        for i in range(0, len(uuids_list), batch_size):
            batch_uuids = set(uuids_list[i:i + batch_size])

            # Fetch only the records we need
            batch_objects = list(
                model.objects.using('default').filter(uuid__in=batch_uuids)
            )

            # Double-check that these UUIDs don't already exist in RBA
            existing_uuids = set(
                model.objects.using('rba').filter(uuid__in=batch_uuids).values_list('uuid', flat=True)
            )
            new_uuids = batch_uuids - existing_uuids
            
            if new_uuids != batch_uuids:
                logger.warning(
                    f"Some UUIDs already exist in RBA, skipping duplicates: "
                    f"{len(batch_uuids - new_uuids)} duplicates found"
                )
                # Filter out objects that already exist
                batch_objects = [obj for obj in batch_objects if obj.uuid in new_uuids]

            if not batch_objects:
                logger.info(f"Batch {i//batch_size + 1}: No new records to sync (all were duplicates)")
                continue

            # Prepare objects for sync (remove IDs to avoid conflicts)
            prepared_objs = self.__prepare_objects_for_sync(batch_objects, model)

            # Pre-check for foreign key constraints and sync missing references
            if not dry_run:
                self.__pre_sync_foreign_key_references(model, prepared_objs)

            # Write batch to RBA
            try:
                self.__sync_objects_to_rba(model, prepared_objs, dry_run)
                total_synced += len(prepared_objs)
            except Exception as e:
                if "foreign key" in str(e).lower() or "constraint" in str(e).lower():
                    logger.warning(f"Foreign key constraint violation during bulk sync, falling back to individual sync: {e}")
                    # Fallback to individual sync with dependency resolution
                    self.__sync_objects_individually_with_dependencies(model, prepared_objs, dry_run)
                    total_synced += len(prepared_objs)
                else:
                    raise

            logger.info(
                f"Synced batch {i//batch_size + 1}: {len(prepared_objs)} records "
                f"({total_synced}/{len(missing_uuids)} total)"
            )

        logger.info(
            f"Successfully inserted {total_synced} new records into RBA for "
            f"{model._meta.app_label}.{model._meta.model_name}."
        )

    def __pre_sync_foreign_key_references(self, model, prepared_objs):
        """Pre-check and sync missing foreign key references before bulk insert"""
        all_missing_refs = {}

        # Collect all missing foreign key references
        for obj in prepared_objs:
            missing_refs = self.__get_missing_foreign_key_references(obj, model)
            for field_name, missing_ids in missing_refs.items():
                if field_name not in all_missing_refs:
                    all_missing_refs[field_name] = set()
                all_missing_refs[field_name].update(missing_ids)
        
        # Sync missing references
        for field_name, missing_ids in all_missing_refs.items():
            if missing_ids:
                logger.info(f"Pre-syncing {len(missing_ids)} missing {field_name} references")
                self.__sync_missing_foreign_key_references(model, field_name, missing_ids, dry_run=False)

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

        # Always prioritize User model if it exists and has UUID field
        return self.__prioritize_user_model(all_models)

    def __validate_model_has_uuid(self, model):
        """Validate that a model has a UUID field"""
        try:
            model._meta.get_field('uuid')
            return True
        except:
            return False

    def __print_summary_table(self, dry_run=False):
        """Print a summary table of sync statistics"""
        if not self.sync_stats:
            logger.info("No models were processed.")
            return

        total_models = len(self.sync_stats)
        total_source_records = sum(stats['total_source'] for stats in self.sync_stats.values())
        total_target_records = sum(stats['total_target'] for stats in self.sync_stats.values())
        total_to_sync = sum(stats['to_sync'] for stats in self.sync_stats.values())

        execution_time = time.time() - self.start_time

        logger.info("\n" + "="*80)
        logger.info("SYNC SUMMARY REPORT")
        logger.info("="*80)

        logger.info(f"{'Table':<40} {'Source':<10} {'Target':<10} {'To Sync':<10}")
        logger.info("-" * 80)

        for model_key, stats in sorted(self.sync_stats.items()):
            if stats['to_sync'] > 0:
                logger.info(
                    f"{model_key:<40} {stats['total_source']:<10} "
                    f"{stats['total_target']:<10} {stats['to_sync']:<10}"
                )

        logger.info("-" * 80)
        logger.info(
            f"{'TOTALS':<40} {total_source_records:<10} "
            f"{total_target_records:<10} {total_to_sync:<10}"
        )

        logger.info("\nSUMMARY:")
        logger.info(f"  • Models processed: {total_models}")
        logger.info(f"  • Models with records to sync: {len([s for s in self.sync_stats.values() if s['to_sync'] > 0])}")
        logger.info(f"  • Total execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")

        if dry_run:
            logger.info(f"  • Mode: DRY RUN (no changes applied)")
        else:
            logger.info(f"  • Mode: LIVE SYNC")

        logger.info("="*80)

    def __build_full_dependency_chain(self, all_models):
        """Build a complete dependency chain for all models in full sync mode"""
        dependency_chain = []
        processed = set()

        def add_model_with_dependencies(model):
            model_key = f"{model._meta.app_label}.{model._meta.model_name}"
            if model_key in processed:
                return
            processed.add(model_key)

            # Get dependencies for this model
            dependencies = self.__get_model_foreign_key_dependencies(model)

            # Recursively add dependencies first
            for dep_key in dependencies:
                try:
                    app_label, model_name = dep_key.split('.')
                    dep_model = apps.get_model(app_label, model_name)
                    if self.__validate_model_has_uuid(dep_model) and dep_model in all_models:
                        add_model_with_dependencies(dep_model)
                except (ValueError, LookupError):
                    logger.warning(f"Could not resolve dependency {dep_key} for {model_key}")

            # Add this model after its dependencies
            if model not in dependency_chain:
                dependency_chain.append(model)

        # Process all models to build the complete dependency chain
        for model in all_models:
            add_model_with_dependencies(model)

        # Always ensure User model is synced first if it's in the dependency chain
        return self.__prioritize_user_model(dependency_chain)

    def __sync_missing_foreign_key_references(self, model, field_name, missing_ids, dry_run=False):
        """Recursively sync missing foreign key references on-demand"""
        if dry_run:
            return  # Skip in dry-run mode

        related_model = model._meta.get_field(field_name).related_model
        if not related_model:
            return

        model_key = f"{related_model._meta.app_label}.{related_model._meta.model_name}"
        
        # Prevent infinite recursion
        if model_key in self.syncing_models:
            logger.warning(f"Circular dependency detected for {model_key}, skipping recursive sync")
            return

        logger.info(f"Syncing missing foreign key references: {len(missing_ids)} {model_key} records")

        try:
            self.syncing_models.add(model_key)

            # Get the missing records from source database by ID
            missing_objects = list(
                related_model.objects.using('default').filter(id__in=missing_ids)
            )

            if not missing_objects:
                logger.warning(f"No objects found in source DB for {len(missing_ids)} missing IDs")
                return

            # Check which ones are actually missing in target database by ID
            existing_ids = set(
                related_model.objects.using('rba').filter(id__in=missing_ids).values_list('id', flat=True)
            )
            actually_missing_ids = missing_ids - existing_ids

            if not actually_missing_ids:
                logger.info(f"All {len(missing_ids)} references already exist in target DB")
                return

            # Filter objects to only those actually missing
            actually_missing_objects = [obj for obj in missing_objects if obj.id in actually_missing_ids]

            # Prepare and sync the missing objects
            prepared_objs = self.__prepare_objects_for_sync(actually_missing_objects, related_model)

            # Use individual sync to handle any nested dependencies
            self.__sync_objects_individually_with_dependencies(related_model, prepared_objs, dry_run)

            logger.info(f"Successfully synced {len(actually_missing_objects)} missing {model_key} references")

        except Exception as e:
            logger.error(f"Failed to sync missing {model_key} references: {e}")
            raise
        finally:
            self.syncing_models.discard(model_key)

    def __sync_objects_individually_with_dependencies(self, model, prepared_objs, dry_run=False):
        """Sync objects individually while handling missing foreign key dependencies"""
        if dry_run:
            logger.info(f"[DRY-RUN] Would sync {len(prepared_objs)} objects individually with dependency resolution for {model._meta.app_label}.{model._meta.model_name}")
            return

        logger.info(f"Syncing {len(prepared_objs)} objects individually with dependency resolution for {model._meta.app_label}.{model._meta.model_name}")

        successful_inserts = 0
        failed_inserts = 0

        for i, obj in enumerate(prepared_objs):
            try:
                # Check for missing foreign key references before inserting
                missing_refs = self.__get_missing_foreign_key_references(obj, model)

                # Sync missing references recursively
                for field_name, missing_ids in missing_refs.items():
                    if missing_ids:
                        self.__sync_missing_foreign_key_references(model, field_name, missing_ids, dry_run)

                # Now try to insert the object
                obj.save(using='rba')
                successful_inserts += 1

                # Log progress every 100 objects
                if (i + 1) % 100 == 0:
                    logger.info(f"Individual sync progress: {i + 1}/{len(prepared_objs)} objects processed")

            except Exception as e:
                failed_inserts += 1
                logger.warning(f"Failed to insert object {i + 1} for {model._meta.app_label}.{model._meta.model_name}: {e}")
                continue

        logger.info(f"Individual sync with dependencies completed: {successful_inserts} successful, {failed_inserts} failed")

        # Update the sequence after individual inserts
        if successful_inserts > 0:
            self.__update_sequence(model, using='rba')

    def __get_missing_foreign_key_references(self, obj, model):
        """Get missing foreign key references for a single object"""
        missing_refs = {}

        for field in model._meta.fields:
            if hasattr(field, 'related_model') and field.related_model:
                related_model = field.related_model

                # Get the foreign key value using the raw ID field (e.g., facility_list_item_id)
                fk_id_field = f"{field.name}_id"
                fk_value = getattr(obj, fk_id_field, None)
                if fk_value is not None:
                    # Check if this reference exists in target database by ID
                    exists = related_model.objects.using('rba').filter(id=fk_value).exists()
                    if not exists:
                        if field.name not in missing_refs:
                            missing_refs[field.name] = set()
                        missing_refs[field.name].add(fk_value)

        return missing_refs

    def handle(self, *args, **options):
        self.start_time = time.time()
        table = options['table']
        dry_run = options['dry_run']

        logger.info(f"Starting sync from OS Hub (default) → RBA. Dry run: {dry_run}")

        if table:
            # Single table sync with automatic dependency resolution
            try:
                app_label, model_name = table.split('.')
                target_model = apps.get_model(app_label, model_name)
            except (ValueError, LookupError):
                raise CommandError("Invalid table format. Use app_label.ModelName")

            # Validate that the model has a UUID field
            if not self.__validate_model_has_uuid(target_model):
                raise CommandError(
                    f"Model {table} does not have a UUID field. Only models with UUID fields can be synced."
                )

            # Get all models that need to be synced (including dependencies)
            models_to_sync = self.__get_models_to_sync(target_model)

            successful_syncs = 0
            failed_syncs = 0

            for model in models_to_sync:
                try:
                    self.__sync_single_model(model, dry_run)
                    successful_syncs += 1
                except Exception as e:
                    failed_syncs += 1
                    logger.error(f"Failed to sync {model._meta.app_label}.{model._meta.model_name}: {e}")
                    
                    if dry_run:
                        # In dry-run mode, terminate on first error
                        logger.error("Dry-run terminated due to foreign key constraint violations.")
                        raise CommandError(f"Sync cannot proceed due to dependency issues: {e}")
                    else:
                        # In real sync mode, continue but log the issue
                        logger.info(
                            f"Previous successful syncs ({successful_syncs} tables) are preserved. "
                            f"Continuing with remaining tables..."
                        )
                        continue

            logger.info(
                f"Single table sync completed. "
                f"Successful: {successful_syncs}, Failed: {failed_syncs}"
            )
        else:
            # Full synchronization
            logger.info(
                "No table specified. Performing full synchronization of all models with UUID fields."
            )

            # Get all models that need to be synced
            models_to_sync = self.__get_models_to_sync()

            successful_syncs = 0
            failed_syncs = 0

            for model in models_to_sync:
                try:
                    self.__sync_single_model(model, dry_run)
                    successful_syncs += 1
                except Exception as e:
                    failed_syncs += 1
                    logger.error(
                        f"Failed to sync {model._meta.app_label}.{model._meta.model_name}: {e}"
                    )

                    if dry_run:
                        # In dry-run mode, terminate on first error
                        logger.error("Dry-run terminated due to foreign key constraint violations.")
                        raise CommandError(f"Sync cannot proceed due to dependency issues: {e}")
                    else:
                        # In real sync mode, continue but log the issue
                        logger.info(
                            f"Previous successful syncs ({successful_syncs} tables) are preserved. "
                            f"Continuing with remaining tables..."
                        )
                        continue

            logger.info(
                f"Full synchronization completed. "
                f"Successful: {successful_syncs}, Failed: {failed_syncs}"
            )

        self.__print_summary_table(dry_run)