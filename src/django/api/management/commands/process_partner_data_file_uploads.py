import logging

from django.core.management.base import BaseCommand

from api.models.partner_data_file_upload import PartnerDataFileUpload
from api.partner_data_file_upload.processing.processor import (
    PartnerDataFileUploadProcessor,
)
from api.partner_data_file_upload.sheets.client import GoogleSheetClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Process queued partner Google Sheets and create pending moderation "
        "events for partner-field production location updates."
    )

    def add_arguments(self, parser):
        parser.add_argument("--queue_entry_uuid", type=str, required=False)

    def handle(self, *args, **options):
        queue_entry_uuid = options.get("queue_entry_uuid")
        logger.info(
            "Starting partner data file upload command."
            + (
                f" queue_entry_uuid={queue_entry_uuid}"
                if queue_entry_uuid
                else ""
            )
        )

        rows = (
            PartnerDataFileUpload.objects
            .select_related("contributor")
            .filter(status=PartnerDataFileUpload.Status.PROCESSING)
        )
        if queue_entry_uuid:
            rows = rows.filter(uuid=queue_entry_uuid)

        if not rows.exists():
            logger.info(
                "No partner data files in PROCESSING status found. "
                "Processing completed."
            )
            return

        upload_count = rows.count()
        logger.info(
            "Found %s partner data file upload(s) in PROCESSING status.",
            upload_count,
        )

        processor = PartnerDataFileUploadProcessor(
            GoogleSheetClient.from_env()
        )
        uploads_succeeded = 0
        uploads_failed = 0
        for queue_row in rows:
            if processor.process(queue_row):
                uploads_succeeded += 1
            else:
                uploads_failed += 1

        logger.info(
            "Partner data file upload command processing completed. "
            "uploads_succeeded=%s uploads_failed=%s uploads_total=%s",
            uploads_succeeded,
            uploads_failed,
            upload_count,
        )
