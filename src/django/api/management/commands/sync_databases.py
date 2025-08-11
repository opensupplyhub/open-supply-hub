import logging
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from api.models.extended_field import ExtendedField
from api.models.user import User
from api.models.source import Source
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_alias import FacilityAlias
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_location import FacilityLocation
from api.models.facility.facility_activity_report import FacilityActivityReport
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_list_item import FacilityListItem
from api.models.transactions.index_facilities_new import index_facilities_new

logger = logging.getLogger(__name__)


class DatabaseSynchronizer:
    """
    Synchronizes data from DB A (source) to DB B (target) for models with
    configurable synchronization fields. Uses Django ORM for cleaner and more
    maintainable code.
    """

    # Configuration dictionary defining how Django models should be
    # synchronized.
    #
    # Structure:
    #     'ModelName': {
    #         'model': ModelClass,
    #         'sync_field': 'uuid' | 'id',
    #         'pk_type': 'auto_increment' | 'custom',
    #         'foreign_keys': {'field_name': ReferencedModel, ...},
    #         'excluded_fields': ['field1', 'field2', ...]
    #     }
    #
    # Field Descriptions:
    #     model: Django Model Class
    #         The actual Django model class to be synchronized.
    #         
    #     sync_field: String ('uuid' | 'id')
    #         The name of the field used to uniquely identify records 
    #         across databases for matching during synchronization.
    #         - 'uuid': Use UUID field for synchronization
    #         - 'id': Use primary key (ID) for synchronization
    #         
    #     pk_type: String ('auto_increment' | 'custom')
    #         Defines primary key handling during synchronization:
    #         - 'auto_increment': Standard auto-incrementing primary keys 
    #           that should be regenerated in target database
    #         - 'custom': Custom primary keys (like OS IDs) that should 
    #           be preserved during synchronization
    #     
    #     foreign_keys: Dictionary
    #         Maps foreign key field names to their referenced model classes.
    #         Some of the foreign keys don't require synchronization so they
    #         are skipped.
    #         Key structure: {'foreign_key_field_name': ReferencedModelClass}
    #         
    #     excluded_fields: List of strings
    #         Fields excluded from synchronization. These are typically:
    #         - Auto-managed Django fields
    #         - Fields handled separately in Phase 2
    #         - Fields that shouldn't be synchronized between databases
    SYNC_MODELS = {
        'User': {
            'model': User,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {},
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        },
        'Contributor': {
            'model': Contributor,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'admin': User,
            },
            'excluded_fields': [
                'embed_config',
                'embed_level',
                'created_at',
                'updated_at'
            ]
        },
        'FacilityList': {
            'model': FacilityList,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'replaces': FacilityList,
                'status_change_by': User
            },
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        },
        'Source': {
            'model': Source,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'contributor': Contributor,
                'facility_list': FacilityList
            },
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        },
        'FacilityListItem': {
            'model': FacilityListItem,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'source': Source,
            },
            'excluded_fields': [
                'facility',
                'created_at',
                'updated_at'
            ]
        },
        'Facility': {
            'model': Facility,
            'sync_field': 'id',
            'pk_type': 'custom',
            'foreign_keys': {
                'created_from': FacilityListItem
            },
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        },
        'FacilityMatch': {
            'model': FacilityMatch,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'facility_list_item': FacilityListItem,
                'facility': Facility
            },
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        },
        'FacilityLocation': {
            'model': FacilityLocation,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'created_by': User,
                'contributor': Contributor,
                'facility': Facility
            },
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        },
        'FacilityClaim': {
            'model': FacilityClaim,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'contributor': Contributor,
                'status_change_by': User,
                'parent_company': Contributor,
                'facility': Facility
            },
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        },
        'ExtendedField': {
            'model': ExtendedField,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'contributor': Contributor,
                'facility_list_item': FacilityListItem,
                'facility_claim': FacilityClaim,
                'facility': Facility
            },
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        },
        'FacilityActivityReport': {
            'model': FacilityActivityReport,
            'sync_field': 'uuid',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'reported_by_user': User,
                'reported_by_contributor': Contributor,
                'status_change_by': User,
                'facility': Facility
            },
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        },
        'FacilityAlias': {
            'model': FacilityAlias,
            'sync_field': 'os_id',
            'pk_type': 'custom',
            'foreign_keys': {
                'facility': Facility
            },
            'excluded_fields': [
                'created_at',
                'updated_at'
            ]
        }
    }

    def __init__(self, source_db_config, target_db_config, dry_run=False):
        """
        Initialize the synchronizer with database configurations.
 
        Args:
            source_db_config (dict): Configuration for source database (DB A)
            target_db_config (dict): Configuration for target database (DB B)
            dry_run (bool): If True, don't actually make changes, just log what
                           would be done
        """
        self.source_config = source_db_config
        self.target_config = target_db_config
        self.dry_run = dry_run
        self.stats = {
            'inserts': 0,
            'updates': 0,
            'errors': 0,
            'skipped': 0,
            'fk_updates': 0,
            'fk_reassignments': 0,
            'circular_reference_updates': 0
        }

        # Set up database connections
        self._setup_database_connections()

    def sync_all(self):
        """Synchronize all configured models in dependency order."""
        logger.info("Starting database synchronization...")
        logger.info(f"Source DB: {self.source_config['HOST']}:"
                   f"{self.source_config['PORT']}/{self.source_config['NAME']}")
        logger.info(f"Target DB: {self.target_config['HOST']}:"
                   f"{self.target_config['PORT']}/{self.target_config['NAME']}")
        logger.info(f"Dry run mode: {self.dry_run}")
        
        start_time = timezone.now()
        
        # Phase 1: Sync models along with avoiding circular dependencies
        # issues by skipping the fields that cause circular dependencies
        # Define sync order based on dependencies (parents first, then children)
        sync_order = [
            'User',           # No dependencies
            'Contributor',    # Depends on User
            'FacilityList',   # Self-referencing
            'Source',         # Depends on Contributor, FacilityList
            'FacilityListItem',  # Depends on Source
            'Facility',       # Depends on FacilityListItem
            'FacilityMatch',  # Depends on FacilityListItem, Facility
            'FacilityLocation',  # Depends on User, Contributor, Facility
            'FacilityClaim',  # Depends on Contributor, User, Facility
            'ExtendedField',  # Depends on Contributor, FacilityListItem,
                              # FacilityClaim, Facility
            'FacilityActivityReport',  # Depends on User, Contributor, Facility
            'FacilityAlias'   # Depends on Facility
        ]

        for model_name in sync_order:
            if model_name not in self.SYNC_MODELS:
                logger.warning(f"Model {model_name} not found in SYNC_MODELS")
                continue

            try:
                model_config = self.SYNC_MODELS[model_name]
                self.sync_model(model_name, model_config)
            except Exception as e:
                logger.error(f"Failed to sync model {model_name}: {e}")
                self.stats['errors'] += 1

        # Phase 2: Update circular references
        self.update_circular_references()

        end_time = timezone.now()
        duration = end_time - start_time

        # Log final statistics
        logger.info("=" * 60)
        logger.info("SYNCHRONIZATION COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration}")
        logger.info(f"Records inserted: {self.stats['inserts']}")
        logger.info(f"Records updated: {self.stats['updates']}")
        logger.info(f"Records skipped: {self.stats['skipped']}")
        logger.info(f"Foreign key updates: {self.stats['fk_updates']}")
        logger.info(f"Foreign key reassignments: "
                    f"{self.stats['fk_reassignments']}")
        logger.info(f"Circular Reference Updates: "
                    f"{self.stats['circular_reference_updates']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("=" * 60)

        return self.stats
        
    def _setup_database_connections(self):
        """Set up database connections for source and target."""
        # Configure source database
        settings.DATABASES['source'] = {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': self.source_config['NAME'],
            'USER': self.source_config['USER'],
            'PASSWORD': self.source_config['PASSWORD'],
            'HOST': self.source_config['HOST'],
            'PORT': self.source_config['PORT'],
        }
        
        # Configure target database
        settings.DATABASES['target'] = {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': self.target_config['NAME'],
            'USER': self.target_config['USER'],
            'PASSWORD': self.target_config['PASSWORD'],
            'HOST': self.target_config['HOST'],
            'PORT': self.target_config['PORT'],
        }

    def sync_model(self, model_name, model_config):
        """Synchronize a single model from source to target."""
        model_class = model_config['model']
        sync_field = model_config['sync_field']
        pk_type = model_config['pk_type']
        foreign_keys = model_config.get('foreign_keys', {})
        excluded_fields = model_config.get('excluded_fields', [])

        logger.info(f"Starting synchronization for model: {model_name}")
        logger.info(f"Using sync field: {sync_field}")
        logger.info(f"Foreign keys: {foreign_keys}")
        
        try:
            # Get all records from source
            source_records = list(model_class.objects.using('source').all())
            logger.info(f"Found {len(source_records)} records in source model "
                        f"{model_name}")
            
            # Process each record
            for source_record in source_records:
                try:
                    self._process_record(
                        model_class, source_record, sync_field,
                        pk_type, foreign_keys, model_name, excluded_fields
                    )
                except Exception as e:
                    logger.error(f"Error processing record in {model_name}: {e}")
                    self.stats['errors'] += 1
            
            logger.info(f"Completed synchronization for model {model_name}")
            
        except Exception as e:
            logger.error(f"Error synchronizing model {model_name}: {e}")
            self.stats['errors'] += 1

    def _process_record(self, model_class, source_record, sync_field, pk_type,
                        foreign_keys, model_name, excluded_fields):
        """Process a single record for synchronization."""
        # Check if record exists in target by sync field
        try:
            existing_record = model_class.objects.using('target').get(
                **{sync_field: getattr(source_record, sync_field)}
            )

            # Record exists, check if it needs updating
            if self._needs_update(source_record, existing_record):
                self._update_record(source_record, existing_record,
                                    foreign_keys, model_name, excluded_fields,
                                    pk_type)
                self.stats['updates'] += 1
                logger.debug(f"Updated record with {sync_field}="
                             f"{getattr(source_record, sync_field)} in {model_name}")
            else:
                self.stats['skipped'] += 1
        except model_class.DoesNotExist:
            # Record doesn't exist, insert it
            self._insert_record(model_class, source_record, sync_field, pk_type,
                                foreign_keys, model_name, excluded_fields)
            self.stats['inserts'] += 1
            logger.debug(f"Inserted record with {sync_field}="
                         f"{getattr(source_record, sync_field)} in {model_name}")

    def _needs_update(self, source_record, target_record):
        """Check if a record needs to be updated based on updated_at field."""
        if hasattr(source_record, 'updated_at') and hasattr(target_record, 'updated_at'):
            source_updated = source_record.updated_at
            target_updated = target_record.updated_at
            
            if source_updated and target_updated:
                return source_updated > target_updated
        
        return False
    
    def _insert_record(self, model_class, source_record, sync_field, pk_type,
                       foreign_keys, model_name, excluded_fields):
        """Insert a new record into the target database."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would insert record with {sync_field} "
                        f"{getattr(source_record, sync_field)} into {model_name}")
            return
        
        # Create a copy of the source record data
        record_data = self._get_record_data(source_record, pk_type, excluded_fields)
        
        # Update foreign key references
        self._update_foreign_keys_in_data(record_data, foreign_keys, model_name)
        
        # Create and save the record
        try:
            logger.info(f"Record data: {record_data}")
            new_record = model_class(**record_data)
            new_record.save(using='target')
        except Exception as e:
            logger.error(f"Error inserting record in {model_name}: {e}")
            raise
    
    def _update_record(self, source_record, target_record,
                       foreign_keys, model_name, excluded_fields, pk_type):
        """Update an existing record in the target database."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update record with sync_field "
                        f"{getattr(source_record, 'uuid')} in {model_name}")
            return
        
        # Get source record data
        record_data = self._get_record_data(source_record, pk_type,
                                            excluded_fields)
        
        # Update foreign key references
        self._update_foreign_keys_in_data(record_data, foreign_keys, model_name)
        
        # Update the target record
        for field, value in record_data.items():
            if field not in ['id', 'uuid']:  # Don't re-update primary key or UUID
                setattr(target_record, field, value)
        
        try:
            target_record.save(using='target')
        except Exception as e:
            logger.error(f"Error updating record in {model_name}: {e}")
            raise
    
    def _get_record_data(self, record, pk_type, excluded_fields=None):
        """Extract field data from a model instance."""
        if excluded_fields is None:
            excluded_fields = []
            
        data = {}
        for field in record._meta.fields:
            # Exclude auto-increment primary key.
            if field.name != 'id' or pk_type != 'auto_increment':
                # Exclude specified fields
                if field.name in excluded_fields:
                    continue
                    
                value = getattr(record, field.name)
                data[field.name] = value
        return data
    
    def _update_foreign_keys_in_data(self, record_data, foreign_keys,
                                     model_name):
        """Update foreign key references by looking up UUIDs and finding
        corresponding IDs in target DB."""
        for fk_field, referenced_model in foreign_keys.items():
            if fk_field in record_data and record_data[fk_field] is not None:
                original_fk_value = record_data[fk_field]
                
                try:
                    # Special handling for Facility foreign keys - use ID directly since it's unique
                    if referenced_model == Facility:
                        self._update_facility_foreign_key(
                            record_data, fk_field, original_fk_value, model_name
                        )
                    else:
                        # Standard UUID-based lookup for other models
                        self._update_uuid_based_foreign_key(
                            record_data, fk_field, referenced_model, 
                            original_fk_value, model_name
                        )
                        
                except Exception as e:
                    logger.error(f"Error updating FK {fk_field} in {model_name}: "
                                 f"{e}")
                    continue

    def _update_facility_foreign_key(self, record_data, fk_field, 
                                    original_fk_value, model_name):
        """Update facility foreign key using direct ID lookup since facility IDs are unique."""
        try:
            # Get the facility ID from the source record
            facility_id = original_fk_value.id
            
            # Find the corresponding facility in target DB using ID directly
            try:
                target_facility = Facility.objects.using('target').get(id=facility_id)
                logger.debug(f"Found target facility {target_facility} "
                             f"for ID {facility_id} in target DB")
            except Facility.DoesNotExist:
                logger.warning(f"Facility with ID {facility_id} not found in "
                               f"target DB for {model_name}")
                return
            
            # Update the foreign key value with the facility instance
            record_data[fk_field] = target_facility
            self.stats['fk_reassignments'] += 1
            logger.info(f"Facility FK {fk_field} in {model_name} already "
                        f"correct: {original_fk_value.id}. Reassigned "
                        f"corresponding facility from the target DB "
                        f"to avoid cross-database references.")
                
        except Exception as e:
            logger.error(f"Error updating facility FK {fk_field} in {model_name}: "
                         f"{e}")
            raise

    def _update_uuid_based_foreign_key(self, record_data, fk_field, 
                                      referenced_model, original_fk_value, model_name):
        """Update foreign key using UUID-based lookup for non-facility models."""
        # Step 1: Get the UUID of the referenced record from source DB
        try:
            referenced_source_record = (
                referenced_model.objects.using('source').get(
                    id=original_fk_value.id
                )
            )
            referenced_uuid = getattr(referenced_source_record, 'uuid')
            logger.debug(f"Found UUID {referenced_uuid} for "
                         f"{referenced_model.__name__} ID "
                         f"{original_fk_value} in source DB")
        except referenced_model.DoesNotExist:
            logger.warning(f"Referenced {referenced_model.__name__} "
                           f"with ID {original_fk_value} not found in "
                           f"source DB for {model_name}")
            return
        
        # Step 2: Find the corresponding record in target DB using UUID
        try:
            referenced_target_record = (
                referenced_model.objects.using('target').get(
                    uuid=referenced_uuid
                )
            )
            logger.debug(f"Found target record {referenced_target_record} "
                         f"for UUID {referenced_uuid} in target DB")
        except referenced_model.DoesNotExist:
            logger.warning(f"Referenced {referenced_model.__name__} "
                           f"with UUID {referenced_uuid} not found in "
                           f"target DB for {model_name}")
            return
        
        # Step 3: Update the foreign key value with the model instance
        if original_fk_value.id != referenced_target_record.id:
            record_data[fk_field] = referenced_target_record
            self.stats['fk_updates'] += 1
            logger.info(f"Updated FK {fk_field} in {model_name}: "
                        f"{original_fk_value.id} -> "
                        f"{referenced_target_record.id} "
                        f"(UUID: {referenced_uuid}). Assigned "
                        f"corresponding record from the target DB "
                        f"to avoid cross-database references.")
        else:
            record_data[fk_field] = referenced_target_record
            self.stats['fk_reassignments'] += 1
            logger.info(f"FK {fk_field} in {model_name} already "
                        f"correct: {original_fk_value}. Reassigned "
                        f"corresponding record from the target DB "
                        f"to avoid cross-database references.")

    def update_circular_references(self):
        """Update circular references after all records are synced."""
        logger.info("Updating circular references...")
        
        # Update FacilityListItem.facility references
        self.update_facility_list_item_facility()
        
        logger.info("Circular references updated!")

    def update_facility_list_item_facility(self):
        """Update FacilityListItem.facility field using UUID matching."""
        logger.info("Updating FacilityListItem.facility references...")
        
        # Get all facility list items that need facility updated
        # This includes both records with no facility and records that might need facility cleared
        list_items = FacilityListItem.objects.using('target').all()
        
        updated_count = 0
        cleared_count = 0
        errors_count = 0
        
        for list_item in list_items:
            # Find the corresponding list item in source DB
            try:
                source_list_item = (
                    FacilityListItem.objects.using('source').get(
                        uuid=list_item.uuid
                    )
                )
                
                if source_list_item.facility:
                    # Source has a facility - find the corresponding facility in target DB
                    try:
                        target_facility = Facility.objects.using('target').get(
                            id=source_list_item.facility.id
                        )
                        # Only update if the facility is different
                        if list_item.facility.id != target_facility.id:
                            list_item.facility = target_facility
                            list_item.save(using='target')
                            updated_count += 1
                            logger.debug(f"Updated FacilityListItem {list_item.id} "
                                         f"facility to {target_facility.id}")
                    except Facility.DoesNotExist:
                        logger.warning(f"Could not find Facility with ID "
                                       f"{source_list_item.facility.id} for "
                                       f"FacilityListItem {list_item.id}")
                        errors_count += 1
                else:
                    # Source has no facility - clear the facility in target if it exists
                    if list_item.facility is not None:
                        list_item.facility = None
                        list_item.save(using='target')
                        cleared_count += 1
                        logger.debug(f"Cleared facility for FacilityListItem {list_item.id} "
                                     f"(source has no facility)")
                    else:
                        logger.debug(f"FacilityListItem {list_item.id} already has no "
                                     f"facility reference")
                    
            except FacilityListItem.DoesNotExist:
                logger.warning(f"Could not find source FacilityListItem with "
                               f"UUID {list_item.uuid}")
                errors_count += 1
        
        # Update stats
        self.stats['circular_reference_updates'] += updated_count + cleared_count
        self.stats['errors'] += errors_count
        
        logger.info(f"Updated facility references for {updated_count} "
                    f"FacilityListItem records")
        logger.info(f"Cleared facility references for {cleared_count} "
                    f"FacilityListItem records")
        logger.info(f"Circular reference errors: {errors_count}")


