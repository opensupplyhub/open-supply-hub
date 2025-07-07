import logging
from django.apps import apps
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Debug sync issues"

    def handle(self, *args, **options):
        Facility = apps.get_model('api', 'Facility')
        
        logger.info("=== CHECKING PROBLEMATIC FACILITIES ===")
        
        # The 6 facilities that had null created_from_id
        problematic_facility_ids = [
            'CN202518210SB6G', 'UA2025182Y2NDKZ', 'IN2025182ETWEDA', 
            'CN2025182W0CZJY', 'IT2025182QXF5D6', 'FR20251828HP6PQ'
        ]
        
        null_count = 0
        for facility_id in problematic_facility_ids:
            try:
                facility = Facility.objects.using('rba').get(id=facility_id)
                logger.info(f"Facility {facility_id}: created_from_id = {facility.created_from_id}")
                
                if facility.created_from_id is None:
                    null_count += 1
                    logger.error(f"  ❌ STILL NULL!")
                else:
                    logger.info(f"  ✅ FIXED!")
                        
            except Facility.DoesNotExist:
                logger.error(f"Facility {facility_id} NOT FOUND in RBA")
        
        logger.info(f"\n=== SUMMARY ===")
        logger.info(f"Facilities with null created_from_id: {null_count}/{len(problematic_facility_ids)}")
        
        if null_count == 0:
            logger.info("🎉 ALL PROBLEMATIC FACILITIES FIXED!")
        else:
            logger.error(f"❌ {null_count} facilities still have null created_from_id") 