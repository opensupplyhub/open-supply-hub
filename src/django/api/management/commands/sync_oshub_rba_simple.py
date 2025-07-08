import logging
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db import connections
from django.db.models import Max
from api.models.facility.facility_list_item import FacilityListItem

logger = logging.getLogger(__name__)

class FastSync:
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the sync state for a fresh run"""
        self.synced_models = set()
        self.os_hub_created_from_ids = set()
        self.os_hub_created_from_uuids = set()
    
    def sync_facilities_only(self):
        """Step 1-4: Sync facilities with temporary NULL created_from_id"""
        logger.info("=== PHASE 1: SYNCING FACILITIES ===")
        
        facility_model = apps.get_model('api', 'Facility')
        
        # Get all facility UUIDs from both databases
        os_hub_facility_uuids = set(facility_model.objects.using('default').values_list('uuid', flat=True))
        rba_facility_uuids = set(facility_model.objects.using('rba').values_list('uuid', flat=True))
        
        # Find facilities that exist in OS Hub but not in RBA
        missing_facility_uuids = os_hub_facility_uuids - rba_facility_uuids
        
        logger.info(f"Found {len(missing_facility_uuids)} facilities to sync")
        
        if not missing_facility_uuids:
            logger.info("No facilities to sync")
            return True
        
        # Get missing facilities from OS Hub
        missing_facilities = facility_model.objects.using('default').filter(uuid__in=missing_facility_uuids)

        logger.info(f"@@@ List of facilities {missing_facilities} to sync")

        
        # Prepare facilities for sync with NULL created_from_id
        prepared_facilities = []
        for facility in missing_facilities:
            facility_data = {}
            
            # Copy all fields except created_from_id
            for field in facility_model._meta.fields:
                if field.name == 'created_from':
                    # Set to NULL temporarily
                    facility_data[f"{field.name}_id"] = None
                elif field.primary_key:
                    facility_data[field.name] = getattr(facility, field.name)
                else:
                    value = getattr(facility, field.name)
                    if value is not None:
                        facility_data[field.name] = value
            
            prepared_facilities.append(facility_model(**facility_data))
        
        # Bulk create facilities
        if prepared_facilities:
            facility_model.objects.using('rba').bulk_create(prepared_facilities, batch_size=1000)
            logger.info(f"Created {len(prepared_facilities)} facilities in RBA")

            logger.info(f"### List of facilities {prepared_facilities} to sync")

            # missing_facilities is what we have in OS Hub but not in RBA
            # self.os_hub_created_from_ids = set(missing_facilities.values_list('created_from_id', flat=True))
            # ------------------------------------------------------------
            missing_created_from_ids = missing_facilities.values_list('created_from_id', flat=True)
            self.os_hub_created_from_ids = set(zip(missing_facility_uuids, missing_created_from_ids))
            for f_uuid, listitem_id in self.os_hub_created_from_ids:
                fli = FacilityListItem.objects.using('default').get(id=listitem_id)
                self.os_hub_created_from_uuids.add((f_uuid, str(fli.uuid)))
            logger.info(f"~~~ List of OS Hub created_from_ids {self.os_hub_created_from_ids} to sync")
            # ------------------------------------------------------------

            # prepared_facilities is what we have in RBA
            for facility_rba in prepared_facilities:
                logger.info(f"@@@ Facility RBA created_from_id {facility_rba.created_from_id} to sync")
            
            # Update sequence
            self._update_sequence(facility_model)
        
        return True

    def copy_missing_facility_list_items_from_oshub(self):
        needed_uuids = {fli_uuid for _, fli_uuid in self.os_hub_created_from_uuids}

        with connections['rba'].cursor() as cursor:
            cursor.execute("SELECT uuid FROM api_facilitylistitem WHERE uuid IN %s", [tuple(needed_uuids)])
            existing_uuids = {str(row[0]) for row in cursor.fetchall()}

        to_copy = needed_uuids - existing_uuids
        logger.info(f"Copying {len(to_copy)} list items from OSHub to RBA")

        for fli_uuid in to_copy:
            fli = FacilityListItem.objects.using('default').get(uuid=fli_uuid)

            # Create in RBA with same ID
            FacilityListItem.objects.using('rba').create(
                uuid=fli.uuid,
                source=fli.source,
                row_index=fli.row_index,
                raw_data=fli.raw_data,
                raw_json=fli.raw_json,
                name=fli.name,
                address=fli.address,
                country_code=fli.country_code,
                facility=None  # set later if needed
            )

    
    def update_facility_created_from_references_fast(self):
        """Step 5: Update facility.created_from_id references using SQL"""
        logger.info("=== PHASE 2: UPDATING FACILITY CREATED_FROM REFERENCES (FAST) ===")

        
        # Use a single SQL UPDATE with JOIN instead of nested loops
        # PROBABLE not working as expected, need to check
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE api_facility f_rba
                SET created_from_id = fli_rba.id
                FROM api_facility f_oshub
                JOIN api_facilitylistitem fli_oshub ON f_oshub.created_from_id = fli_oshub.id
                JOIN api_facilitylistitem fli_rba ON fli_oshub.uuid = fli_rba.uuid
                WHERE f_oshub.uuid = f_rba.uuid
                AND f_rba.created_from_id IS NULL
                AND fli_rba.id IS NOT NULL
                """
            )
            updated_count = cursor.rowcount
        
        logger.info(f"Updated {updated_count} Facility.created_from_id references using SQL")

        # Get facilities with NULL created_from_id on RBA
        # ------------------------------------------------------------
        with connections['rba'].cursor() as cursor:
            cursor.execute("SELECT id, uuid, name FROM api_facility WHERE created_from_id IS NULL")
            rows = cursor.fetchall()

            if not rows:
                logger.info("No facilities with NULL created_from_id found.")

            logger.info(f"Found {len(rows)} facilities with NULL created_from_id:")
            for row in rows:
                logger.info(f"Facility ID={row[0]}, UUID={row[1]}, Name={row[2]}")
        logger.info(f"~~~ List of OS Hub created_from_ids {self.os_hub_created_from_ids} to sync")
        # ------------------------------------------------------------

        self.copy_missing_facility_list_items_from_oshub()
        self.update_facility_list_item_facility_references_fast()

        '''
        with connections['rba'].cursor() as cursor:
            for facility_uuid, created_from_id in self.os_hub_created_from_ids:
                cursor.execute(
                """
                    UPDATE api_facility
                    SET created_from_id = %s
                    WHERE uuid = %s
                    AND created_from_id IS NULL
                """, 
                [created_from_id, facility_uuid]
            )
        '''

        return updated_count
    
    def sync_facility_list_items_fast(self):
        """Step 6: Sync remaining FacilityListItems using bulk operations"""
        logger.info("=== PHASE 3: SYNCING FACILITY LIST ITEMS (FAST) ===")
        
        facility_list_item_model = apps.get_model('api', 'FacilityListItem')
        facility_model = apps.get_model('api', 'Facility')
        
        # Get all FacilityListItem UUIDs from both databases
        os_hub_fli_uuids = set(facility_list_item_model.objects.using('default').values_list('uuid', flat=True))
        rba_fli_uuids = set(facility_list_item_model.objects.using('rba').values_list('uuid', flat=True))
        
        # Find FacilityListItems that exist in OS Hub but not in RBA
        missing_fli_uuids = os_hub_fli_uuids - rba_fli_uuids
        
        logger.info(f"Found {len(missing_fli_uuids)} FacilityListItems to sync")
        
        if not missing_fli_uuids:
            logger.info("No FacilityListItems to sync")
            return True
        
        # Get missing FacilityListItems from OS Hub
        missing_flis = facility_list_item_model.objects.using('default').filter(uuid__in=missing_fli_uuids)
        
        # Prepare FacilityListItems for sync with NULL facility_id initially
        prepared_flis = []
        for fli in missing_flis:
            fli_data = {}
            
            # Copy all fields except facility_id (set to NULL initially)
            for field in facility_list_item_model._meta.fields:
                if field.name == 'facility':
                    # Set to NULL temporarily
                    fli_data[f"{field.name}_id"] = None
                elif field.primary_key:
                    # fli_data[field.name] = getattr(fli, field.name)
                    continue
                else:
                    value = getattr(fli, field.name)
                    if value is not None:
                        fli_data[field.name] = value
            
            prepared_flis.append(facility_list_item_model(**fli_data))
        
        # Bulk create FacilityListItems
        if prepared_flis:
            facility_list_item_model.objects.using('rba').bulk_create(prepared_flis, batch_size=1000)
            logger.info(f"Created {len(prepared_flis)} FacilityListItems in RBA")
            
            # Update sequence
            self._update_sequence(facility_list_item_model)
        
        return True
    
    def update_facility_list_item_facility_references_fast(self):
        """Update FacilityListItem.facility_id references using SQL"""
        logger.info("=== PHASE 4: UPDATING FACILITY LIST ITEM FACILITY REFERENCES (FAST) ===")
        
        # Use a single SQL UPDATE with JOIN
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE api_facilitylistitem fli_rba
                SET facility_id = f_rba.id
                FROM api_facilitylistitem fli_oshub
                JOIN api_facility f_oshub ON fli_oshub.facility_id = f_oshub.id
                JOIN api_facility f_rba ON f_oshub.uuid = f_rba.uuid
                WHERE fli_oshub.uuid = fli_rba.uuid
                AND fli_rba.facility_id IS NULL
                AND fli_oshub.facility_id IS NOT NULL
            """)
            updated_count = cursor.rowcount
        
        logger.info(f"Updated {updated_count} FacilityListItem.facility_id references using SQL")
        return updated_count
    
    def sync_other_models_fast(self):
        """Sync other models using bulk operations"""
        logger.info("=== SYNCING OTHER MODELS (FAST) ===")
        
        models_to_sync = [
            'api.Contributor',
            'api.FacilityList', 
            'api.Source',
        ]
        
        for model_name in models_to_sync:
            app_label, model_name_short = model_name.split('.')
            model = apps.get_model(app_label, model_name_short)
            
            logger.info(f"Syncing {model_name}...")
            
            # Get existing UUIDs in RBA
            rba_uuids = set(model.objects.using('rba').values_list('uuid', flat=True))
            
            # Get all UUIDs from OS Hub
            source_objects = model.objects.using('default').all()
            source_uuids = set(source_objects.values_list('uuid', flat=True))
            
            # Find missing UUIDs
            missing_uuids = source_uuids - rba_uuids
            logger.info(f"Found {len(missing_uuids)} missing records for {model_name}")
            
            if not missing_uuids:
                continue
            
            # Get missing objects and prepare for sync
            missing_objects = source_objects.filter(uuid__in=missing_uuids)
            prepared_objects = []
            
            for obj in missing_objects:
                obj_data = {}
                
                for field in model._meta.fields:
                    if field.primary_key:
                        obj_data[field.name] = getattr(obj, field.name)
                        continue
                    
                    value = getattr(obj, field.name)
                    
                    # Handle foreign keys - set to NULL initially for simplicity
                    if hasattr(field, 'related_model') and field.related_model and value is not None:
                        # For now, set to NULL to avoid complex lookups
                        obj_data[f"{field.name}_id"] = None
                    else:
                        # Non-FK field
                        if value is not None:
                            obj_data[field.name] = value
                
                prepared_objects.append(model(**obj_data))
            
            # Bulk create
            if prepared_objects:
                model.objects.using('rba').bulk_create(prepared_objects, batch_size=1000)
                logger.info(f"Created {len(prepared_objects)} records for {model_name}")
                
                # Update sequence
                self._update_sequence(model)
        
        return True
    
    def verify_facility_consistency(self):
        """Verify that facility_id references in FacilityListItems are consistent"""
        logger.info("=== VERIFYING FACILITY CONSISTENCY ===")
        
        # Check for FacilityListItems with facility_id that don't exist
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*)
                FROM api_facilitylistitem fli
                LEFT JOIN api_facility f ON fli.facility_id = f.id
                WHERE fli.facility_id IS NOT NULL AND f.id IS NULL
            """)
            inconsistent_count = cursor.fetchone()[0]
        
        if inconsistent_count > 0:
            logger.warning(f"Found {inconsistent_count} FacilityListItems with invalid facility_id references")
        else:
            logger.info("All FacilityListItem facility_id references are consistent")
        
        return inconsistent_count == 0
    
    def _update_sequence(self, model):
        """Update PostgreSQL sequence"""
        try:
            table_name = model._meta.db_table
            pk_field = model._meta.pk.name
            pk_field_type = model._meta.pk.get_internal_type()
            
            # Skip sequence update for text primary keys (like Facility.id)
            if pk_field_type in ['CharField', 'TextField']:
                logger.info(f"Skipping sequence update for text primary key: {pk_field}")
                return
                
            sequence_name = f"{table_name}_{pk_field}_seq"
            
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT setval('{sequence_name}', 
                        COALESCE((SELECT MAX({pk_field}) FROM {table_name}), 1)
                    );
                """)
            logger.info(f"Updated sequence {sequence_name}")
        except Exception as e:
            logger.warning(f"Failed to update sequence: {e}")


class Command(BaseCommand):
    help = "Fast sync from OS Hub to RBA with bulk operations and SQL updates"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes'
        )
        parser.add_argument(
            '--reset-state',
            action='store_true',
            help='Reset sync state (this happens automatically on each run)'
        )
        parser.add_argument(
            '--skip-verification',
            action='store_true',
            help='Skip facility consistency verification'
        )
    
    def handle(self, *args, **options):
        reset_state = options['reset_state']
        
        logger.info("=== STARTING FAST SYNC FROM OS HUB TO RBA ===")
        
        sync = FastSync()
        
        if reset_state:
            sync.reset()
            logger.info("Sync state manually reset")
        else:
            logger.info("Sync state initialized and reset (automatic)")
        
        try:
            sync.sync_other_models_fast()
            sync.sync_facilities_only()
            sync.copy_missing_facility_list_items_from_oshub()
            sync.sync_facility_list_items_fast()
            sync.update_facility_list_item_facility_references_fast()  # optional, but good
            sync.update_facility_created_from_references_fast()

            logger.info("Fast sync completed successfully!")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise 