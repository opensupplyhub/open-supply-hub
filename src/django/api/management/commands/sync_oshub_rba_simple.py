import logging
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Max

logger = logging.getLogger(__name__)

# Models to sync in dependency order (bottom to top)
MODELS_TO_SYNC = [
    'api.Contributor',      # No dependencies
    'api.FacilityList',     # No dependencies  
    'api.Source',           # Depends on Contributor, FacilityList
    'api.FacilityListItem', # Depends on Source (no dependency on Facility)
    'api.Facility',         # Depends on FacilityListItem (circular)
]

# Create a mapping for consistent case handling
MODEL_CASE_MAPPING = {
    'api.contributor': 'api.Contributor',
    'api.facilitylist': 'api.FacilityList', 
    'api.source': 'api.Source',
    'api.facilitylistitem': 'api.FacilityListItem',
    'api.facility': 'api.Facility',
}

class SimpleSync:
    def __init__(self):
        self.synced_models = set()
        self.circular_references = []  # [(facility_uuid, facilitylistitem_id), ...]
    
    def sync_model(self, model_name):
        """Sync a single model"""
        app_label, model_name_short = model_name.split('.')
        model = apps.get_model(app_label, model_name_short)
        
        logger.info(f"=== SYNCING {model_name} ===")
        logger.info(f"Currently synced models: {sorted(self.synced_models)}")
        
        # Get existing UUIDs in RBA
        rba_uuids = set(model.objects.using('rba').values_list('uuid', flat=True))
        
        # Get all UUIDs from OS Hub
        source_objects = model.objects.using('default').all()
        source_uuids = set(source_objects.values_list('uuid', flat=True))
        
        # Find missing UUIDs
        missing_uuids = source_uuids - rba_uuids
        logger.info(f"Found {len(missing_uuids)} missing records for {model_name}")
        
        # If no missing records, mark as synced and return
        if not missing_uuids:
            self.synced_models.add(model_name)
            logger.info(f"No missing records for {model_name}, marked as synced")
            return True
        
        # Get missing objects
        missing_objects = source_objects.filter(uuid__in=missing_uuids)
        
        # Prepare objects for sync
        prepared_objects = []
        skipped_objects = []
        
        for obj in missing_objects:
            obj_data = {}
            skip_this_object = False
            skip_reason = None
            
            logger.info(f"Processing {model_name} object: UUID={obj.uuid}, ID={obj.id}")
            
            for field in model._meta.fields:
                if field.primary_key:
                    obj_data[field.name] = getattr(obj, field.name)
                    continue
                
                value = getattr(obj, field.name)
                
                # Handle foreign keys
                if hasattr(field, 'related_model') and field.related_model and value is not None:
                    related_model = field.related_model
                    related_model_key_raw = f"{related_model._meta.app_label}.{related_model._meta.model_name}"
                    
                    # Fix case sensitivity by using the mapping
                    related_model_key = MODEL_CASE_MAPPING.get(related_model_key_raw, related_model_key_raw)
                    
                    logger.info(f"  Foreign key {field.name}: related_model={related_model_key}, value_id={value.id}, value_uuid={value.uuid}")
                    
                    # Check if this is a circular dependency
                    if (model_name == 'api.Facility' and field.name == 'created_from'):
                        # Store for later update
                        self.circular_references.append((obj.uuid, value.id))
                        obj_data[f"{field.name}_id"] = None
                        logger.info(f"  Deferring circular reference: Facility {obj.uuid} -> FacilityListItem {value.id}")
                        continue
                    
                    # Handle FacilityListItem -> Facility circular dependency
                    if (model_name == 'api.FacilityListItem' and field.name == 'facility'):
                        # Store for later update
                        self.circular_references.append((value.uuid, obj.id))  # facility_uuid, facility_list_item_id
                        obj_data[f"{field.name}_id"] = None
                        logger.info(f"  Deferring circular reference: FacilityListItem {obj.uuid} -> Facility {value.uuid}")
                        continue
                    
                    # For non-circular dependencies, check if related model is synced
                    logger.info(f"  Checking if {related_model_key} is synced...")
                    logger.info(f"  Synced models: {sorted(self.synced_models)}")
                    logger.info(f"  {related_model_key} in synced_models: {related_model_key in self.synced_models}")
                    
                    if related_model_key not in self.synced_models:
                        skip_reason = f"{related_model_key} not yet synced"
                        logger.error(f"  Cannot sync {model_name} - {skip_reason}")
                        skip_this_object = True
                        break
                    
                    # Find related object in RBA
                    try:
                        rba_obj = related_model.objects.using('rba').get(uuid=value.uuid)
                        obj_data[f"{field.name}_id"] = rba_obj.id
                        logger.info(f"  Found related object in RBA: ID={rba_obj.id}, UUID={rba_obj.uuid}")
                    except related_model.DoesNotExist:
                        skip_reason = f"Related object not found: {field.name} with UUID {value.uuid}"
                        logger.error(f"  {skip_reason}")
                        skip_this_object = True
                        break
                else:
                    # Non-FK field
                    if value is not None:
                        obj_data[field.name] = value
            
            if not skip_this_object:
                prepared_objects.append(model(**obj_data))
                logger.info(f"  Object prepared for sync: {obj.uuid}")
            else:
                skipped_objects.append((obj.uuid, skip_reason))
                logger.info(f"  Object skipped: {obj.uuid} - {skip_reason}")
        
        # Log summary
        logger.info(f"Summary for {model_name}:")
        logger.info(f"  Prepared objects: {len(prepared_objects)}")
        logger.info(f"  Skipped objects: {len(skipped_objects)}")
        
        if skipped_objects:
            logger.info("  Skipped objects details:")
            for uuid, reason in skipped_objects[:5]:  # Show first 5
                logger.info(f"    {uuid}: {reason}")
            if len(skipped_objects) > 5:
                logger.info(f"    ... and {len(skipped_objects) - 5} more")
        
        # Bulk create
        if prepared_objects:
            model.objects.using('rba').bulk_create(prepared_objects, batch_size=1000)
            logger.info(f"Created {len(prepared_objects)} records for {model_name}")
            
            # Update sequence
            self._update_sequence(model)
        
        # Only add to synced_models after successful sync
        self.synced_models.add(model_name)
        logger.info(f"Marked {model_name} as synced. Total synced models: {sorted(self.synced_models)}")
        
        return True
    
    def update_circular_references(self):
        """Update circular references after all models are synced"""
        if not self.circular_references:
            logger.info("No circular references to update")
            return
        
        logger.info(f"Updating {len(self.circular_references)} circular references...")
        
        facility_model = apps.get_model('api', 'Facility')
        facility_list_item_model = apps.get_model('api', 'FacilityListItem')
        
        updated_count = 0
        for facility_uuid, facility_list_item_id in self.circular_references:
            try:
                # Find facility in RBA
                facility = facility_model.objects.using('rba').get(uuid=facility_uuid)
                
                # Find facility list item in RBA by UUID (not ID)
                # First get the FacilityListItem from OS Hub to get its UUID
                source_facility_list_item = facility_list_item_model.objects.using('default').get(id=facility_list_item_id)
                
                # Then find it in RBA by UUID
                facility_list_item = facility_list_item_model.objects.using('rba').get(uuid=source_facility_list_item.uuid)
                
                # Update the reference - this could be either:
                # 1. Facility.created_from = FacilityListItem
                # 2. FacilityListItem.facility = Facility
                
                # Check if this is a Facility -> FacilityListItem reference
                if hasattr(facility, 'created_from'):
                    facility.created_from = facility_list_item
                    facility.save(using='rba')
                    logger.info(f"Updated Facility -> FacilityListItem: Facility {facility_uuid} -> FacilityListItem {facility_list_item_id} (UUID: {source_facility_list_item.uuid})")
                else:
                    # This must be a FacilityListItem -> Facility reference
                    facility_list_item.facility = facility
                    facility_list_item.save(using='rba')
                    logger.info(f"Updated FacilityListItem -> Facility: FacilityListItem {facility_list_item_id} -> Facility {facility_uuid}")
                
                updated_count += 1
                
            except (facility_model.DoesNotExist, facility_list_item_model.DoesNotExist) as e:
                logger.error(f"Failed to update circular reference: {e}")
        
        logger.info(f"Successfully updated {updated_count}/{len(self.circular_references)} circular references")
    
    def _update_sequence(self, model):
        """Update PostgreSQL sequence"""
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
            logger.info(f"Updated sequence {sequence_name}")
        except Exception as e:
            logger.warning(f"Failed to update sequence: {e}")


class Command(BaseCommand):
    help = "Simple sync from OS Hub to RBA with proper dependency handling"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            logger.info("DRY RUN MODE - no changes will be made")
        
        sync = SimpleSync()
        
        # First pass: sync all models in dependency order
        for model_name in MODELS_TO_SYNC:
            if not dry_run:
                if not sync.sync_model(model_name):
                    logger.error(f"Failed to sync {model_name}")
                    return
            else:
                logger.info(f"[DRY RUN] Would sync {model_name}")
        
        # Second pass: update circular references
        if not dry_run:
            sync.update_circular_references()
        else:
            logger.info(f"[DRY RUN] Would update {len(sync.circular_references)} circular references")
        
        logger.info("Sync completed successfully!") 