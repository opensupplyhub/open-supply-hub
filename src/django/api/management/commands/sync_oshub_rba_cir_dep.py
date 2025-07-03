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

# FacilityListItem circular dependency related models
FACILITY_LIST_ITEM_RELATED_MODELS = [
    'api.Facility',              # FacilityListItem depends on Facility
    'api.Source',                # FacilityListItem depends on Source
    'api.FacilityListItem',      # Main model with circular dependencies
    'api.FacilityMatch',         # Depends on FacilityListItem
    'api.FacilityListItemField', # Depends on FacilityListItem
    'api.ExtendedField',         # Depends on FacilityListItem
]


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
        return dependency_chain
    
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


class FacilityListItemDependencyResolver(DependencyResolver):
    """Resolves dependencies specifically for FacilityListItem and its circular dependencies"""
    
    def __init__(self):
        self.processed: Set[str] = set()
    
    def resolve_dependencies(self, model: Model) -> List[Model]:
        """Resolve dependencies for FacilityListItem and related models only"""
        dependency_chain = []
        self.processed.clear()
        
        # Get all related models that are allowed
        allowed_models = self._get_allowed_models()
        
        def add_model_with_dependencies(target_model: Model) -> None:
            model_key = f"{target_model._meta.app_label}.{target_model._meta.model_name}"
            if model_key in self.processed:
                return
            self.processed.add(model_key)
            
            # Get dependencies for this model (only from allowed models)
            dependencies = self.get_model_foreign_key_dependencies(target_model, allowed_models)
            
            # Recursively add dependencies first
            for dep_key in dependencies:
                try:
                    app_label, model_name = dep_key.split('.')
                    dep_model = apps.get_model(app_label, model_name)
                    if self.__validate_model_has_uuid(dep_model) and dep_model in allowed_models:
                        add_model_with_dependencies(dep_model)
                except (ValueError, LookupError) as e:
                    logger.warning(f"Could not resolve dependency {dep_key} for {model_key}: {e}")
            
            # Add this model after its dependencies
            if target_model not in dependency_chain:
                dependency_chain.append(target_model)
        
        # Start with FacilityListItem model
        facility_list_item_model = apps.get_model('api', 'FacilityListItem')
        add_model_with_dependencies(facility_list_item_model)
        
        return self._prioritize_facility_list_item_models(dependency_chain)
    
    def get_model_foreign_key_dependencies(self, model: Model, allowed_models: List[Model]) -> List[str]:
        """Get foreign key dependencies for a model (only from allowed models)"""
        dependencies = []
        for field in model._meta.fields:
            if hasattr(field, 'related_model') and field.related_model:
                related_model = field.related_model
                try:
                    related_model._meta.get_field('uuid')
                    dependency_key = f"{related_model._meta.app_label}.{related_model._meta.model_name}"
                    
                    # Only include dependencies that are in our allowed models list
                    if related_model in allowed_models and dependency_key not in dependencies:
                        dependencies.append(dependency_key)
                except (AttributeError, ValueError, LookupError, FieldDoesNotExist):
                    continue
        return dependencies
    
    def _get_allowed_models(self) -> List[Model]:
        """Get list of models that are allowed for FacilityListItem sync"""
        allowed_models = []
        for model_key in FACILITY_LIST_ITEM_RELATED_MODELS:
            try:
                app_label, model_name = model_key.split('.')
                model = apps.get_model(app_label, model_name)
                if self.__validate_model_has_uuid(model):
                    allowed_models.append(model)
            except (ValueError, LookupError) as e:
                logger.warning(f"Could not load model {model_key}: {e}")
        return allowed_models
    
    def _prioritize_facility_list_item_models(self, models_list: List[Model]) -> List[Model]:
        """Prioritize models in the correct order for FacilityListItem sync"""
        prioritized_models = []
        
        # 1. Facility first (source table that others depend on)
        try:
            facility_model = apps.get_model('api', 'Facility')
            if facility_model in models_list:
                prioritized_models.append(facility_model)
                models_list = [m for m in models_list if m != facility_model]
                logger.info("Facility model prioritized to sync FIRST")
        except (ValueError, LookupError):
            pass
        
        # 2. Source model (FacilityListItem depends on it)
        try:
            source_model = apps.get_model('api', 'Source')
            if source_model in models_list:
                prioritized_models.append(source_model)
                models_list = [m for m in models_list if m != source_model]
                logger.info("Source model prioritized to sync second")
        except (ValueError, LookupError):
            pass
        
        # 3. FacilityListItem (main model with circular dependencies)
        try:
            facility_list_item_model = apps.get_model('api', 'FacilityListItem')
            if facility_list_item_model in models_list:
                prioritized_models.append(facility_list_item_model)
                models_list = [m for m in models_list if m != facility_list_item_model]
                logger.info("FacilityListItem model prioritized to sync third")
        except (ValueError, LookupError):
            pass
        
        # 4. FacilityMatch (depends on FacilityListItem)
        try:
            facility_match_model = apps.get_model('api', 'FacilityMatch')
            if facility_match_model in models_list:
                prioritized_models.append(facility_match_model)
                models_list = [m for m in models_list if m != facility_match_model]
                logger.info("FacilityMatch model prioritized to sync fourth")
        except (ValueError, LookupError):
            pass
        
        # 5. FacilityListItemField (depends on FacilityListItem)
        try:
            facility_list_item_field_model = apps.get_model('api', 'FacilityListItemField')
            if facility_list_item_field_model in models_list:
                prioritized_models.append(facility_list_item_field_model)
                models_list = [m for m in models_list if m != facility_list_item_field_model]
                logger.info("FacilityListItemField model prioritized to sync fifth")
        except (ValueError, LookupError):
            pass
        
        # 6. ExtendedField (depends on FacilityListItem)
        try:
            extended_field_model = apps.get_model('api', 'ExtendedField')
            if extended_field_model in models_list:
                prioritized_models.append(extended_field_model)
                models_list = [m for m in models_list if m != extended_field_model]
                logger.info("ExtendedField model prioritized to sync last")
        except (ValueError, LookupError):
            pass
        
        # Add any remaining models
        prioritized_models.extend(models_list)
        
        return prioritized_models
    
    def __validate_model_has_uuid(self, model: Model) -> bool:
        """Validate that a model has a UUID field"""
        try:
            model._meta.get_field('uuid')
            return True
        except (AttributeError, ValueError, LookupError):
            return False


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
                    # Check if model exists in source database
                    try:
                        model.objects.using(self.source_db).count()
                        # Only check target database if it's configured
                        if self.target_db in settings.DATABASES:
                            try:
                                model.objects.using(self.target_db).count()
                                all_models.append(model)
                            except Exception as e:
                                logger.debug(f"Target database not accessible for {model._meta.app_label}.{model._meta.model_name}: {e}")
                        else:
                            logger.warning(f"Target database '{self.target_db}' not configured in settings.DATABASES")
                            # Still add the model if source database is accessible
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
        # Track circular references that need to be updated after sync
        self.circular_references_to_update: List[Tuple[str, str, str]] = []  # (model_name, facility_uuid, created_from_id)
    
    def get_missing_references(self, obj: Model, model: Model) -> Dict[str, List[str]]:
        """Get missing foreign key references for an object"""
        missing_refs = {}
        
        for field in model._meta.fields:
            if hasattr(field, 'related_model') and field.related_model:
                try:
                    value = getattr(obj, field.name)
                    if value is not None:
                        # Check if the referenced object exists in the target database
                        related_model = field.related_model
                        try:
                            # Always use UUID for foreign key lookups since we sync by UUID
                            # and IDs are different between databases
                            related_model.objects.using('rba').get(uuid=value.uuid)
                        except (AttributeError, related_model.DoesNotExist):
                            # If we can't find by UUID, mark as missing reference
                            if field.name not in missing_refs:
                                missing_refs[field.name] = []
                            missing_refs[field.name].append(str(value.id))
                except Exception as e:
                    logger.debug(f"Error checking reference {field.name}: {e}")
                    continue
        
        return missing_refs
    
    def parse_foreign_key_error(self, error_message: str) -> Optional[Tuple[str, str, str]]:
        """Parse foreign key error message to extract table, column, and value"""
        import re
        
        # Special handling for created_from constraint errors first
        if "created_from_id" in error_message.lower():
            # Extract the ID from the error message
            id_match = re.search(r'Key \(created_from_id\)=\((\d+)\)', error_message)
            if id_match:
                return "api_facility", "created_from_id", id_match.group(1)
        
        # Common foreign key error patterns
        patterns = [
            r'insert or update on table "([^"]+)" violates foreign key constraint "([^"]+)"',
            r'Key \(([^)]+)\)=\(([^)]+)\) is not present in table "([^"]+)"',
            r'foreign key constraint "([^"]+)" on table "([^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3:
                    return match.group(1), match.group(2), match.group(3)
                elif len(match.groups()) == 2:
                    return match.group(1), match.group(2), "unknown"
        
        return None
    
    def handle_foreign_key_constraint_error(self, error: Exception, model: Model, dry_run: bool = False) -> bool:
        """Handle foreign key constraint errors by attempting to sync missing references"""
        error_message = str(error)
        parsed_error = self.parse_foreign_key_error(error_message)
        
        if not parsed_error:
            return False
        
        table_name, column_name, value = parsed_error
        logger.info(f"Foreign key constraint error: table={table_name}, column={column_name}, value={value}")
        
        # Special handling for created_from constraint errors
        if column_name == "created_from_id" and table_name == "api_facility":
            logger.info(f"Handling created_from constraint error for facility, value={value}")
            # This is expected during circular dependency handling, so we'll skip it
            # The created_from field should have been nullified during prepare_objects_for_sync
            return False
        
        # Try to sync the missing reference
        try:
            self.sync_missing_references_in_transaction(model, column_name, [value], dry_run)
            return True
        except Exception as e:
            logger.warning(f"Failed to sync missing reference for {column_name}={value}: {e}")
            return False
    
    def sync_missing_references_in_transaction(self, model: Model, field_name: str, missing_ids: List[str], dry_run: bool = False) -> None:
        """Sync missing foreign key references in a transaction"""
        if dry_run:
            logger.info(f"[DRY-RUN] Would sync missing references for {field_name}: {missing_ids}")
            return
        
        # Find the related model
        field = model._meta.get_field(field_name)
        if not hasattr(field, 'related_model') or not field.related_model:
            logger.warning(f"Field {field_name} is not a foreign key")
            return
        
        related_model = field.related_model
        
        # Get the missing objects from source database
        missing_objects = related_model.objects.using('default').filter(id__in=missing_ids)
        
        if not missing_objects:
            logger.warning(f"No objects found in source database for {field_name}: {missing_ids}")
            return
        
        # Sync the missing objects
        for obj in missing_objects:
            try:
                # Check if it already exists in target database
                existing = related_model.objects.using('rba').filter(uuid=obj.uuid).first()
                if not existing:
                    # Prepare and save the object
                    obj_data = {}
                    for obj_field in related_model._meta.fields:
                        if obj_field.primary_key:
                            continue
                        obj_data[obj_field.name] = getattr(obj, obj_field.name)
                    
                    new_obj = related_model(**obj_data)
                    new_obj.save(using='rba')
                    logger.info(f"Synced missing reference {obj.id} for {field_name}")
            except Exception as e:
                logger.warning(f"Failed to sync missing reference {obj.id} for {field_name}: {e}")
    
    def prepare_objects_for_sync(self, objects: List[Model], model: Model) -> List[Model]:
        """Prepare objects for sync by removing ID to avoid conflicts and handling circular dependencies"""
        prepared_objects = []
        for obj in objects:
            obj_data = {}
            for field in model._meta.fields:
                if field.primary_key:
                    continue
                
                value = getattr(obj, field.name)
                
                # Handle circular dependency: temporarily nullify created_from for facilities
                if (model._meta.model_name == 'Facility' and 
                    field.name == 'created_from' and 
                    value is not None):
                    logger.info(f"Temporarily nullifying created_from ({value}) for facility {obj.uuid} to break circular dependency")
                    # Store the reference for later update
                    self.circular_references_to_update.append((
                        model._meta.model_name,
                        obj.uuid,
                        str(value.id)  # Store the FacilityListItem ID
                    ))
                    logger.info(f"Added circular reference to track: Facility {obj.uuid} -> FacilityListItem {value.id}")
                    value = None
                
                # Handle foreign key ID mapping from OS Hub to RBA
                elif (hasattr(field, 'related_model') and field.related_model and 
                      value is not None and 
                      field.name not in ['created_from']):  # Don't map created_from here
                    try:
                        related_model = field.related_model
                        # Try to find the related object in RBA by UUID
                        try:
                            rba_obj = related_model.objects.using('rba').get(uuid=value.uuid)
                            # Map the ID from OS Hub to RBA
                            if hasattr(value, 'id') and hasattr(rba_obj, 'id'):
                                if value.id != rba_obj.id:
                                    logger.info(f"Mapping {field.name}: OS Hub ID {value.id} -> RBA ID {rba_obj.id}")
                                    # Always set the *_id field for foreign keys
                                    id_field_name = f"{field.name}_id"
                                    obj_data[id_field_name] = rba_obj.id
                                    # Do not set the object field itself
                                    value = None
                        except (AttributeError, related_model.DoesNotExist):
                            # If we can't find by UUID, try to sync the missing reference
                            logger.warning(f"Could not find {field.name} with UUID {value.uuid} in RBA, will try to sync missing reference")
                            # Don't nullify here, let the sync process handle it
                    except Exception as e:
                        logger.debug(f"Error mapping foreign key {field.name}: {e}")
                        # If mapping fails, keep the original value
                
                # Only add the field to obj_data if it's not None and it's not a foreign key object (we always set *_id instead)
                if value is not None and not (hasattr(field, 'related_model') and field.related_model and field.name not in ['created_from']):
                    obj_data[field.name] = value
            
            new_obj = model(**obj_data)
            prepared_objects.append(new_obj)
        
        logger.info(f"Prepared {len(prepared_objects)} objects for sync. Circular references to update: {len(self.circular_references_to_update)}")
        return prepared_objects
    
    def update_circular_references(self, dry_run: bool = False) -> None:
        """Update circular references after all models have been synced"""
        if not self.circular_references_to_update:
            logger.info("No circular references to update")
            return
        
        if dry_run:
            logger.info(f"[DRY-RUN] Would update {len(self.circular_references_to_update)} circular references")
            return
        
        logger.info(f"Updating {len(self.circular_references_to_update)} circular references...")
        logger.info(f"Circular references to update: {self.circular_references_to_update}")
        
        try:
            from django.apps import apps
            facility_model = apps.get_model('api', 'Facility')
            facility_list_item_model = apps.get_model('api', 'FacilityListItem')
            
            updated_count = 0
            for model_name, facility_uuid, created_from_id in self.circular_references_to_update:
                try:
                    logger.info(f"Processing circular reference: Facility {facility_uuid} -> FacilityListItem {created_from_id}")
                    
                    # Find the facility in RBA database
                    facility = facility_model.objects.using('rba').get(uuid=facility_uuid)
                    logger.info(f"Found facility in RBA: {facility.id}")
                    
                    # Find the facility list item in RBA database
                    facility_list_item = facility_list_item_model.objects.using('rba').get(id=created_from_id)
                    logger.info(f"Found facility list item in RBA: {facility_list_item.id}")
                    
                    # Update the created_from reference
                    facility.created_from = facility_list_item
                    facility.save(using='rba')
                    
                    updated_count += 1
                    logger.info(f"Successfully updated circular reference: Facility {facility_uuid} -> FacilityListItem {created_from_id}")
                    
                except (facility_model.DoesNotExist, facility_list_item_model.DoesNotExist) as e:
                    logger.warning(f"Could not update circular reference for Facility {facility_uuid} -> FacilityListItem {created_from_id}: {e}")
                except Exception as e:
                    logger.error(f"Error updating circular reference for Facility {facility_uuid} -> FacilityListItem {created_from_id}: {e}")
            
            logger.info(f"Successfully updated {updated_count}/{len(self.circular_references_to_update)} circular references")
            
        except Exception as e:
            logger.error(f"Error during circular reference update: {e}")
        
        # Clear the tracking list
        self.circular_references_to_update.clear()
    
    def prepare_objects_for_sync_aggressive(self, objects: List[Model], model: Model) -> List[Model]:
        """Prepare objects for sync with more aggressive foreign key handling"""
        prepared_objects = []
        for obj in objects:
            obj_data = {}
            for field in model._meta.fields:
                if field.primary_key:
                    continue
                
                value = getattr(obj, field.name)
                
                # Handle circular dependency: temporarily nullify created_from for facilities
                if (model._meta.model_name == 'Facility' and 
                    field.name == 'created_from' and 
                    value is not None):
                    logger.info(f"Temporarily nullifying created_from ({value}) for facility {obj.uuid} to break circular dependency")
                    # Store the reference for later update
                    self.circular_references_to_update.append((
                        model._meta.model_name,
                        obj.uuid,
                        str(value.id)  # Store the FacilityListItem ID
                    ))
                    logger.info(f"Added circular reference to track: Facility {obj.uuid} -> FacilityListItem {value.id}")
                    value = None
                
                # More aggressive handling: nullify problematic foreign keys (but not created_from)
                if (hasattr(field, 'related_model') and field.related_model and 
                    value is not None and 
                    field.name not in ['created_from']):  # Don't nullify created_from here
                    try:
                        # Check if the referenced object exists in target database
                        related_model = field.related_model
                        try:
                            related_model.objects.using('rba').get(uuid=value.uuid)
                        except (AttributeError, related_model.DoesNotExist):
                            try:
                                related_model.objects.using('rba').get(id=value.id)
                            except related_model.DoesNotExist:
                                logger.warning(f"Nullifying problematic foreign key {field.name}={value} for {model._meta.model_name} {obj.uuid}")
                                value = None
                    except Exception as e:
                        logger.debug(f"Error checking foreign key {field.name}: {e}")
                        # If we can't check, nullify to be safe
                        value = None
                
                # Only add the field to obj_data if it's not None and it's not a foreign key object (we always set *_id instead)
                if value is not None and not (hasattr(field, 'related_model') and field.related_model and field.name not in ['created_from']):
                    obj_data[field.name] = value
            
            new_obj = model(**obj_data)
            prepared_objects.append(new_obj)
        
        logger.info(f"Prepared {len(prepared_objects)} objects for aggressive sync. Circular references to update: {len(self.circular_references_to_update)}")
        return prepared_objects
    
    def resolve_all_dependencies_aggressive(self, obj: Model, model: Model, dry_run: bool = False) -> None:
        """Resolve all foreign key dependencies aggressively"""
        if dry_run:
            return
        
        for field in model._meta.fields:
            if hasattr(field, 'related_model') and field.related_model:
                try:
                    value = getattr(obj, field.name)
                    if value is not None:
                        # Try to sync the referenced object if it doesn't exist
                        related_model = field.related_model
                        try:
                            related_model.objects.using('rba').get(uuid=value.uuid)
                        except (AttributeError, related_model.DoesNotExist):
                            try:
                                related_model.objects.using('rba').get(id=value.id)
                            except related_model.DoesNotExist:
                                # The referenced object doesn't exist, try to sync it
                                logger.info(f"Attempting to sync missing dependency {field.name}={value} for {model._meta.model_name} {obj.uuid}")
                                try:
                                    # Get the object from source database
                                    source_obj = related_model.objects.using('default').get(id=value.id)
                                    
                                    # Prepare and save it
                                    obj_data = {}
                                    for obj_field in related_model._meta.fields:
                                        if obj_field.primary_key:
                                            continue
                                        obj_data[obj_field.name] = getattr(source_obj, obj_field.name)
                                    
                                    new_obj = related_model(**obj_data)
                                    new_obj.save(using='rba')
                                    logger.info(f"Successfully synced missing dependency {field.name}={value}")
                                except Exception as e:
                                    logger.warning(f"Failed to sync missing dependency {field.name}={value}: {e}")
                                    # Nullify the problematic foreign key
                                    setattr(obj, field.name, None)
                except Exception as e:
                    logger.debug(f"Error resolving dependency {field.name}: {e}")
                    continue

    def sync_problematic_facilities(self, dry_run: bool = False) -> None:
        """Special method to sync facilities with problematic created_from references"""
        if dry_run:
            logger.info("[DRY-RUN] Would sync problematic facilities")
            return
        
        from django.apps import apps
        facility_model = apps.get_model('api', 'Facility')
        facility_list_item_model = apps.get_model('api', 'FacilityListItem')
        
        # Get all facilities that exist in OS Hub but not in RBA
        os_uuids = set(facility_model.objects.using('default').values_list('uuid', flat=True))
        rba_uuids = set(facility_model.objects.using('rba').values_list('uuid', flat=True))
        missing_uuids = os_uuids - rba_uuids
        
        if not missing_uuids:
            logger.info("No problematic facilities found to sync")
            return
        
        logger.info(f"Found {len(missing_uuids)} facilities missing in RBA, attempting special sync...")
        
        successful_syncs = 0
        failed_syncs = 0
        
        for uuid in missing_uuids:
            try:
                # Get the facility from source database
                facility = facility_model.objects.using('default').get(uuid=uuid)
                
                # Create a copy with mapped created_from_id
                facility_data = {}
                for field in facility_model._meta.fields:
                    if field.primary_key:
                        continue
                    
                    value = getattr(facility, field.name)
                    
                    # Map created_from_id from OS Hub ID to RBA ID
                    if field.name == 'created_from' and value is not None:
                        logger.info(f"Mapping created_from from OS Hub ID {value.id} to RBA ID for facility {uuid}")
                        
                        # Find the corresponding FacilityListItem in RBA by UUID
                        try:
                            rba_facility_list_item = facility_list_item_model.objects.using('rba').get(uuid=value.uuid)
                            value = rba_facility_list_item
                            logger.info(f"Successfully mapped created_from: OS Hub ID {value.id} -> RBA ID {rba_facility_list_item.id}")
                        except facility_list_item_model.DoesNotExist:
                            logger.error(f"Could not find FacilityListItem with UUID {value.uuid} in RBA database")
                            failed_syncs += 1
                            continue
                    
                    facility_data[field.name] = value
                
                # Create and save the facility
                new_facility = facility_model(**facility_data)
                new_facility.save(using='rba')
                successful_syncs += 1
                logger.info(f"Successfully synced problematic facility {uuid}")
                
            except Exception as e:
                failed_syncs += 1
                logger.error(f"Failed to sync problematic facility {uuid}: {e}")
        
        logger.info(f"Problematic facilities sync completed: {successful_syncs} successful, {failed_syncs} failed")
        
        if successful_syncs > 0:
            # Update sequence
            sequence_updater = PostgreSQLSequenceUpdater()
            sequence_updater.update_sequence(facility_model, using='rba')

    def sync_problematic_extended_fields(self, dry_run: bool = False) -> None:
        """Special method to sync ExtendedField records with problematic foreign key references"""
        if dry_run:
            logger.info("[DRY-RUN] Would sync problematic extended fields")
            return
        
        from django.apps import apps
        extended_field_model = apps.get_model('api', 'ExtendedField')
        facility_model = apps.get_model('api', 'Facility')
        facility_list_item_model = apps.get_model('api', 'FacilityListItem')
        
        # Get all extended fields that exist in OS Hub but not in RBA
        os_uuids = set(extended_field_model.objects.using('default').values_list('uuid', flat=True))
        rba_uuids = set(extended_field_model.objects.using('rba').values_list('uuid', flat=True))
        missing_uuids = os_uuids - rba_uuids
        
        if not missing_uuids:
            logger.info("No problematic extended fields found to sync")
            return
        
        logger.info(f"Found {len(missing_uuids)} extended fields missing in RBA, attempting special sync...")
        
        successful_syncs = 0
        failed_syncs = 0
        
        for uuid in missing_uuids:
            try:
                # Get the extended field from source database
                extended_field = extended_field_model.objects.using('default').get(uuid=uuid)
                
                # Create a copy with mapped foreign key IDs
                extended_field_data = {}
                for field in extended_field_model._meta.fields:
                    if field.primary_key:
                        continue
                    
                    value = getattr(extended_field, field.name)
                    
                    # Map facility_id from OS Hub UUID to RBA UUID (same UUID, different ID)
                    if field.name == 'facility_id' and value is not None:
                        try:
                            # Find the facility in RBA by UUID
                            rba_facility = facility_model.objects.using('rba').get(uuid=value)
                            value = rba_facility.id
                            logger.info(f"Mapped facility_id: OS Hub UUID {value} -> RBA ID {rba_facility.id}")
                        except facility_model.DoesNotExist:
                            logger.warning(f"Could not find facility with UUID {value} in RBA database, nullifying")
                            value = None
                    
                    # Map facility_list_item_id from OS Hub ID to RBA ID
                    elif field.name == 'facility_list_item_id' and value is not None:
                        try:
                            # Get the facility list item from OS Hub to get its UUID
                            os_facility_list_item = facility_list_item_model.objects.using('default').get(id=value)
                            # Find the corresponding item in RBA by UUID
                            rba_facility_list_item = facility_list_item_model.objects.using('rba').get(uuid=os_facility_list_item.uuid)
                            value = rba_facility_list_item.id
                            logger.info(f"Mapped facility_list_item_id: OS Hub ID {value} -> RBA ID {rba_facility_list_item.id}")
                        except (facility_list_item_model.DoesNotExist, AttributeError) as e:
                            logger.warning(f"Could not map facility_list_item_id {value}: {e}, nullifying")
                            value = None
                    
                    extended_field_data[field.name] = value
                
                # Create and save the extended field
                new_extended_field = extended_field_model(**extended_field_data)
                new_extended_field.save(using='rba')
                successful_syncs += 1
                logger.info(f"Successfully synced problematic extended field {uuid}")
                
            except Exception as e:
                failed_syncs += 1
                logger.error(f"Failed to sync problematic extended field {uuid}: {e}")
        
        logger.info(f"Problematic extended fields sync completed: {successful_syncs} successful, {failed_syncs} failed")
        
        if successful_syncs > 0:
            # Update sequence
            sequence_updater = PostgreSQLSequenceUpdater()
            sequence_updater.update_sequence(extended_field_model, using='rba')

    def sync_problematic_facility_list_items(self, dry_run: bool = False) -> None:
        """Special method to sync FacilityListItem records with problematic foreign key references"""
        if dry_run:
            logger.info("[DRY-RUN] Would sync problematic facility list items")
            return
        
        from django.apps import apps
        facility_list_item_model = apps.get_model('api', 'FacilityListItem')
        facility_model = apps.get_model('api', 'Facility')
        source_model = apps.get_model('api', 'Source')
        
        # Get all facility list items that exist in OS Hub but not in RBA
        os_uuids = set(facility_list_item_model.objects.using('default').values_list('uuid', flat=True))
        rba_uuids = set(facility_list_item_model.objects.using('rba').values_list('uuid', flat=True))
        missing_uuids = os_uuids - rba_uuids
        
        if not missing_uuids:
            logger.info("No problematic facility list items found to sync")
            return
        
        logger.info(f"Found {len(missing_uuids)} facility list items missing in RBA, attempting special sync...")
        
        successful_syncs = 0
        failed_syncs = 0
        
        for uuid in missing_uuids:
            try:
                # Get the facility list item from source database
                facility_list_item = facility_list_item_model.objects.using('default').get(uuid=uuid)
                
                # Create a copy with mapped foreign key IDs
                facility_list_item_data = {}
                for field in facility_list_item_model._meta.fields:
                    if field.primary_key:
                        continue
                    
                    value = getattr(facility_list_item, field.name)
                    
                    # Map facility_id from OS Hub UUID to RBA UUID (same UUID, different ID)
                    if field.name == 'facility_id' and value is not None:
                        try:
                            # Find the facility in RBA by UUID
                            rba_facility = facility_model.objects.using('rba').get(uuid=value)
                            value = rba_facility.id
                            logger.info(f"Mapped facility_id: OS Hub UUID {value} -> RBA ID {rba_facility.id}")
                        except facility_model.DoesNotExist:
                            logger.warning(f"Could not find facility with UUID {value} in RBA database, nullifying")
                            value = None
                    
                    # Map source_id from OS Hub ID to RBA ID
                    elif field.name == 'source_id' and value is not None:
                        try:
                            # Get the source from OS Hub to get its UUID
                            os_source = source_model.objects.using('default').get(id=value)
                            # Find the corresponding source in RBA by UUID
                            rba_source = source_model.objects.using('rba').get(uuid=os_source.uuid)
                            value = rba_source.id
                            logger.info(f"Mapped source_id: OS Hub ID {value} -> RBA ID {rba_source.id}")
                        except (source_model.DoesNotExist, AttributeError) as e:
                            logger.warning(f"Could not map source_id {value}: {e}, nullifying")
                            value = None
                    
                    facility_list_item_data[field.name] = value
                
                # Create and save the facility list item
                new_facility_list_item = facility_list_item_model(**facility_list_item_data)
                new_facility_list_item.save(using='rba')
                successful_syncs += 1
                logger.info(f"Successfully synced problematic facility list item {uuid}")
                
            except Exception as e:
                failed_syncs += 1
                logger.error(f"Failed to sync problematic facility list item {uuid}: {e}")
        
        logger.info(f"Problematic facility list items sync completed: {successful_syncs} successful, {failed_syncs} failed")
        
        if successful_syncs > 0:
            # Update sequence
            sequence_updater = PostgreSQLSequenceUpdater()
            sequence_updater.update_sequence(facility_list_item_model, using='rba')

    def sync_problematic_facility_matches(self, dry_run: bool = False) -> None:
        """Special method to sync FacilityMatch records with problematic foreign key references"""
        if dry_run:
            logger.info("[DRY-RUN] Would sync problematic facility matches")
            return
        
        from django.apps import apps
        facility_match_model = apps.get_model('api', 'FacilityMatch')
        facility_model = apps.get_model('api', 'Facility')
        facility_list_item_model = apps.get_model('api', 'FacilityListItem')
        
        # Get all facility matches that exist in OS Hub but not in RBA
        os_uuids = set(facility_match_model.objects.using('default').values_list('uuid', flat=True))
        rba_uuids = set(facility_match_model.objects.using('rba').values_list('uuid', flat=True))
        missing_uuids = os_uuids - rba_uuids
        
        if not missing_uuids:
            logger.info("No problematic facility matches found to sync")
            return
        
        logger.info(f"Found {len(missing_uuids)} facility matches missing in RBA, attempting special sync...")
        
        successful_syncs = 0
        failed_syncs = 0
        
        for uuid in missing_uuids:
            try:
                # Get the facility match from source database
                facility_match = facility_match_model.objects.using('default').get(uuid=uuid)
                
                # Create a copy with mapped foreign key IDs
                facility_match_data = {}
                for field in facility_match_model._meta.fields:
                    if field.primary_key:
                        continue
                    
                    value = getattr(facility_match, field.name)
                    
                    # Map facility_id from OS Hub UUID to RBA UUID (same UUID, different ID)
                    if field.name == 'facility_id' and value is not None:
                        try:
                            # Find the facility in RBA by UUID
                            rba_facility = facility_model.objects.using('rba').get(uuid=value)
                            value = rba_facility.id
                            logger.info(f"Mapped facility_id: OS Hub UUID {value} -> RBA ID {rba_facility.id}")
                        except facility_model.DoesNotExist:
                            logger.warning(f"Could not find facility with UUID {value} in RBA database, nullifying")
                            value = None
                    
                    # Map facility_list_item_id from OS Hub ID to RBA ID
                    elif field.name == 'facility_list_item_id' and value is not None:
                        try:
                            # Get the facility list item from OS Hub to get its UUID
                            os_facility_list_item = facility_list_item_model.objects.using('default').get(id=value)
                            # Find the corresponding item in RBA by UUID
                            rba_facility_list_item = facility_list_item_model.objects.using('rba').get(uuid=os_facility_list_item.uuid)
                            value = rba_facility_list_item.id
                            logger.info(f"Mapped facility_list_item_id: OS Hub ID {value} -> RBA ID {rba_facility_list_item.id}")
                        except (facility_list_item_model.DoesNotExist, AttributeError) as e:
                            logger.warning(f"Could not map facility_list_item_id {value}: {e}, nullifying")
                            value = None
                    
                    facility_match_data[field.name] = value
                
                # Create and save the facility match
                new_facility_match = facility_match_model(**facility_match_data)
                new_facility_match.save(using='rba')
                successful_syncs += 1
                logger.info(f"Successfully synced problematic facility match {uuid}")
                
            except Exception as e:
                failed_syncs += 1
                logger.error(f"Failed to sync problematic facility match {uuid}: {e}")
        
        logger.info(f"Problematic facility matches sync completed: {successful_syncs} successful, {failed_syncs} failed")
        
        if successful_syncs > 0:
            # Update sequence
            sequence_updater = PostgreSQLSequenceUpdater()
            sequence_updater.update_sequence(facility_match_model, using='rba')

    def sync_problematic_facility_list_item_fields(self, dry_run: bool = False) -> None:
        """Special method to sync FacilityListItemField records with problematic foreign key references"""
        if dry_run:
            logger.info("[DRY-RUN] Would sync problematic facility list item fields")
            return
        
        from django.apps import apps
        facility_list_item_field_model = apps.get_model('api', 'FacilityListItemField')
        facility_model = apps.get_model('api', 'Facility')
        source_model = apps.get_model('api', 'Source')
        
        # Get all facility list item fields that exist in OS Hub but not in RBA
        os_uuids = set(facility_list_item_field_model.objects.using('default').values_list('uuid', flat=True))
        rba_uuids = set(facility_list_item_field_model.objects.using('rba').values_list('uuid', flat=True))
        missing_uuids = os_uuids - rba_uuids
        
        if not missing_uuids:
            logger.info("No problematic facility list item fields found to sync")
            return
        
        logger.info(f"Found {len(missing_uuids)} facility list item fields missing in RBA, attempting special sync...")
        
        successful_syncs = 0
        failed_syncs = 0
        
        for uuid in missing_uuids:
            try:
                # Get the facility list item field from source database
                facility_list_item_field = facility_list_item_field_model.objects.using('default').get(uuid=uuid)
                
                # Create a copy with mapped foreign key IDs
                facility_list_item_field_data = {}
                for field in facility_list_item_field_model._meta.fields:
                    if field.primary_key:
                        continue
                    
                    value = getattr(facility_list_item_field, field.name)
                    
                    # Map facility_id from OS Hub UUID to RBA UUID (same UUID, different ID)
                    if field.name == 'facility_id' and value is not None:
                        try:
                            # Find the facility in RBA by UUID
                            rba_facility = facility_model.objects.using('rba').get(uuid=value)
                            value = rba_facility.id
                            logger.info(f"Mapped facility_id: OS Hub UUID {value} -> RBA ID {rba_facility.id}")
                        except facility_model.DoesNotExist:
                            logger.warning(f"Could not find facility with UUID {value} in RBA database, nullifying")
                            value = None
                    
                    # Map source_id from OS Hub ID to RBA ID
                    elif field.name == 'source_id' and value is not None:
                        try:
                            # Get the source from OS Hub to get its UUID
                            os_source = source_model.objects.using('default').get(id=value)
                            # Find the corresponding source in RBA by UUID
                            rba_source = source_model.objects.using('rba').get(uuid=os_source.uuid)
                            value = rba_source.id
                            logger.info(f"Mapped source_id: OS Hub ID {value} -> RBA ID {rba_source.id}")
                        except (source_model.DoesNotExist, AttributeError) as e:
                            logger.warning(f"Could not map source_id {value}: {e}, nullifying")
                            value = None
                    
                    facility_list_item_field_data[field.name] = value
                
                # Create and save the facility list item field
                new_facility_list_item_field = facility_list_item_field_model(**facility_list_item_field_data)
                new_facility_list_item_field.save(using='rba')
                successful_syncs += 1
                logger.info(f"Successfully synced problematic facility list item field {uuid}")
                
            except Exception as e:
                failed_syncs += 1
                logger.error(f"Failed to sync problematic facility list item field {uuid}: {e}")
        
        logger.info(f"Problematic facility list item fields sync completed: {successful_syncs} successful, {failed_syncs} failed")
        
        if successful_syncs > 0:
            # Update sequence
            sequence_updater = PostgreSQLSequenceUpdater()
            sequence_updater.update_sequence(facility_list_item_field_model, using='rba')

    def handle_facility_list_item_constraints(self, dry_run: bool = False) -> None:
        """Handle all constraint issues for FacilityListItem and related tables"""
        if dry_run:
            logger.info("[DRY-RUN] Would handle FacilityListItem constraint issues")
            return
        
        logger.info("Handling FacilityListItem and related tables constraint issues...")
        
        # Handle each type of constraint issue
        try:
            self.sync_problematic_facilities(dry_run)
        except Exception as e:
            logger.error(f"Failed to handle facility constraints: {e}")
        
        try:
            self.sync_problematic_facility_list_items(dry_run)
        except Exception as e:
            logger.error(f"Failed to handle facility list item constraints: {e}")
        
        try:
            self.sync_problematic_facility_matches(dry_run)
        except Exception as e:
            logger.error(f"Failed to handle facility match constraints: {e}")
        
        try:
            self.sync_problematic_facility_list_item_fields(dry_run)
        except Exception as e:
            logger.error(f"Failed to handle facility list item field constraints: {e}")
        
        try:
            self.sync_problematic_extended_fields(dry_run)
        except Exception as e:
            logger.error(f"Failed to handle extended field constraints: {e}")
        
        logger.info("FacilityListItem constraint handling completed")


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
        failed_uuids = set()  # Track failed UUIDs for retry
        
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
                    individual_synced, individual_failed_uuids = self.__sync_objects_individually_with_transactions(model, prepared_objs, dry_run)
                    total_synced += individual_synced
                    failed_uuids.update(individual_failed_uuids)
                else:
                    # If it's not a foreign key error, track all UUIDs as failed
                    failed_uuids.update([obj.uuid for obj in prepared_objs])
                    raise
            
            logger.info(f"Synced batch {i//batch_size + 1}: {len(prepared_objs)} records ({total_synced}/{len(missing_uuids)} total)")
        
        # Retry failed records with more aggressive foreign key handling
        if failed_uuids and not dry_run:
            logger.info(f"Retrying {len(failed_uuids)} failed records with aggressive foreign key handling...")
            retry_synced, retry_failed_uuids = self.__retry_failed_records(model, failed_uuids, dry_run)
            total_synced += retry_synced
            failed_uuids = retry_failed_uuids
        
        logger.info(f"Successfully inserted {total_synced} new records into RBA for {model._meta.app_label}.{model._meta.model_name}")
        if failed_uuids:
            logger.warning(f"Failed to sync {len(failed_uuids)} records: {list(failed_uuids)[:10]}...")
    
    def __retry_failed_records(self, model: Model, failed_uuids: Set[str], dry_run: bool = False) -> Tuple[int, Set[str]]:
        """Retry failed records with more aggressive foreign key handling"""
        if dry_run:
            return 0, failed_uuids
        
        retry_objects = self.model_repository.get_objects_by_uuids(model, failed_uuids)
        if not retry_objects:
            return 0, failed_uuids
        
        # For facilities, use regular prepare_objects_for_sync to handle created_from properly
        if model._meta.model_name == 'Facility':
            prepared_objs = self.foreign_key_handler.prepare_objects_for_sync(retry_objects, model)
        else:
            # For other models, use aggressive handling
            prepared_objs = self.foreign_key_handler.prepare_objects_for_sync_aggressive(retry_objects, model)
        
        successful_inserts = 0
        still_failed_uuids = set()
        
        for obj in prepared_objs:
            try:
                with transaction.atomic(using='rba'):
                    # For facilities, don't try to resolve created_from dependencies
                    if model._meta.model_name != 'Facility':
                        # Try to resolve all foreign key dependencies aggressively
                        self.foreign_key_handler.resolve_all_dependencies_aggressive(obj, model, dry_run)
                    
                    # Try to insert the object
                    obj.save(using='rba')
                    successful_inserts += 1
                    
            except Exception as e:
                still_failed_uuids.add(obj.uuid)
                logger.warning(f"Failed to retry sync for {obj.uuid}: {e}")
        
        logger.info(f"Retry completed: {successful_inserts} successful, {len(still_failed_uuids)} still failed")
        return successful_inserts, still_failed_uuids
    
    def __sync_objects_individually_with_transactions(self, model: Model, objects: List[Model], dry_run: bool = False) -> Tuple[int, Set[str]]:
        """Sync objects individually, each in its own transaction"""
        if dry_run:
            logger.info(f"[DRY-RUN] Would sync {len(objects)} objects individually for {model._meta.app_label}.{model._meta.model_name}")
            return len(objects), set()
        
        logger.info(f"Syncing {len(objects)} objects individually for {model._meta.app_label}.{model._meta.model_name}")
        
        # Always use prepared objects (with circular dependencies handled)
        prepared_objects = self.foreign_key_handler.prepare_objects_for_sync(objects, model)
        
        successful_inserts = 0
        failed_inserts = 0
        failed_uuids = set()
        
        for i, obj in enumerate(prepared_objects):
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
                failed_uuids.add(obj.uuid)
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
                                failed_uuids.discard(obj.uuid)  # Remove from failed set
                                logger.info(f"Successfully inserted object {i + 1} after resolving foreign key constraint")
                        except Exception as retry_error:
                            logger.warning(f"Failed to insert object {i + 1} even after resolving foreign key constraint: {retry_error}")
                else:
                    logger.warning(f"Failed to insert object {i + 1} for {model._meta.app_label}.{model._meta.model_name}: {e}")
            
            if (i + 1) % PROGRESS_LOG_INTERVAL == 0:
                logger.info(f"Individual sync progress: {i + 1}/{len(prepared_objects)} objects processed")
        
        logger.info(f"Individual sync completed: {successful_inserts} successful, {failed_inserts} failed")
        
        if successful_inserts > 0:
            sequence_updater = PostgreSQLSequenceUpdater()
            sequence_updater.update_sequence(model, using='rba')
        
        return successful_inserts, failed_uuids
    
    def get_facility_list_item_models_to_sync(self) -> List[Model]:
        """Get models specifically for FacilityListItem circular dependency sync"""
        try:
            facility_list_item_model = apps.get_model('api', 'FacilityListItem')
            facility_list_item_resolver = FacilityListItemDependencyResolver()
            models_to_sync = facility_list_item_resolver.resolve_dependencies(facility_list_item_model)
            logger.info(f"FacilityListItem circular dependency sync requested")
            logger.info(f"Will sync models: {[f'{m._meta.app_label}.{m._meta.model_name}' for m in models_to_sync]}")
            return models_to_sync
        except (ValueError, LookupError) as e:
            logger.error(f"Could not resolve FacilityListItem dependencies: {e}")
            return []

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
        logger.info("FACILITYLISTITEM SYNC SUMMARY REPORT")
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

    def update_circular_references(self, dry_run: bool = False) -> None:
        """Update circular references after all models have been synced"""
        self.foreign_key_handler.update_circular_references(dry_run)
    
    def sync_problematic_facilities(self, dry_run: bool = False) -> None:
        """Sync problematic facilities with special handling"""
        self.foreign_key_handler.sync_problematic_facilities(dry_run)
    
    def sync_problematic_facility_list_items(self, dry_run: bool = False) -> None:
        """Special method to sync FacilityListItem records with problematic foreign key references"""
        self.foreign_key_handler.sync_problematic_facility_list_items(dry_run)

    def sync_problematic_extended_fields(self, dry_run: bool = False) -> None:
        """Special method to sync ExtendedField records with problematic foreign key references"""
        self.foreign_key_handler.sync_problematic_extended_fields(dry_run)

    def sync_problematic_facility_matches(self, dry_run: bool = False) -> None:
        """Special method to sync FacilityMatch records with problematic foreign key references"""
        self.foreign_key_handler.sync_problematic_facility_matches(dry_run)

    def sync_problematic_facility_list_item_fields(self, dry_run: bool = False) -> None:
        """Special method to sync FacilityListItemField records with problematic foreign key references"""
        self.foreign_key_handler.sync_problematic_facility_list_item_fields(dry_run)

    def handle_facility_list_item_constraints(self, dry_run: bool = False) -> None:
        """Handle all constraint issues for FacilityListItem and related tables"""
        self.foreign_key_handler.handle_facility_list_item_constraints(dry_run)

    def final_cleanup_sync(self, dry_run: bool = False) -> None:
        """Final cleanup: try to sync any remaining missing records"""
        if dry_run:
            logger.info("[DRY-RUN] Would perform final cleanup sync")
            return
        
        logger.info("Performing final cleanup sync for any remaining missing records...")
        
        # Get all models that were processed
        for model_key, stats in self.sync_stats.items():
            if stats['to_sync'] > 0:
                try:
                    app_label, model_name = model_key.split('.')
                    model = apps.get_model(app_label, model_name)
                    
                    # Check if there are still missing records
                    rba_uuids = self.model_repository.get_existing_uuids(model)
                    source_uuids = self.model_repository.get_source_uuids(model)
                    still_missing_uuids = source_uuids - rba_uuids
                    
                    if still_missing_uuids:
                        logger.info(f"Found {len(still_missing_uuids)} still missing records for {model_key}, attempting aggressive sync...")
                        
                        # Try aggressive sync for remaining records
                        retry_objects = self.model_repository.get_objects_by_uuids(model, still_missing_uuids)
                        if retry_objects:
                            prepared_objs = self.foreign_key_handler.prepare_objects_for_sync_aggressive(retry_objects, model)
                            
                            successful_inserts = 0
                            for obj in prepared_objs:
                                try:
                                    with transaction.atomic(using='rba'):
                                        # Resolve all dependencies aggressively
                                        self.foreign_key_handler.resolve_all_dependencies_aggressive(obj, model, dry_run)
                                        
                                        # Try to insert the object
                                        obj.save(using='rba')
                                        successful_inserts += 1
                                        
                                except Exception as e:
                                    logger.warning(f"Final cleanup failed for {obj.uuid}: {e}")
                            
                            if successful_inserts > 0:
                                logger.info(f"Final cleanup synced {successful_inserts} additional records for {model_key}")
                                sequence_updater = PostgreSQLSequenceUpdater()
                                sequence_updater.update_sequence(model, using='rba')
                            
                            # Update stats
                            final_rba_uuids = self.model_repository.get_existing_uuids(model)
                            final_missing = len(source_uuids - final_rba_uuids)
                            self.sync_stats[model_key]['total_target'] = len(final_rba_uuids)
                            self.sync_stats[model_key]['to_sync'] = final_missing
                            
                except Exception as e:
                    logger.error(f"Error during final cleanup for {model_key}: {e}")
        
        logger.info("Final cleanup sync completed")


# ============================================================================
# FACTORY PATTERN
# ============================================================================

class SyncServiceFactory:
    """Factory for creating sync services with proper dependencies"""
    
    @staticmethod
    def create_facility_list_item_sync_service() -> SyncService:
        """Create a sync service specifically for FacilityListItem circular dependencies"""
        model_repository = ModelRepository()
        validator = UUIDModelValidator()
        dependency_resolver = FacilityListItemDependencyResolver()
        foreign_key_handler = ForeignKeyHandler(model_repository)
        
        return SyncService(model_repository, validator, dependency_resolver, foreign_key_handler)


# ============================================================================
# MAIN COMMAND CLASS
# ============================================================================

class Command(BaseCommand):
    help = """Sync FacilityListItem and related tables from OS Hub (default) to RBA (rba DB) by UUID.
    
    This script is dedicated to syncing ONLY FacilityListItem and its related tables with circular dependencies.
    
    The sync includes:
    - Facility (source table that FacilityListItem depends on)
    - Source (FacilityListItem dependency)
    - FacilityListItem (main model with circular dependencies)
    - FacilityMatch (depends on FacilityListItem)
    - FacilityListItemField (depends on FacilityListItem)
    - ExtendedField (depends on FacilityListItem)
    
    The command includes comprehensive constraint handling for all related tables.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only show changes, do not apply them'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        logger.info(f"Starting FacilityListItem sync from OS Hub (default) → RBA. Dry run: {dry_run}")
        
        try:
            # FacilityListItem circular dependency sync
            logger.info("FacilityListItem circular dependency sync mode enabled")
            sync_service = SyncServiceFactory.create_facility_list_item_sync_service()
            sync_service.start_time = time.time()
            
            models_to_sync = sync_service.get_facility_list_item_models_to_sync()
            if not models_to_sync:
                raise CommandError("No models found for FacilityListItem circular dependency sync")
            
            self.__sync_facility_list_item_models(sync_service, models_to_sync, dry_run)
            sync_service.print_summary_table(dry_run)
            
        except (ValueError, LookupError) as e:
            raise CommandError(f"Invalid table format or model not found: {e}")
    
    def __sync_facility_list_item_models(self, sync_service: SyncService, models_to_sync: List[Model], dry_run: bool) -> None:
        """Sync FacilityListItem and related models with circular dependencies"""
        successful_syncs = 0
        failed_syncs = 0
        
        logger.info(f"Starting FacilityListItem circular dependency sync for {len(models_to_sync)} models")
        logger.info(f"Models to sync: {[f'{m._meta.app_label}.{m._meta.model_name}' for m in models_to_sync]}")
        
        # Note: We skip the source tables sync since we're only focusing on FacilityListItem circular dependencies
        # The models are already prioritized in the correct order by the FacilityListItemDependencyResolver
        
        for model in models_to_sync:
            try:
                logger.info(f"Syncing {model._meta.app_label}.{model._meta.model_name}...")
                sync_service.sync_model(model, dry_run)
                successful_syncs += 1
                logger.info(f"Successfully synced {model._meta.app_label}.{model._meta.model_name}")
            except Exception as e:
                failed_syncs += 1
                logger.error(f"Failed to sync {model._meta.app_label}.{model._meta.model_name}: {e}")
                
                if dry_run:
                    logger.error("Dry-run terminated due to errors.")
                    raise CommandError(f"FacilityListItem sync cannot proceed due to errors: {e}")
                else:
                    logger.info(f"Previous successful syncs ({successful_syncs} tables) are preserved. Continuing with remaining tables...")
                    continue
        
        # Update circular references after all models are synced
        try:
            logger.info("Updating circular references after FacilityListItem sync...")
            sync_service.update_circular_references(dry_run)
            logger.info("Circular reference update completed")
        except Exception as e:
            logger.error(f"Failed to update circular references: {e}")
            if dry_run:
                raise CommandError(f"Circular reference update failed: {e}")
        
        # Comprehensive constraint handling for all related tables
        try:
            logger.info("Performing comprehensive constraint handling for FacilityListItem and related tables...")
            sync_service.handle_facility_list_item_constraints(dry_run)
            logger.info("Comprehensive constraint handling completed")
        except Exception as e:
            logger.error(f"Failed to handle constraints: {e}")
            if dry_run:
                raise CommandError(f"Constraint handling failed: {e}")
        
        # Special handling for problematic facilities
        try:
            logger.info("Performing special sync for problematic facilities...")
            sync_service.sync_problematic_facilities(dry_run)
            logger.info("Problematic facilities sync completed")
        except Exception as e:
            logger.error(f"Failed to sync problematic facilities: {e}")
            if dry_run:
                raise CommandError(f"Problematic facilities sync failed: {e}")
        
        # Special handling for problematic facility list items
        try:
            logger.info("Performing special sync for problematic facility list items...")
            sync_service.sync_problematic_facility_list_items(dry_run)
            logger.info("Problematic facility list items sync completed")
        except Exception as e:
            logger.error(f"Failed to sync problematic facility list items: {e}")
            if dry_run:
                raise CommandError(f"Problematic facility list items sync failed: {e}")
        
        # Special handling for problematic facility matches
        try:
            logger.info("Performing special sync for problematic facility matches...")
            sync_service.sync_problematic_facility_matches(dry_run)
            logger.info("Problematic facility matches sync completed")
        except Exception as e:
            logger.error(f"Failed to sync problematic facility matches: {e}")
            if dry_run:
                raise CommandError(f"Problematic facility matches sync failed: {e}")
        
        # Special handling for problematic facility list item fields
        try:
            logger.info("Performing special sync for problematic facility list item fields...")
            sync_service.sync_problematic_facility_list_item_fields(dry_run)
            logger.info("Problematic facility list item fields sync completed")
        except Exception as e:
            logger.error(f"Failed to sync problematic facility list item fields: {e}")
            if dry_run:
                raise CommandError(f"Problematic facility list item fields sync failed: {e}")
        
        # Special handling for problematic ExtendedField records
        try:
            logger.info("Performing special sync for problematic ExtendedField records...")
            sync_service.sync_problematic_extended_fields(dry_run)
            logger.info("Problematic ExtendedField records sync completed")
        except Exception as e:
            logger.error(f"Failed to sync problematic ExtendedField records: {e}")
            if dry_run:
                raise CommandError(f"Problematic ExtendedField records sync failed: {e}")
        
        logger.info(f"FacilityListItem circular dependency sync completed. Successful: {successful_syncs}, Failed: {failed_syncs}")