import logging
import os
from datetime import datetime
import hashlib
import hmac

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.db.models import EmailField
from django.db import connections

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

logger = logging.getLogger(__name__)


class DatabaseSynchronizer:
    '''
    Synchronizes data from source database to target database for models with
    configurable synchronization fields. Uses Django ORM for cleaner and more
    maintainable code.
    '''

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
    #     model: Django model class
    #     The actual Django model class to be synchronized.
    #
    #     sync_field: String ('uuid' | 'id')
    #         The name of the field used to uniquely identify records
    #         across databases for matching during synchronization:
    #         - 'uuid': Use UUID field for synchronization.
    #         - 'id': Use primary key (ID) for synchronization.
    #
    #     pk_type: String ('auto_increment' | 'custom')
    #         Defines primary key handling during synchronization:
    #         - 'auto_increment': Standard auto-incrementing primary keys
    #           that should be regenerated in target database.
    #         - 'custom': Custom primary keys (like OS IDs) that should
    #           be preserved during synchronization.
    #
    #     foreign_keys: Dictionary
    #         Maps foreign key field names to their referenced model classes.
    #         Some of the foreign keys don't require synchronization so they
    #         are skipped.
    #         Key structure: {'foreign_key_field_name': ReferencedModelClass}
    #
    #     excluded_fields: List of strings
    #         Fields excluded from synchronization. These are typically:
    #         - Auto-managed Django fields.
    #         - Fields handled separately in Phase 2 (circular references).
    #         - Fields that shouldn't be synchronized between databases.
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
                'updated_at',
                'partner_fields'
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

    def __init__(self, source_db_config, chunk_size=1000,
                 dry_run=False, last_run_path=None,
                 connection_refresh_interval=54000):
        '''
        Initialize the synchronizer with database configurations.

        Args:
            source_db_config (dict): Configuration for source database.
            chunk_size (int): Chunk size for processing records from
                a table in source database.
            dry_run (bool): If True, don't actually make changes, just log what
                would be done.
            last_run_path (str): Path to store last run metadata for each
                model.
            connection_refresh_interval (int): Seconds before refreshing
                database connections to avoid RDS Proxy 24-hour timeout
                (default: 54000 = 15 hours).
        '''
        self.__source_config = source_db_config
        self.__chunk_size = chunk_size
        self.__dry_run = dry_run
        self.__last_run_path = last_run_path or '/tmp/sync_databases_last_run'
        self.__connection_refresh_interval = connection_refresh_interval

        # Ensure the last run directory exists.
        os.makedirs(self.__last_run_path, exist_ok=True)

        self.__stats = {
            'inserts': 0,
            'updates': 0,
            'errors': 0,
            'fk_updates': 0,
            'fk_reassignments': 0,
            'circular_reference_updates': 0
        }

        # Track session start time at the synchronizer level to properly
        # handle connection refreshes across multiple models.
        self.__session_start_time = None

        # Set up database connection.
        self.__setup_source_database_connection()

    def sync_all(self):
        '''Synchronize all configured models in dependency order.'''
        logger.info('Starting database synchronization...')
        logger.info(f'Source DB: {self.__source_config["HOST"]}:'
                    f'{self.__source_config["PORT"]}/'
                    f'{self.__source_config["NAME"]}')
        logger.info(f'Dry run mode: {self.__dry_run}')

        start_time = timezone.now()
        # Initialize session start time for connection refresh tracking.
        self.__session_start_time = timezone.now()

        # Phase 1: Sync models along with avoiding circular dependencies
        # issues by skipping the fields that cause them.

        # Define sync order based on dependencies (parents first, then
        # children).
        sync_order = [
            'User',  # No dependencies.
            'Contributor',  # Depends on User.
            'FacilityList',  # Self-referencing.
            'Source',  # Depends on Contributor, FacilityList.
            'FacilityListItem',  # Depends on Source.
            'Facility',  # Depends on FacilityListItem.
            'FacilityMatch',  # Depends on FacilityListItem, Facility.
            'FacilityLocation',  # Depends on User, Contributor, Facility.
            'FacilityClaim',  # Depends on Contributor, User, Facility.
            'ExtendedField',  # Depends on Contributor, FacilityListItem,
                              # FacilityClaim, Facility.
            'FacilityActivityReport',  # Depends on User, Contributor,
                                       # Facility.
            'FacilityAlias',  # Depends on Facility.
        ]

        for model_name in sync_order:
            if model_name not in self.SYNC_MODELS:
                logger.warning(f'Model {model_name} not found in SYNC_MODELS.')
                continue

            try:
                model_config = self.SYNC_MODELS[model_name]
                self.__sync_model(model_name, model_config)
            except Exception as e:
                logger.exception(f'Failed to sync model {model_name}: {e}.')
                self.__stats['errors'] += 1

        # Phase 2: Update circular references.
        self.__update_circular_references()

        end_time = timezone.now()
        duration = end_time - start_time

        # Log final statistics.
        logger.info('=' * 60)
        logger.info('SYNCHRONIZATION COMPLETED')
        logger.info('=' * 60)
        logger.info(f'Duration: {duration}')
        logger.info(f'Records inserted: {self.__stats["inserts"]}')
        logger.info(f'Records updated: {self.__stats["updates"]}')
        logger.info(f'Foreign key updates: {self.__stats["fk_updates"]}')
        logger.info(f'Foreign key reassignments: '
                    f'{self.__stats["fk_reassignments"]}')
        logger.info(f'Circular Reference Updates: '
                    f'{self.__stats["circular_reference_updates"]}')
        logger.info(f'Errors: {self.__stats["errors"]}')
        logger.info('=' * 60)

    def __sync_model(self, model_name, model_config):
        '''Synchronize a single model from source to target.'''
        model_class = model_config['model']
        sync_field = model_config['sync_field']
        pk_type = model_config['pk_type']
        foreign_keys = model_config.get('foreign_keys', {})
        excluded_fields = model_config.get('excluded_fields', [])

        logger.info(f'Starting synchronization for model: {model_name}')
        logger.info(f'Using sync field: {sync_field}')
        logger.info(f'Foreign keys: {foreign_keys}')

        # Get the last run timestamp for this model.
        last_run = self.__get_last_run_timestamp(model_name)
        logger.info(f'Last run timestamp for {model_name}: {last_run}')

        try:
            # Process records in sessions with connection refresh.
            last_processed_timestamp = None
            record_count = 0
            continue_processing = True

            while continue_processing:
                # Get only records updated since last run.
                current_start = (last_processed_timestamp
                                 if last_processed_timestamp else last_run)
                source_records = model_class.objects.using('source').filter(
                    updated_at__gt=current_start
                ).order_by('updated_at').iterator(
                    chunk_size=self.__chunk_size)

                logger.info(
                    f'Created iterator for {model_name} starting from '
                    f'{current_start} with chunk size '
                    f'{self.__chunk_size}.'
                )

                records_in_session = 0
                need_connection_refresh = False

                for source_record in source_records:
                    try:
                        self.__process_record(
                            model_class, source_record, sync_field,
                            pk_type, foreign_keys, model_name, excluded_fields
                        )

                        # Track the timestamp of the last processed record.
                        last_processed_timestamp = source_record.updated_at
                        record_count += 1
                        records_in_session += 1

                        # Save timestamp after each chunk.
                        if (record_count % self.__chunk_size == 0 and
                                last_processed_timestamp):
                            if self.__dry_run:
                                logger.info(
                                    f'[DRY RUN] Would save checkpoint '
                                    f'after {record_count} records for '
                                    f'{model_name}: '
                                    f'{last_processed_timestamp}.'
                                )
                            else:
                                self.__save_last_run_timestamp(
                                    model_name, last_processed_timestamp
                                )
                                logger.info(
                                    f'Saved checkpoint after '
                                    f'{record_count} records for '
                                    f'{model_name}: '
                                    f'{last_processed_timestamp}.'
                                )

                            # Check if we need to refresh connections.
                            elapsed_time = (
                                timezone.now() - self.__session_start_time
                            ).total_seconds()
                            logger.info(f'Elapsed time of the current '
                                        f'database session: {elapsed_time}.')
                            refresh_interval = \
                                self.__connection_refresh_interval
                            if elapsed_time >= refresh_interval:
                                need_connection_refresh = True
                                logger.info(
                                    f'Connection has been open for '
                                    f'{elapsed_time/3600:.1f} hours. '
                                    f'Will refresh after current batch.'
                                )
                                break  # Break to refresh connections.

                    except Exception as e:
                        logger.exception('Error processing record in '
                                         f'{model_name}: {e}.')
                        self.__stats['errors'] += 1

                # Check if we processed any records in this session.
                if records_in_session == 0:
                    # No more records to process.
                    continue_processing = False
                elif need_connection_refresh:
                    # Refresh connections and continue with next session.
                    if not self.__dry_run:
                        self.__refresh_database_connections()
                        self.__session_start_time = timezone.now()
                        logger.info(
                            f'Resuming from timestamp: '
                            f'{last_processed_timestamp}'
                        )
                else:
                    # Finished all records without needing refresh.
                    continue_processing = False

            # Final save after all processing completes.
            if last_processed_timestamp:
                if self.__dry_run:
                    logger.info(f'[DRY RUN] Would save final timestamp '
                                f'for {model_name}: '
                                f'{last_processed_timestamp}.')
                else:
                    self.__save_last_run_timestamp(model_name,
                                                   last_processed_timestamp)
                    logger.info(f'Saved final timestamp for {model_name}: '
                                f'{last_processed_timestamp}.')

            logger.info(f'Completed synchronization for model {model_name}.')

        except Exception as e:
            logger.exception(f'Error synchronizing model {model_name}: {e}.')
            self.__stats['errors'] += 1

    def __process_record(self, model_class, source_record, sync_field, pk_type,
                         foreign_keys, model_name, excluded_fields):
        '''Process a single record for synchronization.'''
        # Check if record exists in target by sync field
        try:
            logger.info(f'Starting processing record with {sync_field}='
                        f'{getattr(source_record, sync_field)} in '
                        f'{model_name}.')
            existing_record = model_class.objects.get(
                **{sync_field: getattr(source_record, sync_field)}
            )

            # Record exists - always update it (since incremental sync already
            # filtered by updated_at).
            self.__update_record(source_record, existing_record,
                                 foreign_keys, model_name, excluded_fields,
                                 pk_type, sync_field)
            self.__stats['updates'] += 1
            logger.info(f'Updated record with {sync_field}='
                        f'{getattr(source_record, sync_field)} in '
                        f'{model_name}.')

        except model_class.DoesNotExist:
            # Record doesn't exist - insert it.
            self.__insert_record(model_class, source_record, sync_field,
                                 pk_type, foreign_keys, model_name,
                                 excluded_fields)
            self.__stats['inserts'] += 1
            logger.info(f'Inserted record with {sync_field}='
                        f'{getattr(source_record, sync_field)} in '
                        f'{model_name}.')

    def __insert_record(self, model_class, source_record, sync_field, pk_type,
                        foreign_keys, model_name, excluded_fields):
        '''Insert a new record into the target database.'''
        if self.__dry_run:
            logger.info(f'[DRY RUN] Would insert record with {sync_field} '
                        f'{getattr(source_record, sync_field)} into '
                        f'{model_name}.')
            return

        # Create a copy of the source record data.
        record_data = self.__get_record_data(
            source_record, pk_type,
            excluded_fields
        )

        # Update foreign key references.
        self.__update_foreign_keys_in_data(
            record_data, foreign_keys, model_name
        )

        # Create and save the record.
        try:
            new_record = model_class(**record_data)
            new_record.save()
        except Exception as e:
            logger.exception(f'Error inserting record in {model_name}: {e}.')
            raise

    def __update_record(self, source_record, target_record,
                        foreign_keys, model_name, excluded_fields, pk_type,
                        sync_field):
        '''Update an existing record in the target database.'''
        if self.__dry_run:
            logger.info(f'[DRY RUN] Would update record with sync_field '
                        f'{getattr(source_record, sync_field)} in '
                        f'{model_name}.')
            return

        # Get source record data.
        record_data = self.__get_record_data(
            source_record, pk_type, excluded_fields
        )

        # Update foreign key references.
        self.__update_foreign_keys_in_data(
            record_data,
            foreign_keys,
            model_name
        )

        # Update the target record.
        for field, value in record_data.items():
            # Don't re-update primary key or UUID.
            if field not in ['id', 'uuid']:
                setattr(target_record, field, value)

        try:
            target_record.save()
        except Exception as e:
            logger.exception(f'Error updating record in {model_name}: {e}.')
            raise

    @staticmethod
    def __get_record_data(record, pk_type, excluded_fields=None):
        '''Extract field data from a model instance.'''
        if excluded_fields is None:
            excluded_fields = []

        data = {}
        for field in record._meta.fields:
            # Exclude auto-increment primary key.
            if field.name != 'id' or pk_type != 'auto_increment':
                # Exclude specified fields.
                if field.name in excluded_fields:
                    continue

                value = getattr(record, field.name)

                # Anonymize EmailField values using MD5 hash of random text.
                if isinstance(field, EmailField) and value:
                    value = DatabaseSynchronizer.__anonymize_email(value)

                data[field.name] = value
        return data

    @staticmethod
    def __anonymize_email(email):
        '''
        Anonymize email using deterministic HMAC-SHA256.
        Same input always produces same output, preserving data stability.
        '''
        if not email or not isinstance(email, str):
            return email

        # Use Django secret key as salt for consistency
        secret = getattr(settings, 'EMAIL_ANONYMIZATION_SECRET')
        if not secret:
            raise ValueError('EMAIL_ANONYMIZATION_SECRET must be configured.')

        # Normalize email to lowercase for consistency.
        normalized_email = email.lower().strip()

        # Generate deterministic hash using HMAC-SHA256.
        hashed = hmac.new(
            secret.encode('utf-8'),
            normalized_email.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Use consistent domain and truncate hash for readability.
        return f'{hashed[:32]}@anonymized.example'

    def __update_foreign_keys_in_data(
            self, record_data, foreign_keys, model_name):
        '''
        Update foreign key references by looking up UUIDs and finding
        corresponding IDs in target DB.
        '''
        for fk_field, referenced_model in foreign_keys.items():
            if fk_field in record_data and record_data[fk_field] is not None:
                original_fk_value = record_data[fk_field]

                try:
                    # Special handling for Facility foreign keys - use ID
                    # directly since it's unique.
                    if referenced_model == Facility:
                        self.__update_facility_foreign_key(
                            record_data, fk_field, original_fk_value,
                            model_name
                        )
                    else:
                        # Standard UUID-based lookup for other models.
                        self.__update_uuid_based_foreign_key(
                            record_data, fk_field, referenced_model,
                            original_fk_value, model_name
                        )

                except Exception as e:
                    logger.exception(
                        f'Error updating FK {fk_field} in {model_name}: {e}.'
                    )
                    continue

    def __update_facility_foreign_key(
            self, record_data, fk_field, original_fk_value, model_name):
        '''
        Update facility foreign key using direct ID lookup since facility IDs
        are unique.
        '''
        try:
            # Get the facility ID from the source record.
            facility_id = original_fk_value.id

            # Find the corresponding facility in target DB using ID directly.
            try:
                target_facility = Facility.objects.get(id=facility_id)
                logger.info(f'Found target facility {target_facility} '
                            f'for ID {facility_id} in target DB.')
            except Facility.DoesNotExist:
                logger.warning(f'Facility with ID {facility_id} not found in '
                               f'target DB for {model_name}.')
                return

            # Update the foreign key value with the facility instance.
            record_data[fk_field] = target_facility
            self.__stats['fk_reassignments'] += 1
            logger.info(f'Facility FK {fk_field} in {model_name} already '
                        f'correct: {original_fk_value.id}. Reassigned '
                        f'corresponding facility from the target DB '
                        f'to avoid cross-database references.')

        except Exception as e:
            logger.exception(
                f'Error updating facility FK {fk_field} in {model_name}: {e}.'
            )
            raise

    def __update_uuid_based_foreign_key(
            self, record_data, fk_field, referenced_model, original_fk_value,
            model_name):
        '''
        Update foreign key using UUID-based lookup for non-facility models.
        '''
        # Step 1: Get the UUID of the referenced record from source DB.
        try:
            referenced_source_record = (
                referenced_model.objects.using('source').get(
                    id=original_fk_value.id
                )
            )
            referenced_uuid = getattr(referenced_source_record, 'uuid')
            logger.info(f'Found UUID {referenced_uuid} for '
                        f'{referenced_model.__name__} ID '
                        f'{original_fk_value} in source DB.')
        except referenced_model.DoesNotExist:
            logger.warning(f'Referenced {referenced_model.__name__} '
                           f'with ID {original_fk_value} not found in '
                           f'source DB for {model_name}.')
            return

        # Step 2: Find the corresponding record in target DB using UUID.
        try:
            referenced_target_record = (
                referenced_model.objects.get(
                    uuid=referenced_uuid
                )
            )
            logger.info(f'Found target record {referenced_target_record} '
                        f'for UUID {referenced_uuid} in target DB.')
        except referenced_model.DoesNotExist:
            logger.warning(f'Referenced {referenced_model.__name__} '
                           f'with UUID {referenced_uuid} not found in '
                           f'target DB for {model_name}.')
            return

        # Step 3: Update the foreign key value with the model instance.
        if original_fk_value.id != referenced_target_record.id:
            record_data[fk_field] = referenced_target_record
            self.__stats['fk_updates'] += 1
            logger.info(f'Updated FK {fk_field} in {model_name}: '
                        f'{original_fk_value.id} -> '
                        f'{referenced_target_record.id} '
                        f'(UUID: {referenced_uuid}). Assigned '
                        f'corresponding record from the target DB '
                        f'to avoid cross-database references.')
        else:
            record_data[fk_field] = referenced_target_record
            self.__stats['fk_reassignments'] += 1
            logger.info(f'FK {fk_field} in {model_name} already '
                        f'correct: {original_fk_value}. Reassigned '
                        f'corresponding record from the target DB '
                        f'to avoid cross-database references.')

    def __update_circular_references(self):
        '''Update circular references after all records are synced.'''

        logger.info('Updating circular references...')

        # Update FacilityListItem.facility references.
        self.__update_facility_list_item_facility()

        logger.info('Circular references updated!')

    def __update_facility_list_item_facility(self):
        '''Update FacilityListItem.facility field using UUID matching.'''
        if self.__dry_run:
            logger.info('[DRY RUN] Would update FacilityListItem.facility '
                        'circular references.')
            return

        logger.info('Updating FacilityListItem.facility references...')

        # Use a separate timestamp for facility updates.
        last_run = self.__get_last_run_timestamp(
            'FacilityListItem', 'facility_updates'
        )
        logger.info('Last run timestamp for FacilityListItem facility '
                    f'updates: {last_run}')

        # Process records in sessions with connection refresh.
        updated_count = 0
        cleared_count = 0
        errors_count = 0
        record_count = 0
        last_processed_timestamp = None
        continue_processing = True

        try:
            while continue_processing:
                # Query source records by updated_at.
                current_start = (last_processed_timestamp
                                 if last_processed_timestamp else last_run)
                source_list_items = \
                    FacilityListItem.objects.using('source').filter(
                        updated_at__gt=current_start
                    ).order_by('updated_at').iterator(
                        chunk_size=self.__chunk_size)

                logger.info(
                    'Created iterator for FacilityListItem facility '
                    f'updates starting from {current_start} with '
                    f'chunk_size={self.__chunk_size}.'
                )

                records_in_session = 0
                need_connection_refresh = False

                for source_list_item in source_list_items:
                    # Find the corresponding list item in target DB by UUID.
                    try:
                        target_list_item = FacilityListItem.objects.get(
                            uuid=source_list_item.uuid
                        )

                        if source_list_item.facility:
                            # Source has a facility - find the corresponding
                            # facility in target DB.
                            try:
                                target_facility = Facility.objects.get(
                                    id=source_list_item.facility.id
                                )
                                # Only update if the facility is different.
                                if (target_list_item.facility is None or
                                        target_list_item.facility.id !=
                                        target_facility.id):
                                    target_list_item.facility = target_facility
                                    target_list_item.save()
                                    updated_count += 1
                                    logger.info(
                                        'Updated FacilityListItem '
                                        f'{target_list_item.id} facility '
                                        f'to {target_facility.id}.'
                                    )
                            except Facility.DoesNotExist:
                                logger.warning(
                                    'Could not find Facility with ID '
                                    f'{source_list_item.facility.id} '
                                    'for FacilityListItem '
                                    f'{target_list_item.id}.'
                                )
                                errors_count += 1
                        else:
                            # Source has no facility - clear the facility in
                            # target if it exists.
                            if target_list_item.facility is not None:
                                target_list_item.facility = None
                                target_list_item.save()
                                cleared_count += 1
                                logger.info('Cleared facility for '
                                            f'FacilityListItem '
                                            f'{target_list_item.id} '
                                            '(source has no facility).')
                            else:
                                logger.info(
                                    f'FacilityListItem '
                                    f'{target_list_item.id} '
                                    'already has no facility reference.'
                                )

                        # Track the timestamp of the last processed record.
                        last_processed_timestamp = source_list_item.updated_at
                        record_count += 1
                        records_in_session += 1

                        # Save timestamp after each chunk.
                        if (record_count % self.__chunk_size == 0 and
                                last_processed_timestamp):
                            self.__save_last_run_timestamp(
                                'FacilityListItem',
                                last_processed_timestamp,
                                'facility_updates'
                            )
                            logger.info(
                                f'Saved checkpoint after {record_count} '
                                f'facility updates: '
                                f'{last_processed_timestamp}.'
                            )

                            # Check if we need to refresh connections.
                            elapsed_time = (
                                timezone.now() - self.__session_start_time
                            ).total_seconds()
                            logger.info(f'Elapsed time of the current '
                                        f'database session: {elapsed_time}.')
                            refresh_interval = \
                                self.__connection_refresh_interval
                            if elapsed_time >= refresh_interval:
                                need_connection_refresh = True
                                logger.info(
                                    f'Connection has been open for '
                                    f'{elapsed_time/3600:.1f} hours. '
                                    f'Will refresh after current batch.'
                                )
                                break  # Break to refresh connections.

                    except FacilityListItem.DoesNotExist:
                        logger.warning(
                            'Could not find target FacilityListItem '
                            f'with UUID {source_list_item.uuid}.'
                        )
                        errors_count += 1

                # Check if we processed any records in this session.
                if records_in_session == 0:
                    # No more records to process.
                    continue_processing = False
                elif need_connection_refresh:
                    # Refresh connections and continue with next session.
                    if not self.__dry_run:
                        self.__refresh_database_connections()
                        self.__session_start_time = timezone.now()
                        logger.info(
                            f'Resuming facility updates from timestamp: '
                            f'{last_processed_timestamp}'
                        )
                else:
                    # Finished all records without needing refresh.
                    continue_processing = False

        except Exception as e:
            logger.exception(
                f'Error during facility list item facility updates: {e}.'
            )
            self.__stats['errors'] += 1

        # Update statistics.
        self.__stats['circular_reference_updates'] += (
            updated_count + cleared_count
        )
        self.__stats['errors'] += errors_count

        logger.info(f'Updated facility references for {updated_count} '
                    f'FacilityListItem records.')
        logger.info(f'Cleared facility references for {cleared_count} '
                    f'FacilityListItem records.')
        logger.info(f'Circular reference errors: {errors_count}.')

        # Final save after loop completes.
        if last_processed_timestamp:
            self.__save_last_run_timestamp(
                'FacilityListItem',
                last_processed_timestamp,
                'facility_updates'
            )
            logger.info('Saved final facility updates timestamp: '
                        f'{last_processed_timestamp}.')

    def __setup_source_database_connection(self):
        '''Set up database connection for source.'''
        # Configure source database.
        settings.DATABASES['source'] = {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': self.__source_config['NAME'],
            'USER': self.__source_config['USER'],
            'PASSWORD': self.__source_config['PASSWORD'],
            'HOST': self.__source_config['HOST'],
            'PORT': self.__source_config['PORT'],
        }

    def __get_last_run_timestamp(self, model_name, suffix=''):
        '''Get the last run timestamp for a specific model.'''
        filename = f'{model_name.lower()}_last_run'
        if suffix:
            filename += f'_{suffix}'
        last_run_file = os.path.join(self.__last_run_path, filename)

        if os.path.exists(last_run_file):
            try:
                with open(last_run_file, 'r') as f:
                    timestamp_str = f.read().strip()
                    return datetime.fromisoformat(timestamp_str)
            except (ValueError, IOError) as e:
                logger.warning(
                    'Could not read last run timestamp '
                    f'for {model_name}: {e}.')

        # Return a very old date if no last run file exists.
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

    def __save_last_run_timestamp(self, model_name, timestamp, suffix=''):
        '''Save the last run timestamp for a specific model.'''
        filename = f'{model_name.lower()}_last_run'
        if suffix:
            filename += f'_{suffix}'
        last_run_file = os.path.join(self.__last_run_path, filename)

        try:
            with open(last_run_file, 'w') as f:
                f.write(timestamp.isoformat())
            logger.info(f'Saved last run timestamp '
                        f'for {model_name}: {timestamp}.')
        except IOError as e:
            logger.exception(
                f'Could not save last run timestamp for {model_name}: {e}.'
            )

    @staticmethod
    def __refresh_database_connections():
        '''Close all database connections to avoid RDS Proxy timeouts.'''
        logger.info('Refreshing database connections to avoid 24-hour '
                    'RDS Proxy timeout...')
        connections.close_all()
        logger.info('Database connections closed. They will reopen on next '
                    'query.')


class Command(BaseCommand):
    help = (
        'Synchronize data from OS Hub to the DB of the private instance '
        'using Django ORM. This is a one-way sync, so the data in the '
        'private instance will be updated, but not the data in OS Hub.'
        'To run this command, you need to provide the source database '
        'credentials, the database from which the data is being synced '
        'from. The private instance database credentials will be taken '
        'automatically from settings.DATABASES["default"].'
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
            '--chunk-size',
            type=int,
            default=1000,
            help='Chunk size for processing records from a table in source '
                 'database (default: 1000)'
        )
        parser.add_argument(
            '--connection-refresh-interval',
            type=int,
            default=54000,
            help='Seconds before refreshing database connections to avoid '
                 'RDS Proxy 24-hour timeout (default: 54000 = 15 hours)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--last-run-path',
            type=str,
            default='/tmp/sync_databases_last_run',
            help='Path to store last run metadata for incremental syncs '
                 '(default: /tmp/sync_databases_last_run)'
        )

    def handle(self, *args, **options):
        # Build database configurations.
        source_config = {
            'HOST': options['source_host'],
            'PORT': options['source_port'],
            'NAME': options['source_name'],
            'USER': options['source_user'],
            'PASSWORD': options['source_password']
        }

        try:
            # Create and run synchronizer.
            synchronizer = DatabaseSynchronizer(
                source_config,
                chunk_size=options['chunk_size'],
                dry_run=options['dry_run'],
                last_run_path=options['last_run_path'],
                connection_refresh_interval=options[
                    'connection_refresh_interval'
                ]
            )
            synchronizer.sync_all()

            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(
                        'DRY RUN COMPLETED - No changes were made to the '
                        'database.'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Synchronization failed: {e}')
            )
            raise CommandError(f'Synchronization failed: {e}')
