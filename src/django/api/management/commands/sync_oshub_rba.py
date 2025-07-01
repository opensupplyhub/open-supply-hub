import logging
import time
from abc import ABC, abstractmethod
from typing import List, Set, Dict, Optional, Tuple, Any
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection, models
from django.db.models import Model
from django.core.exceptions import FieldDoesNotExist

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_BATCH_SIZE = 1000
DEFAULT_UUID_BATCH_SIZE = 10000
DEFAULT_BULK_BATCH_SIZE = 500
PROGRESS_LOG_INTERVAL = 100


# ============================================================================
# ABSTRACT BASE CLASSES (Strategy Pattern)
# ============================================================================

class ModelValidator(ABC):
    """Abstract base class for model validation strategies"""
    
    @abstractmethod
    def validate(self, model: Model) -> bool:
        """Validate if a model can be synced"""
        pass


class DependencyResolver(ABC):
    """Abstract base class for dependency resolution strategies"""
    
    @abstractmethod
    def resolve_dependencies(self, model: Model) -> List[Model]:
        """Resolve dependencies for a given model"""
        pass


class DataSyncStrategy(ABC):
    """Abstract base class for data synchronization strategies"""
    
    @abstractmethod
    def sync_objects(self, model: Model, objects: List[Model], dry_run: bool = False) -> int:
        """Sync objects to target database"""
        pass


class SequenceUpdater(ABC):
    """Abstract base class for sequence update strategies"""
    
    @abstractmethod
    def update_sequence(self, model: Model, using: str = 'rba') -> None:
        """Update sequence for a model's primary key"""
        pass


# ============================================================================
# CONCRETE IMPLEMENTATIONS
# ============================================================================

class UUIDModelValidator(ModelValidator):
    """Validates that models have UUID fields"""
    
    def validate(self, model: Model) -> bool:
        try:
            model._meta.get_field('uuid')
            return True
        except (AttributeError, ValueError, LookupError):
            return False


class ForeignKeyDependencyResolver(DependencyResolver):
    """Resolves foreign key dependencies for models"""
    
    def __init__(self):
        self.processed: Set[str] = set()
        self.syncing_models: Set[str] = set()
    
    def resolve_dependencies(self, model: Model) -> List[Model]:
        dependency_chain = []
        self.processed.clear()
        
        def add_model_with_dependencies(target_model: Model) -> None:
            model_key = f"{target_model._meta.app_label}.{target_model._meta.model_name}"
            if model_key in self.processed:
                return
            self.processed.add(model_key)
            
            # Get dependencies for this model
            dependencies = self.get_model_foreign_key_dependencies(target_model)
            
            # Recursively add dependencies first
            for dep_key in dependencies:
                try:
                    app_label, model_name = dep_key.split('.')
                    dep_model = apps.get_model(app_label, model_name)
                    if self.__validate_model_has_uuid(dep_model):
                        add_model_with_dependencies(dep_model)
                except (ValueError, LookupError) as e:
                    logger.warning(f"Could not resolve dependency {dep_key} for {model_key}: {e}")
            
            # Add this model after its dependencies
            if target_model not in dependency_chain:
                dependency_chain.append(target_model)
        
        add_model_with_dependencies(model)
        return self.__prioritize_user_model(dependency_chain)
    
    def get_model_foreign_key_dependencies(self, model: Model) -> List[str]:
        """Get foreign key dependencies for a model"""
        dependencies = []
        for field in model._meta.fields:
            if hasattr(field, 'related_model') and field.related_model:
                related_model = field.related_model
                try:
                    related_model._meta.get_field('uuid')
                    dependency_key = f"{related_model._meta.app_label}.{related_model._meta.model_name}"
                    if dependency_key not in dependencies:
                        dependencies.append(dependency_key)
                except (AttributeError, ValueError, LookupError, FieldDoesNotExist):
                    continue
        return dependencies
    
    def __validate_model_has_uuid(self, model: Model) -> bool:
        """Validate that a model has a UUID field"""
        try:
            model._meta.get_field('uuid')
            return True
        except (AttributeError, ValueError, LookupError):
            return False
    
    def __prioritize_user_model(self, models_list: List[Model]) -> List[Model]:
        """Ensure User model is always synced first if present"""
        try:
            user_model = apps.get_model('auth', 'User')
            if user_model in models_list and self.__validate_model_has_uuid(user_model):
                models_list = [m for m in models_list if m != user_model]
                models_list.insert(0, user_model)
                logger.info("User model prioritized to sync first")
        except (ValueError, LookupError):
            pass
        return models_list


