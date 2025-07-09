import logging
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection, connections
from api.models.facility.facility_list_item import FacilityListItem

logger = logging.getLogger(__name__)

class FastSync:
    def __init__(self):
        self.reset()

    def reset(self):
        self.synced_models = set()
        self.os_hub_created_from_ids = set()
        self.os_hub_created_from_uuids = set()

    def sync_other_models_fast(self):
        logger.info("=== PHASE 1: SYNCING OTHER MODELS ===")
        models_to_sync = ['api.Contributor', 'api.FacilityList', 'api.Source']
        for model_path in models_to_sync:
            app_label, model_name = model_path.split('.')
            model = apps.get_model(app_label, model_name)
            source_qs = model.objects.using('default').all()
            target_uuids = set(model.objects.using('rba').values_list('uuid', flat=True))
            to_create = [obj for obj in source_qs if obj.uuid not in target_uuids]
            if to_create:
                model.objects.using('rba').bulk_create(to_create, batch_size=1000)
                self._update_sequence(model)

    def sync_facility_list_items_fast(self):
        logger.info("=== PHASE 2: SYNCING FACILITY LIST ITEMS ===")
        model = apps.get_model('api', 'FacilityListItem')
        source_uuids = set(model.objects.using('default').values_list('uuid', flat=True))
        target_uuids = set(model.objects.using('rba').values_list('uuid', flat=True))
        missing_uuids = source_uuids - target_uuids
        if not missing_uuids:
            return
        missing_flis = model.objects.using('default').filter(uuid__in=missing_uuids)
        prepared = []
        for fli in missing_flis:
            fli_data = {}
            for field in model._meta.fields:
                if field.name == 'facility':
                    fli_data['facility_id'] = None
                elif field.primary_key:
                    continue
                else:
                    value = getattr(fli, field.name)
                    if value is not None:
                        fli_data[field.name] = value
            prepared.append(model(**fli_data))
        model.objects.using('rba').bulk_create(prepared, batch_size=1000)
        self._update_sequence(model)

    def sync_facilities_only(self):
        logger.info("=== PHASE 3: SYNCING FACILITIES ===")
        facility_model = apps.get_model('api', 'Facility')
        os_hub_facility_uuids = set(facility_model.objects.using('default').values_list('uuid', flat=True))
        rba_facility_uuids = set(facility_model.objects.using('rba').values_list('uuid', flat=True))
        missing_facility_uuids = os_hub_facility_uuids - rba_facility_uuids
        logger.info(f"Found {len(missing_facility_uuids)} facilities to sync")
        if not missing_facility_uuids:
            return
        missing_facilities = facility_model.objects.using('default').filter(uuid__in=missing_facility_uuids)
        prepared_facilities = []
        for facility in missing_facilities:
            facility_data = {}
            for field in facility_model._meta.fields:
                if field.name == 'created_from':
                    facility_data['created_from_id'] = None
                elif field.primary_key:
                    facility_data[field.name] = getattr(facility, field.name)
                else:
                    value = getattr(facility, field.name)
                    if value is not None:
                        facility_data[field.name] = value
            prepared_facilities.append(facility_model(**facility_data))
            self.os_hub_created_from_ids.add((facility.uuid, facility.created_from_id))
            if facility.created_from_id:
                try:
                    fli = FacilityListItem.objects.using('default').get(id=facility.created_from_id)
                    self.os_hub_created_from_uuids.add((facility.uuid, str(fli.uuid)))
                except FacilityListItem.DoesNotExist:
                    logger.warning(f"Missing FLI id {facility.created_from_id} in OS Hub")
        facility_model.objects.using('rba').bulk_create(prepared_facilities, batch_size=1000)
        self._update_sequence(facility_model)

    def update_facility_created_from_references_fast(self):
        logger.info("=== PHASE 4: UPDATING FACILITY.created_from REFERENCES ===")
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE api_facility f_rba
                SET created_from_id = fli_rba.id
                FROM api_facility f_oshub
                JOIN api_facilitylistitem fli_oshub ON f_oshub.created_from_id = fli_oshub.id
                JOIN api_facilitylistitem fli_rba ON fli_oshub.uuid = fli_rba.uuid
                WHERE f_oshub.uuid = f_rba.uuid
                AND f_rba.created_from_id IS NULL
                AND fli_rba.id IS NOT NULL
            """)

    def update_facility_list_item_facility_references_fast(self):
        logger.info("=== PHASE 5: UPDATING FLI.facility REFERENCES ===")
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

    def _update_sequence(self, model):
        try:
            table_name = model._meta.db_table
            pk_field = model._meta.pk.name
            pk_type = model._meta.pk.get_internal_type()
            if pk_type in ['CharField', 'TextField']:
                return
            sequence_name = f"{table_name}_{pk_field}_seq"
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT setval('{sequence_name}', 
                        COALESCE((SELECT MAX({pk_field}) FROM {table_name}), 1)
                    );
                """)
        except Exception as e:
            logger.warning(f"Failed to update sequence: {e}")

class Command(BaseCommand):
    help = "Fast sync from OS Hub to RBA with correct FK resolution order"

    def handle(self, *args, **options):
        sync = FastSync()
        try:
            sync.reset()
            sync.sync_other_models_fast()
            sync.sync_facility_list_items_fast()
            sync.sync_facilities_only()
            sync.update_facility_created_from_references_fast()
            sync.update_facility_list_item_facility_references_fast()
            logger.info("Fast sync completed successfully!")
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise
