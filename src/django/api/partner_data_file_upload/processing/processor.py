import logging
import time
from typing import Dict, Optional

from django.utils import timezone

from api.models.partner_data_file_upload import PartnerDataFileUpload
from api.moderation_event_actions.creation.location_contribution.location_contribution import (  # noqa: E501
    LocationContribution,
)
from api.moderation_event_actions.creation.moderation_event_creator import (
    ModerationEventCreator,
)
from api.partner_data_file_upload.errors import format_upload_processing_error
from api.partner_data_file_upload.parsing.parser import PartnerFieldSheetParser
from api.partner_data_file_upload.parsing.types import SheetProcessingContext
from api.partner_data_file_upload.processing.event_creator import (
    PartnerPatchModerationEventCreator,
)
from api.partner_data_file_upload.sheets.client import GoogleSheetClient

logger = logging.getLogger(__name__)


class PartnerDataFileUploadProcessor:
    def __init__(
        self,
        sheets_client: GoogleSheetClient,
        me_creator: Optional[ModerationEventCreator] = None,
        row_processing_delay_seconds: float = 0,
    ):
        self.sheets_client = sheets_client
        self.row_processing_delay_seconds = row_processing_delay_seconds
        self.event_creator = PartnerPatchModerationEventCreator(
            me_creator or ModerationEventCreator(LocationContribution())
        )

    def process(self, queue_row: PartnerDataFileUpload) -> bool:
        logger.info(
            "Starting partner data file upload processing for uuid=%s "
            "contributor_id=%s",
            queue_row.uuid,
            queue_row.contributor_id,
        )
        try:
            context = self._build_context(queue_row)
            row_stats = self._process_rows(queue_row, context)
            self._mark_queue_row_processed(queue_row)
            logger.info(
                "Partner data file upload uuid=%s processing completed "
                "successfully. rows_succeeded=%s rows_failed=%s "
                "rows_skipped_empty=%s rows_skipped_existing=%s",
                queue_row.uuid,
                row_stats["rows_succeeded"],
                row_stats["rows_failed"],
                row_stats["rows_skipped_empty"],
                row_stats["rows_skipped_existing"],
            )
            return True
        except Exception as error:
            queue_row.status = PartnerDataFileUpload.Status.FAILED
            queue_row.processing_error = format_upload_processing_error(error)
            queue_row.save(
                update_fields=["status", "processing_error", "updated_at"]
            )
            logger.error(
                "Partner data file upload uuid=%s processing failed: %s",
                queue_row.uuid,
                queue_row.processing_error,
            )
            logger.exception(
                "Failed processing partner data file upload uuid=%s",
                queue_row.uuid,
            )
            return False

    def _build_context(
        self,
        queue_row: PartnerDataFileUpload,
    ) -> SheetProcessingContext:
        workbook = self.sheets_client.load_workbook(
            queue_row.google_drive_file_link
        )
        header_map = PartnerFieldSheetParser.build_header_map(workbook.headers)
        data_columns = PartnerFieldSheetParser.validate_headers(header_map)
        column_mappings, partner_fields_by_name = (
            PartnerFieldSheetParser.build_column_mappings(
                data_columns,
                queue_row.contributor,
            )
        )
        tracking_columns = self.sheets_client.ensure_tracking_columns(
            workbook
        )
        cols_count = max(
            len(workbook.headers),
            tracking_columns["error"] + 1,
            tracking_columns["moderation_id"] + 1,
        )

        return SheetProcessingContext(
            workbook=workbook,
            data_columns=data_columns,
            header_map=header_map,
            column_mappings=column_mappings,
            partner_fields_by_name=partner_fields_by_name,
            tracking_columns=tracking_columns,
            cols_count=cols_count,
        )

    def _process_rows(
        self,
        queue_row: PartnerDataFileUpload,
        context: SheetProcessingContext,
    ) -> Dict[str, int]:
        error_col = context.tracking_columns["error"]
        moderation_id_col = context.tracking_columns["moderation_id"]
        row_stats = {
            "rows_succeeded": 0,
            "rows_failed": 0,
            "rows_skipped_empty": 0,
            "rows_skipped_existing": 0,
        }

        logger.info(
            "Processing sheet rows for upload uuid=%s. data_rows=%s",
            queue_row.uuid,
            len(context.workbook.rows),
        )

        for row_idx, row_values in enumerate(context.workbook.rows, start=2):
            record = PartnerFieldSheetParser.build_record_from_row(
                row_values,
                context.header_map,
            )
            if not PartnerFieldSheetParser.row_has_values(record):
                row_stats["rows_skipped_empty"] += 1
                continue

            if PartnerFieldSheetParser.row_has_existing_outcome(record):
                row_stats["rows_skipped_existing"] += 1
                logger.info(
                    "Row %s skipped for upload uuid=%s because it already has "
                    "a moderation_id or error value. os_id=%s",
                    row_idx,
                    queue_row.uuid,
                    record.get("os_id"),
                )
                continue

            row_started_at = time.monotonic()
            try:
                moderation_id = self.event_creator.create(
                    queue_row.contributor,
                    record,
                    context.column_mappings,
                )
                self.sheets_client.mark_row(
                    context.workbook,
                    row_idx,
                    context.cols_count,
                    error_col,
                    moderation_id_col,
                    "",
                    moderation_id,
                )
                row_stats["rows_succeeded"] += 1
                logger.info(
                    "Row %s processed successfully for upload uuid=%s. "
                    "os_id=%s moderation_id=%s",
                    row_idx,
                    queue_row.uuid,
                    record.get("os_id"),
                    moderation_id,
                )
            except Exception as error:
                self.sheets_client.mark_row(
                    context.workbook,
                    row_idx,
                    context.cols_count,
                    error_col,
                    moderation_id_col,
                    str(error),
                    "",
                )
                row_stats["rows_failed"] += 1
                logger.error(
                    "Row %s failed for upload uuid=%s. os_id=%s error=%s",
                    row_idx,
                    queue_row.uuid,
                    record.get("os_id"),
                    str(error),
                )

            self._wait_before_next_row(row_started_at)

        logger.info(
            "Finished sheet row processing for upload uuid=%s. "
            "rows_succeeded=%s rows_failed=%s rows_skipped_empty=%s "
            "rows_skipped_existing=%s",
            queue_row.uuid,
            row_stats["rows_succeeded"],
            row_stats["rows_failed"],
            row_stats["rows_skipped_empty"],
            row_stats["rows_skipped_existing"],
        )
        return row_stats

    def _wait_before_next_row(self, row_started_at: float) -> None:
        if self.row_processing_delay_seconds <= 0:
            return

        elapsed = time.monotonic() - row_started_at
        remaining = self.row_processing_delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    @staticmethod
    def _mark_queue_row_processed(queue_row: PartnerDataFileUpload) -> None:
        queue_row.status = PartnerDataFileUpload.Status.PROCESSED
        queue_row.processed_at = timezone.now()
        queue_row.processing_error = ""
        queue_row.save(
            update_fields=[
                "status",
                "processed_at",
                "processing_error",
                "updated_at",
            ]
        )