class BulkSyncStrategy(DataSyncStrategy):
    """Bulk synchronization strategy using bulk_create"""
    
    def __init__(self, sequence_updater: SequenceUpdater):
        self.sequence_updater = sequence_updater
    
    def sync_objects(self, model: Model, objects: List[Model], dry_run: bool = False) -> int:
        if dry_run:
            logger.info(f"[DRY-RUN] Would bulk create {len(objects)} objects for {model._meta.app_label}.{model._meta.model_name}")
            return len(objects)
        
        if not objects:
            return 0
        
        try:
            model.objects.using('rba').bulk_create(objects, batch_size=500)
            logger.info(f"Successfully bulk created {len(objects)} objects for {model._meta.app_label}.{model._meta.model_name}")
            self.sequence_updater.update_sequence(model, using='rba')
            return len(objects)
        except Exception as e:
            if "Adapter" in str(e) or "DatabaseOperations" in str(e):
                logger.warning(f"Bulk create failed due to database adapter issue: {e}")
                raise
            elif "foreign key" in str(e).lower() or "constraint" in str(e).lower():
                logger.warning(f"Bulk create failed due to foreign key constraints: {e}")
                raise
            else:
                logger.error(f"Failed to sync objects for {model._meta.app_label}.{model._meta.model_name}: {e}")
                raise


class IndividualSyncStrategy(DataSyncStrategy):
    """Individual synchronization strategy for handling complex dependencies"""
    
    def __init__(self, sequence_updater: SequenceUpdater, foreign_key_handler: 'ForeignKeyHandler'):
        self.sequence_updater = sequence_updater
        self.foreign_key_handler = foreign_key_handler
    
    def sync_objects(self, model: Model, objects: List[Model], dry_run: bool = False) -> int:
        if not objects:
            logger.info(f"No objects to sync individually for {model._meta.app_label}.{model._meta.model_name}")
            return 0
            
        if dry_run:
            logger.info(f"[DRY-RUN] Would sync {len(objects)} objects individually for {model._meta.app_label}.{model._meta.model_name}")
            return len(objects)
        
        logger.info(f"Syncing {len(objects)} objects individually for {model._meta.app_label}.{model._meta.model_name}")
        
        successful_inserts = 0
        failed_inserts = 0
        
        for i, obj in enumerate(objects):
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Handle missing foreign key references
                    missing_refs = self.foreign_key_handler.get_missing_references(obj, model)
                    for field_name, missing_ids in missing_refs.items():
                        if missing_ids:
                            self.foreign_key_handler.sync_missing_references(model, field_name, missing_ids, dry_run)
                    
                    obj.save(using='rba')
                    successful_inserts += 1
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    error_message = str(e)
                    
                    # Check if it's a foreign key constraint error
                    if "foreign key" in error_message.lower() or "constraint" in error_message.lower():
                        if self.foreign_key_handler.handle_foreign_key_constraint_error(e, model, dry_run):
                            retry_count += 1
                            logger.info(f"Retrying insert after handling foreign key constraint (attempt {retry_count}/{max_retries})")
                            continue
                    
                    # If not a foreign key error or max retries reached, log and continue
                    failed_inserts += 1
                    logger.warning(f"Failed to insert object {i + 1} for {model._meta.app_label}.{model._meta.model_name}: {e}")
                    break
            
            if (i + 1) % PROGRESS_LOG_INTERVAL == 0:
                logger.info(f"Individual sync progress: {i + 1}/{len(objects)} objects processed")
        
        logger.info(f"Individual sync completed: {successful_inserts} successful, {failed_inserts} failed")
        
        if successful_inserts > 0:
            self.sequence_updater.update_sequence(model, using='rba')
        
        return successful_inserts


