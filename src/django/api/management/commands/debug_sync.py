import logging
from django.apps import apps
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Debug sync issues"

    def handle(self, *args, **options):
        Source = apps.get_model('api', 'Source')
        Contributor = apps.get_model('api', 'Contributor')
        
        logger.info("=== DEBUGGING SYNC ISSUE ===")
        
        # Get the missing source
        source_uuids_os = set(Source.objects.using('default').values_list('uuid', flat=True))
        source_uuids_rba = set(Source.objects.using('rba').values_list('uuid', flat=True))
        missing_sources = source_uuids_os - source_uuids_rba
        
        if missing_sources:
            missing_source_uuid = list(missing_sources)[0]
            logger.info(f"Missing source UUID: {missing_source_uuid}")
            
            # Get source details from OS Hub
            source_os = Source.objects.using('default').get(uuid=missing_source_uuid)
            logger.info(f"Source in OS Hub: ID={source_os.id}, contributor_id={source_os.contributor_id}")
            
            # Check if contributor exists in OS Hub
            contributor_os = Contributor.objects.using('default').filter(id=source_os.contributor_id)
            logger.info(f"Contributor {source_os.contributor_id} exists in OS Hub: {contributor_os.exists()}")
            
            if contributor_os.exists():
                contributor_os = contributor_os.first()
                logger.info(f"Contributor in OS Hub: ID={contributor_os.id}, UUID={contributor_os.uuid}")
                
                # Check if contributor exists in RBA
                contributor_rba = Contributor.objects.using('rba').filter(uuid=contributor_os.uuid)
                logger.info(f"Contributor exists in RBA: {contributor_rba.exists()}")
                
                if contributor_rba.exists():
                    contributor_rba = contributor_rba.first()
                    logger.info(f"Contributor in RBA: ID={contributor_rba.id}, UUID={contributor_rba.uuid}")
                    
                    # Check if contributor is in synced_models
                    logger.info("=== SYNC LOGIC DEBUG ===")
                    logger.info("The issue might be in the sync logic - contributor exists in both DBs")
                    logger.info("but sync_model for Source still fails to find it")
                else:
                    logger.info("Contributor missing in RBA - this explains the sync failure")
            else:
                logger.info("Contributor missing in OS Hub - this is the root cause")
        else:
            logger.info("No missing sources found") 