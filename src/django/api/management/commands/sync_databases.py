import logging
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from api.models.extended_field import ExtendedField
from api.models.user import User
from api.models.source import Source
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_alias import FacilityAlias
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_location import FacilityLocation
from api.models.facility.facility_activity_report import FacilityActivityReport
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_list_item import FacilityListItem

logger = logging.getLogger(__name__)


class DatabaseSynchronizer:
    """
    Synchronizes data from DB A (source) to DB B (target) for models with UUID fields.
    Uses Django ORM for cleaner and more maintainable code.
    """

    # Models to synchronize with their configuration
    SYNC_MODELS = {
        'User': {
            'model': User,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {}
        },
        'Contributor': {
            'model': Contributor,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'admin_id': 'User',
                'embed_config_id': 'EmbedConfig'  # Not in sync list, but need to track
            }
        },
        'Source': {
            'model': Source,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'contributor_id': 'Contributor',
                'facility_list_id': 'FacilityList'
            }
        },
        'FacilityList': {
            'model': FacilityList,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'replaces_id': 'FacilityList'  # Self-referencing
            }
        },
        'FacilityListItem': {
            'model': FacilityListItem,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'source_id': 'Source',
                'facility_id': 'Facility'
            }
        },
        'FacilityClaim': {
            'model': FacilityClaim,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'contributor_id': 'Contributor',
                'facility_id': 'Facility',
                'status_change_by_id': 'User',
                'parent_company_id': 'Contributor'
            }
        },
        'ExtendedField': {
            'model': ExtendedField,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'contributor_id': 'Contributor',
                'facility_id': 'Facility',
                'facility_list_item_id': 'FacilityListItem',
                'facility_claim_id': 'FacilityClaim'
            }
        },
        'FacilityLocation': {
            'model': FacilityLocation,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'facility_id': 'Facility',
                'created_by_id': 'User',
                'contributor_id': 'Contributor'
            }
        },
        'FacilityActivityReport': {
            'model': FacilityActivityReport,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'facility_id': 'Facility',
                'reported_by_user_id': 'User',
                'reported_by_contributor_id': 'Contributor'
            }
        },
        'FacilityMatch': {
            'model': FacilityMatch,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'auto_increment',
            'foreign_keys': {
                'facility_list_item_id': 'FacilityListItem',
                'facility_id': 'Facility'
            }
        },
        # Facility models with native primary keys
        'Facility': {
            'model': Facility,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'native',  # Uses OS ID as primary key
            'foreign_keys': {
                'created_from_id': 'FacilityListItem'
            }
        },
        'FacilityIndex': {
            'model': FacilityIndex,
            'uuid_field': 'uuid',
            'pk_field': 'id',
            'pk_type': 'native',  # Uses OS ID as primary key
            'foreign_keys': {}
        },
        'FacilityAlias': {
            'model': FacilityAlias,
            'uuid_field': 'uuid',
            'pk_field': 'os_id',  # Uses os_id as primary key
            'pk_type': 'native',
            'foreign_keys': {
                'facility_id': 'Facility'
            }
        }
    }

    def __init__(self, source_db_config, target_db_config, dry_run=False):
        """
        Initialize the synchronizer with database configurations.
 
        Args:
            source_db_config (dict): Configuration for source database (DB A)
            target_db_config (dict): Configuration for target database (DB B)
            dry_run (bool): If True, don't actually make changes, just log what would be done
        """
        self.source_config = source_db_config
        self.target_config = target_db_config
        self.dry_run = dry_run
        self.stats = {
            'inserts': 0,
            'updates': 0,
            'errors': 0,
            'skipped': 0,
            'pk_conflicts_resolved': 0,
            'fk_updates': 0
        }
        
        # Track primary key mappings for foreign key updates
        self.pk_mappings = defaultdict(dict)  # {model_name: {old_pk: new_pk}}
        
        # Set up database connections
        self._setup_database_connections()
        
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

    def get_next_auto_increment_value(self, model_class, pk_field, using='target'):
        """Get the next available auto-increment value for a model."""
        try:
            max_pk = model_class.objects.using(using).aggregate(
                max_pk=Q(**{pk_field: Q(pk__isnull=False)})
            )['max_pk']
            return (max_pk or 0) + 1
        except Exception as e:
            logger.warning(f"Error getting next auto-increment value for {model_class.__name__}: {e}")
            return 1

    def sync_model(self, model_name, model_config):
        """Synchronize a single model from source to target."""
        model_class = model_config['model']
        uuid_field = model_config['uuid_field']
        pk_field = model_config['pk_field']
        pk_type = model_config['pk_type']
        foreign_keys = model_config.get('foreign_keys', {})

        logger.info(f"Starting synchronization for model: {model_name}")
        logger.info(f"UUID field: {uuid_field}, PK field: {pk_field}, PK type: {pk_type}")
        logger.info(f"Foreign keys: {foreign_keys}")
        
        try:
            # Get all records from source
            source_records = list(model_class.objects.using('source').all())
            logger.info(f"Found {len(source_records)} records in source model {model_name}")
            
            # Process each record
            for source_record in source_records:
                try:
                    self._process_record(
                        model_class, source_record, uuid_field, pk_field, 
                        pk_type, foreign_keys, model_name
                    )
                except Exception as e:
                    logger.error(f"Error processing record in {model_name}: {e}")
                    self.stats['errors'] += 1
            
            logger.info(f"Completed synchronization for model {model_name}")
            
        except Exception as e:
            logger.error(f"Error synchronizing model {model_name}: {e}")
            self.stats['errors'] += 1
    
    def _process_record(self, model_class, source_record, uuid_field, pk_field, pk_type, foreign_keys, model_name):
        """Process a single record for synchronization."""
        # Check if record exists in target by UUID
        try:
            existing_record = model_class.objects.using('target').get(
                **{uuid_field: getattr(source_record, uuid_field)}
            )
            
            # Record exists, check if it needs updating
            if self._needs_update(source_record, existing_record):
                self._update_record(model_class, source_record, existing_record, foreign_keys, model_name)
                self.stats['updates'] += 1
                logger.debug(f"Updated record with {uuid_field}={getattr(source_record, uuid_field)} in {model_name}")
            else:
                self.stats['skipped'] += 1
                
        except model_class.DoesNotExist:
            # Record doesn't exist, insert it
            self._insert_record(model_class, source_record, uuid_field, pk_field, pk_type, foreign_keys, model_name)
            self.stats['inserts'] += 1
            logger.debug(f"Inserted record with {uuid_field}={getattr(source_record, uuid_field)} in {model_name}")
    
    def _needs_update(self, source_record, target_record):
        """Check if a record needs to be updated based on updated_at field."""
        if hasattr(source_record, 'updated_at') and hasattr(target_record, 'updated_at'):
            source_updated = source_record.updated_at
            target_updated = target_record.updated_at
            
            if source_updated and target_updated:
                return source_updated > target_updated
        
        return False
    
    def _insert_record(self, model_class, source_record, uuid_field, pk_field, pk_type, foreign_keys, model_name):
        """Insert a new record into the target database."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would insert record with UUID {getattr(source_record, uuid_field)} into {model_name}")
            return
        
        # Create a copy of the source record data
        record_data = self._get_record_data(source_record)
        original_pk = record_data.get(pk_field)
        
        # Handle primary key conflicts for auto-increment fields
        if pk_type == 'auto_increment':
            # Check if there's a primary key conflict
            if original_pk is not None:
                try:
                    model_class.objects.using('target').get(**{pk_field: original_pk})
                    # PK conflict - get next available value and update the record
                    next_pk = self.get_next_auto_increment_value(model_class, pk_field)
                    record_data[pk_field] = next_pk
                    self.stats['pk_conflicts_resolved'] += 1
                    logger.info(f"Resolved PK conflict in {model_name}: {pk_field}={original_pk} -> {pk_field}={next_pk}")
                    
                    # Store the mapping for foreign key updates
                    self.pk_mappings[model_name][original_pk] = next_pk
                except model_class.DoesNotExist:
                    # No conflict, keep original PK
                    pass
        
        # Update foreign key references
        self._update_foreign_keys_in_data(record_data, foreign_keys, model_name)
        
        # Create and save the record
        try:
            new_record = model_class(**record_data)
            new_record.save(using='target')
        except Exception as e:
            logger.error(f"Error inserting record in {model_name}: {e}")
            raise
    
    def _update_record(self, model_class, source_record, target_record, foreign_keys, model_name):
        """Update an existing record in the target database."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update record with UUID {getattr(source_record, 'uuid')} in {model_name}")
            return
        
        # Get source record data
        record_data = self._get_record_data(source_record)
        
        # Update foreign key references
        self._update_foreign_keys_in_data(record_data, foreign_keys, model_name)
        
        # Update the target record
        for field, value in record_data.items():
            if field not in ['id', 'uuid']:  # Don't update primary key or UUID
                setattr(target_record, field, value)
        
        try:
            target_record.save(using='target')
        except Exception as e:
            logger.error(f"Error updating record in {model_name}: {e}")
            raise
    
    def _get_record_data(self, record):
        """Extract field data from a model instance."""
        data = {}
        for field in record._meta.fields:
            if field.name not in ['id', 'uuid'] or field.name == record._meta.pk.name:
                # Include primary key field but exclude auto-generated UUID
                value = getattr(record, field.name)
                if value is not None or not field.null:
                    data[field.name] = value
        return data
    
    def _update_foreign_keys_in_data(self, record_data, foreign_keys, model_name):
        """Update foreign key references in record data based on primary key mappings."""
        for fk_field, referenced_model in foreign_keys.items():
            if fk_field in record_data and record_data[fk_field] is not None:
                old_fk_value = record_data[fk_field]
                
                # Check if we have a mapping for this foreign key
                if referenced_model in self.pk_mappings:
                    if old_fk_value in self.pk_mappings[referenced_model]:
                        new_fk_value = self.pk_mappings[referenced_model][old_fk_value]
                        record_data[fk_field] = new_fk_value
                        self.stats['fk_updates'] += 1
                        logger.info(f"Updated FK {fk_field} in {model_name}: {old_fk_value} -> {new_fk_value}")
    
    def sync_all(self):
        """Synchronize all configured models in dependency order."""
        logger.info("Starting database synchronization...")
        logger.info(f"Source DB: {self.source_config['HOST']}:{self.source_config['PORT']}/{self.source_config['NAME']}")
        logger.info(f"Target DB: {self.target_config['HOST']}:{self.target_config['PORT']}/{self.target_config['NAME']}")
        logger.info(f"Dry run mode: {self.dry_run}")
        
        start_time = timezone.now()
        
        # Define sync order based on dependencies (parents first, then children)
        sync_order = [
            'User',           # No dependencies
            'Contributor',    # Depends on User
            'Source',         # Depends on Contributor, FacilityList
            'FacilityList',   # Self-referencing
            'FacilityListItem', # Depends on Source
            'FacilityClaim',  # Depends on Contributor, User
            'ExtendedField',  # Depends on Contributor, FacilityListItem, FacilityClaim
            'FacilityLocation', # Depends on User, Contributor
            'FacilityActivityReport', # Depends on User, Contributor
            'FacilityMatch',  # Depends on FacilityListItem
            'Facility',       # Depends on FacilityListItem
            'FacilityIndex',  # Depends on Facility
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
        logger.info(f"Primary key conflicts resolved: {self.stats['pk_conflicts_resolved']}")
        logger.info(f"Foreign key updates: {self.stats['fk_updates']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("=" * 60)

        return self.stats


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
        # Setup logging
        if options['verbose']:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        
        # Build database configurations
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
        
        # Create and run synchronizer
        synchronizer = DatabaseSynchronizer(
            source_config, 
            target_config, 
            dry_run=options['dry_run']
        )
        
        try:
            stats = synchronizer.sync_all()
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(
                        'DRY RUN COMPLETED - No changes were made to the database'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Synchronization completed successfully! '
                        f'Inserted: {stats["inserts"]}, Updated: {stats["updates"]}, '
                        f'Skipped: {stats["skipped"]}, PK Conflicts Resolved: {stats["pk_conflicts_resolved"]}, '
                        f'FK Updates: {stats["fk_updates"]}, Errors: {stats["errors"]}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Synchronization failed: {e}')
            )
            raise CommandError(f'Synchronization failed: {e}') 