class PostgreSQLSequenceUpdater(SequenceUpdater):
    """Updates PostgreSQL sequences to prevent ID conflicts"""
    
    def update_sequence(self, model: Model, using: str = 'rba') -> None:
        try:
            table_name = model._meta.db_table
            pk_field = model._meta.pk.name
            sequence_name = f"{table_name}_{pk_field}_seq"
            
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT setval('{sequence_name}', 
                        COALESCE((SELECT MAX({pk_field}) FROM {table_name}), 1)
                    );
                """)
            logger.info(f"Updated sequence {sequence_name} for {table_name}")
        except Exception as e:
            logger.warning(f"Failed to update sequence for {model._meta.db_table}: {e}")


# ============================================================================
# REPOSITORY PATTERN
# ============================================================================

class ModelRepository:
    """Repository for model operations"""
    
    def __init__(self, source_db: str = 'default', target_db: str = 'rba'):
        self.source_db = source_db
        self.target_db = target_db
    
    def get_all_models_with_uuid(self) -> List[Model]:
        """Get all models that have UUID fields and exist in both databases"""
        all_models = []
        
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                try:
                    model._meta.get_field('uuid')
                    # Check if model exists in both databases
                    try:
                        model.objects.using(self.source_db).count()
                        model.objects.using(self.target_db).count()
                        all_models.append(model)
                    except Exception as e:
                        logger.debug(f"Skipping {model._meta.app_label}.{model._meta.model_name}: {e}")
                except Exception:
                    continue
        
        return all_models
    
    def get_existing_uuids(self, model: Model, batch_size: int = DEFAULT_UUID_BATCH_SIZE) -> Set[str]:
        """Get existing UUIDs from target database in batches"""
        rba_uuids = set()
        rba_qs = model.objects.using(self.target_db).values_list('uuid', flat=True)
        
        for batch_start in range(0, rba_qs.count(), batch_size):
            batch_uuids = set(rba_qs[batch_start:batch_start + batch_size])
            rba_uuids.update(batch_uuids)
        
        return rba_uuids
    
    def get_source_uuids(self, model: Model, batch_size: int = DEFAULT_UUID_BATCH_SIZE) -> Set[str]:
        """Get all UUIDs from source database in batches"""
        source_uuids = set()
        source_qs = model.objects.using(self.source_db).values_list('uuid', flat=True)
        
        for batch_start in range(0, source_qs.count(), batch_size):
            batch_uuids = set(source_qs[batch_start:batch_start + batch_size])
            source_uuids.update(batch_uuids)
        
        return source_uuids
    
    def get_objects_by_uuids(self, model: Model, uuids: Set[str]) -> List[Model]:
        """Get objects by UUIDs from source database"""
        if not uuids:
            return []
        return list(model.objects.using(self.source_db).filter(uuid__in=uuids))


# ============================================================================
# SERVICE LAYER
# ============================================================================

class ForeignKeyHandler:
    """Handles foreign key reference synchronization"""
    
    def __init__(self, model_repository: ModelRepository):
        self.model_repository = model_repository
        self.syncing_models: Set[str] = set()
    
    def get_missing_references(self, obj: Model, model: Model) -> Dict[str, List[str]]:
        """Get missing foreign key references for an object"""
        missing_refs = {}
        
        for field in model._meta.fields:
            if hasattr(field, 'related_model') and field.related_model:
                field_value = getattr(obj, field.name)
                if field_value is not None:
                    # Check if the referenced record exists in RBA
                    try:
                        related_model = field.related_model
                        if hasattr(related_model, 'objects'):
                            # Try to find by UUID first, then by ID
                            try:
                                related_model._meta.get_field('uuid')
                                exists = related_model.objects.using('rba').filter(uuid=field_value).exists()
                            except (AttributeError, ValueError, LookupError, FieldDoesNotExist):
                                exists = related_model.objects.using('rba').filter(id=field_value).exists()
                            
                            if not exists:
                                if field.name not in missing_refs:
                                    missing_refs[field.name] = []
                                missing_refs[field.name].append(str(field_value))
                    except Exception as e:
                        logger.warning(f"Error checking foreign key reference {field.name}: {e}")
        
        return missing_refs
    
    def parse_foreign_key_error(self, error_message: str) -> Optional[Tuple[str, str, str]]:
        """
        Parse foreign key constraint error message to extract table, column, and missing value.
        Returns (table_name, column_name, missing_value) or None if not a foreign key error.
        """
        import re
        
        # Pattern for PostgreSQL foreign key constraint errors
        # Example: "insert or update on table "api_facilitylistitem" violates foreign key constraint "api_facilitylistitem_facility_id_7c94a3a3_fk_api_facility_id"
        # DETAIL:  Key (facility_id)=(IT2025182QXF5D6) is not present in table "api_facility"."
        
        fk_pattern = r'insert or update on table "([^"]+)" violates foreign key constraint[^"]*"([^"]+)"[^"]*DETAIL:\s*Key \(([^)]+)\)=\(([^)]+)\) is not present in table "([^"]+)"'
        match = re.search(fk_pattern, error_message, re.IGNORECASE | re.DOTALL)
        
        if match:
            table_name = match.group(1)
            constraint_name = match.group(2)
            column_name = match.group(3)
            missing_value = match.group(4)
            referenced_table = match.group(5)
            return (referenced_table, column_name, missing_value)
        
        return None
    
    def handle_foreign_key_constraint_error(self, error: Exception, model: Model, dry_run: bool = False) -> bool:
        """Handle foreign key constraint error by attempting to sync missing references"""
        if dry_run:
            return False
        
        error_message = str(error)
        
        # Parse the foreign key error to get table, column, and missing value
        parsed_error = self.parse_foreign_key_error(error_message)
        if not parsed_error:
            return False
        
        table_name, column_name, missing_value = parsed_error
        
        logger.info(f"Attempting to resolve foreign key constraint: table={table_name}, column={column_name}, missing_value={missing_value}")
        
        try:
            # Find the field that corresponds to this foreign key
            field = None
            for f in model._meta.fields:
                if hasattr(f, 'related_model') and f.related_model:
                    related_table = f.related_model._meta.db_table
                    if related_table == table_name and f.column == column_name:
                        field = f
                        break
            
            if field:
                # Sync the missing reference
                self.sync_missing_references_in_transaction(model, field.name, [missing_value], dry_run)
                return True
            else:
                logger.warning(f"Could not find field for foreign key constraint: {table_name}.{column_name}")
                return False
                
        except Exception as e:
            logger.warning(f"Failed to handle foreign key constraint error: {e}")
            return False
    
    def sync_missing_references_in_transaction(self, model: Model, field_name: str, missing_ids: List[str], dry_run: bool = False) -> None:
        """Sync missing foreign key references within a transaction"""
        if dry_run:
            logger.info(f"[DRY-RUN] Would sync {len(missing_ids)} missing references for {field_name}")
            return
        
        # Get the related model
        field = model._meta.get_field(field_name)
        if not hasattr(field, 'related_model') or not field.related_model:
            return
        
        related_model = field.related_model
        
        # Try to sync each missing reference
        for missing_id in missing_ids:
            try:
                # Try to find the record in the source database
                if hasattr(related_model, 'objects'):
                    try:
                        # Try by UUID first
                        related_model._meta.get_field('uuid')
                        source_obj = related_model.objects.using('default').filter(uuid=missing_id).first()
                    except (AttributeError, ValueError, LookupError, FieldDoesNotExist):
                        # Try by ID
                        source_obj = related_model.objects.using('default').filter(id=missing_id).first()
                    
                    if source_obj:
                        # Prepare and insert the missing reference
                        prepared_obj = self.prepare_objects_for_sync([source_obj], related_model)[0]
                        prepared_obj.save(using='rba')
                        logger.info(f"Successfully synced missing reference {missing_id} for {field_name}")
                    else:
                        logger.warning(f"Could not find missing reference {missing_id} in source database for {field_name}")
            except Exception as e:
                logger.warning(f"Failed to sync missing reference {missing_id} for {field_name}: {e}")
    
    def prepare_objects_for_sync(self, objects: List[Model], model: Model) -> List[Model]:
        """Prepare objects for sync by removing ID to avoid conflicts"""
        prepared_objects = []
        for obj in objects:
            obj_data = {}
            for field in model._meta.fields:
                if field.primary_key:
                    continue
                value = getattr(obj, field.name)
                obj_data[field.name] = value
            new_obj = model(**obj_data)
            prepared_objects.append(new_obj)
        return prepared_objects


class SyncService:
    """Main service for orchestrating synchronization operations"""
    
    def __init__(self, model_repository: ModelRepository, validator: ModelValidator, 
                 dependency_resolver: DependencyResolver, foreign_key_handler: ForeignKeyHandler):
        self.model_repository = model_repository
        self.validator = validator
        self.dependency_resolver = dependency_resolver
        self.foreign_key_handler = foreign_key_handler
        self.sync_stats: Dict[str, Dict[str, int]] = {}
        self.start_time: Optional[float] = None
    
    def sync_model(self, model: Model, dry_run: bool = False) -> Dict[str, int]:
        """Sync a single model from source to target database"""
        model_key = f"{model._meta.app_label}.{model._meta.model_name}"
        logger.info(f"Syncing model {model_key}")
        
        # Get UUIDs from both databases
        rba_uuids = self.model_repository.get_existing_uuids(model)
        source_uuids = self.model_repository.get_source_uuids(model)
        missing_uuids = source_uuids - rba_uuids
        
        logger.info(f"Found {len(rba_uuids)} existing UUIDs in RBA for {model_key}")
        logger.info(f"Found {len(missing_uuids)} missing UUIDs to sync for {model_key}")
        
        # Update stats
        self.sync_stats[model_key] = {
            'total_source': len(source_uuids),
            'total_target': len(rba_uuids),
            'to_sync': len(missing_uuids)
        }
        
        if dry_run:
            logger.warning(f"[DRY-RUN] Would insert {len(missing_uuids)} records into RBA for {model_key}")
            return self.sync_stats[model_key]
        
        # Sync missing records without transaction wrapper
        if missing_uuids:
            self.__sync_missing_records_without_transaction(model, missing_uuids, dry_run)
            logger.info(f"Successfully completed sync for {model_key}")
        else:
            logger.info(f"No new records to sync for {model_key}")
        
        return self.sync_stats[model_key]
    
    def __sync_missing_records_without_transaction(self, model: Model, missing_uuids: Set[str], dry_run: bool = False) -> None:
        """Sync missing records without transaction wrapper to handle foreign key constraints better"""
        batch_size = 1000
        total_synced = 0
        
        uuids_list = list(missing_uuids)
        for i in range(0, len(uuids_list), batch_size):
            batch_uuids = set(uuids_list[i:i + batch_size])
            batch_objects = self.model_repository.get_objects_by_uuids(model, batch_uuids)
            
            # Check for duplicates
            existing_uuids = set(model.objects.using('rba').filter(uuid__in=batch_uuids).values_list('uuid', flat=True))
            new_uuids = batch_uuids - existing_uuids
            
            if new_uuids != batch_uuids:
                logger.warning(f"Some UUIDs already exist in RBA, skipping duplicates: {len(batch_uuids - new_uuids)} duplicates found")
                batch_objects = [obj for obj in batch_objects if obj.uuid in new_uuids]
            
            if not batch_objects:
                logger.info(f"Batch {i//batch_size + 1}: No new records to sync (all were duplicates)")
                continue
            
            # Prepare objects for sync
            prepared_objs = self.foreign_key_handler.prepare_objects_for_sync(batch_objects, model)
            
            # Try bulk sync first, fallback to individual sync
            try:
                bulk_strategy = BulkSyncStrategy(PostgreSQLSequenceUpdater())
                bulk_strategy.sync_objects(model, prepared_objs, dry_run)
                total_synced += len(prepared_objs)
                logger.info(f"Successfully bulk synced {len(prepared_objs)} records")
            except Exception as e:
                if "foreign key" in str(e).lower() or "constraint" in str(e).lower():
                    logger.warning(f"Foreign key constraint violation during bulk sync, falling back to individual sync: {e}")
                    # Sync each object individually with its own transaction
                    individual_synced = self.__sync_objects_individually_with_transactions(model, prepared_objs, dry_run)
                    total_synced += individual_synced
                else:
                    raise
            
            logger.info(f"Synced batch {i//batch_size + 1}: {len(prepared_objs)} records ({total_synced}/{len(missing_uuids)} total)")
        
        logger.info(f"Successfully inserted {total_synced} new records into RBA for {model._meta.app_label}.{model._meta.model_name}")
    
    def __sync_objects_individually_with_transactions(self, model: Model, objects: List[Model], dry_run: bool = False) -> int:
        """Sync objects individually, each in its own transaction"""
        if dry_run:
            logger.info(f"[DRY-RUN] Would sync {len(objects)} objects individually for {model._meta.app_label}.{model._meta.model_name}")
            return len(objects)
        
        logger.info(f"Syncing {len(objects)} objects individually for {model._meta.app_label}.{model._meta.model_name}")
        
        successful_inserts = 0
        failed_inserts = 0
        
        for i, obj in enumerate(objects):
            try:
                # Each object gets its own transaction
                with transaction.atomic(using='rba'):
                    # Handle missing foreign key references before inserting
                    missing_refs = self.foreign_key_handler.get_missing_references(obj, model)
                    for field_name, missing_ids in missing_refs.items():
                        if missing_ids:
                            self.foreign_key_handler.sync_missing_references_in_transaction(model, field_name, missing_ids, dry_run)
                    
                    # Try to insert the object
                    obj.save(using='rba')
                    successful_inserts += 1
                    
            except Exception as e:
                failed_inserts += 1
                error_message = str(e)
                
                # Check if it's a foreign key constraint error
                if "foreign key" in error_message.lower() or "constraint" in error_message.lower():
                    logger.warning(f"Foreign key constraint error for object {i + 1}: {e}")
                    # Try to resolve the foreign key constraint
                    if self.foreign_key_handler.handle_foreign_key_constraint_error(e, model, dry_run):
                        # Retry the insert in a new transaction
                        try:
                            with transaction.atomic(using='rba'):
                                obj.save(using='rba')
                                successful_inserts += 1
                                failed_inserts -= 1  # Adjust the count
                                logger.info(f"Successfully inserted object {i + 1} after resolving foreign key constraint")
                        except Exception as retry_error:
                            logger.warning(f"Failed to insert object {i + 1} even after resolving foreign key constraint: {retry_error}")
                else:
                    logger.warning(f"Failed to insert object {i + 1} for {model._meta.app_label}.{model._meta.model_name}: {e}")
            
            if (i + 1) % PROGRESS_LOG_INTERVAL == 0:
                logger.info(f"Individual sync progress: {i + 1}/{len(objects)} objects processed")
        
        logger.info(f"Individual sync completed: {successful_inserts} successful, {failed_inserts} failed")
        
        if successful_inserts > 0:
            sequence_updater = PostgreSQLSequenceUpdater()
            sequence_updater.update_sequence(model, using='rba')
        
        return successful_inserts
    
    def get_models_to_sync(self, target_model: Optional[Model] = None) -> List[Model]:
        """Get models that need to be synced, including dependencies"""
        if target_model:
            models_to_sync = self.dependency_resolver.resolve_dependencies(target_model)
            logger.info(f"Single table sync requested for {target_model._meta.app_label}.{target_model._meta.model_name}")
            logger.info(f"Will sync dependency chain: {[f'{m._meta.app_label}.{m._meta.model_name}' for m in models_to_sync]}")
        else:
            all_models = self.model_repository.get_all_models_with_uuid()
            models_to_sync = self.__build_full_dependency_chain(all_models)
            logger.info(f"Full sync requested for {len(models_to_sync)} models")
        
        return models_to_sync
    
    def __build_full_dependency_chain(self, all_models: List[Model]) -> List[Model]:
        """Build complete dependency chain for all models in full sync mode"""
        dependency_chain = []
        processed = set()
        
        def add_model_with_dependencies(model: Model):
            model_key = f"{model._meta.app_label}.{model._meta.model_name}"
            if model_key in processed:
                return
            processed.add(model_key)
            
            dependencies = self.dependency_resolver.get_model_foreign_key_dependencies(model)
            
            for dep_key in dependencies:
                try:
                    app_label, model_name = dep_key.split('.')
                    dep_model = apps.get_model(app_label, model_name)
                    if self.validator.validate(dep_model) and dep_model in all_models:
                        add_model_with_dependencies(dep_model)
                except (ValueError, LookupError):
                    logger.warning(f"Could not resolve dependency {dep_key} for {model_key}")
            
            if model not in dependency_chain:
                dependency_chain.append(model)
        
        for model in all_models:
            add_model_with_dependencies(model)
        
        return self.__prioritize_user_model(dependency_chain)
    
    def __prioritize_user_model(self, models_list: List[Model]) -> List[Model]:
        """Ensure User model is always synced first if present"""
        try:
            user_model = apps.get_model('auth', 'User')
            if user_model in models_list and self.validator.validate(user_model):
                models_list = [m for m in models_list if m != user_model]
                models_list.insert(0, user_model)
                logger.info("User model prioritized to sync first")
        except (ValueError, LookupError):
            pass
        return models_list
    
    def print_summary_table(self, dry_run: bool = False) -> None:
        """Print summary table of sync statistics"""
        if not self.sync_stats:
            logger.info("No models were processed.")
            return
        
        if self.start_time is None:
            logger.warning("Start time not set, cannot calculate execution time")
            execution_time = 0.0
        else:
            execution_time = time.time() - self.start_time
        
        total_models = len(self.sync_stats)
        total_source_records = sum(stats['total_source'] for stats in self.sync_stats.values())
        total_target_records = sum(stats['total_target'] for stats in self.sync_stats.values())
        total_to_sync = sum(stats['to_sync'] for stats in self.sync_stats.values())
        
        logger.info("\n" + "="*80)
        logger.info("SYNC SUMMARY REPORT")
        logger.info("="*80)
        
        logger.info(f"{'Table':<40} {'Source':<10} {'Target':<10} {'To Sync':<10}")
        logger.info("-" * 80)
        
        for model_key, stats in sorted(self.sync_stats.items()):
            if stats['to_sync'] > 0:
                logger.info(f"{model_key:<40} {stats['total_source']:<10} {stats['total_target']:<10} {stats['to_sync']:<10}")
        
        logger.info("-" * 80)
        logger.info(f"{'TOTALS':<40} {total_source_records:<10} {total_target_records:<10} {total_to_sync:<10}")
        
        logger.info("\nSUMMARY:")
        logger.info(f"  • Models processed: {total_models}")
        logger.info(f"  • Models with records to sync: {len([s for s in self.sync_stats.values() if s['to_sync'] > 0])}")
        if execution_time > 0:
            logger.info(f"  • Total execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")
        
        if dry_run:
            logger.info(f"  • Mode: DRY RUN (no changes applied)")
        else:
            logger.info(f"  • Mode: LIVE SYNC")
        
        logger.info("="*80)


# ============================================================================
# FACTORY PATTERN
# ============================================================================

class SyncServiceFactory:
    """Factory for creating sync services with proper dependencies"""
    
    @staticmethod
    def create_sync_service() -> SyncService:
        """Create a sync service with all required dependencies"""
        model_repository = ModelRepository()
        validator = UUIDModelValidator()
        dependency_resolver = ForeignKeyDependencyResolver()
        foreign_key_handler = ForeignKeyHandler(model_repository)
        
        return SyncService(model_repository, validator, dependency_resolver, foreign_key_handler)


# ============================================================================
# MAIN COMMAND CLASS
# ============================================================================

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

    def handle(self, *args, **options):
        # Create sync service using factory
        sync_service = SyncServiceFactory.create_sync_service()
        sync_service.start_time = time.time()
        
        table = options['table']
        dry_run = options['dry_run']
        
        logger.info(f"Starting sync from OS Hub (default) → RBA. Dry run: {dry_run}")
        
        try:
            if table:
                # Single table sync
                app_label, model_name = table.split('.')
                target_model = apps.get_model(app_label, model_name)
                
                if not sync_service.validator.validate(target_model):
                    raise CommandError(f"Model {table} does not have a UUID field. Only models with UUID fields can be synced.")
                
                models_to_sync = sync_service.get_models_to_sync(target_model)
                self.__sync_models(sync_service, models_to_sync, dry_run, "Single table")
            else:
                # Full synchronization
                logger.info("No table specified. Performing full synchronization of all models with UUID fields.")
                models_to_sync = sync_service.get_models_to_sync()
                self.__sync_models(sync_service, models_to_sync, dry_run, "Full")
            
            sync_service.print_summary_table(dry_run)
            
        except (ValueError, LookupError) as e:
            raise CommandError(f"Invalid table format or model not found: {e}")
    
    def __sync_models(self, sync_service: SyncService, models_to_sync: List[Model], dry_run: bool, sync_type: str) -> None:
        """Sync a list of models with error handling"""
        successful_syncs = 0
        failed_syncs = 0
        
        for model in models_to_sync:
            try:
                sync_service.sync_model(model, dry_run)
                successful_syncs += 1
            except Exception as e:
                failed_syncs += 1
                logger.error(f"Failed to sync {model._meta.app_label}.{model._meta.model_name}: {e}")
                
                if dry_run:
                    logger.error("Dry-run terminated due to errors.")
                    raise CommandError(f"Sync cannot proceed due to errors: {e}")
                else:
                    logger.info(f"Previous successful syncs ({successful_syncs} tables) are preserved. Continuing with remaining tables...")
                    continue
        
        logger.info(f"{sync_type} synchronization completed. Successful: {successful_syncs}, Failed: {failed_syncs}")