class Command(BaseCommand):
    help = (
        'Synchronize data from OS Hub to the DB of the private instance '
        'using Django ORM. This is a one-way sync, so the data in the '
        'private instance will be updated, but not the data in OS Hub.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-host',
            type=str,
            required=True,
            help='Source database host'
        )
        parser.add_argument(
            '--source-port',
            type=int,
            default=5432,
            help='Source database port (default: 5432)'
        )
        parser.add_argument(
            '--source-name',
            type=str,
            required=True,
            help='Source database name'
        )
        parser.add_argument(
            '--source-user',
            type=str,
            required=True,
            help='Source database user'
        )
        parser.add_argument(
            '--source-password',
            type=str,
            required=True,
            help='Source database password'
        )
        parser.add_argument(
            '--target-host',
            type=str,
            required=True,
            help='Target database host'
        )
        parser.add_argument(
            '--target-port',
            type=int,
            default=5432,
            help='Target database port (default: 5432)'
        )
        parser.add_argument(
            '--target-name',
            type=str,
            required=True,
            help='Target database name'
        )
        parser.add_argument(
            '--target-user',
            type=str,
            required=True,
            help='Target database user'
        )
        parser.add_argument(
            '--target-password',
            type=str,
            required=True,
            help='Target database password'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

    def handle(self, *args, **options):
        # Setup logging.
        if options['verbose']:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        # Build database configurations.
        source_config = {
            'HOST': options['source_host'],
            'PORT': options['source_port'],
            'NAME': options['source_name'],
            'USER': options['source_user'],
            'PASSWORD': options['source_password']
        }

        target_config = {
            'HOST': options['target_host'],
            'PORT': options['target_port'],
            'NAME': options['target_name'],
            'USER': options['target_user'],
            'PASSWORD': options['target_password']
        }

        # Create and run synchronizer.
        synchronizer = DatabaseSynchronizer(
            source_config,
            target_config,
            dry_run=options['dry_run']
        )

        try:
            stats = synchronizer.sync_all()

            # Reindex the database.
            logger.info("Starting database reindexing with "
                        "index_facilities_new...")
            try:
                index_facilities_new([])
                logger.info("Database reindexing completed successfully")
            except Exception as e:
                logger.error(f"Database reindexing failed: {e}")
                raise

            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(
                        'DRY RUN COMPLETED - No changes were made to the '
                        'database'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Synchronization completed successfully!\n'
                        f'Inserted: {stats["inserts"]}\n'
                        f'Updated: {stats["updates"]}\n'
                        f'Skipped: {stats["skipped"]}\n'
                        f'FK Updates: {stats["fk_updates"]}\n'
                        f'FK Reassignments: {stats["fk_reassignments"]}\n'
                        f'Circular Reference Updates: '
                        f'{stats["circular_reference_updates"]}\n'
                        f'Errors: {stats["errors"]}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Synchronization failed: {e}')
            )
            raise CommandError(f'Synchronization failed: {e}')
