import logging

from django.core.management.base import BaseCommand
from api.models.facility_download_limit import FacilityDownloadLimit

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        FacilityDownloadLimit.objects.update_expired_limits()
        logger.info("Updated expired facility download limits.")
