import re
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from api.models.contributor.contributor import Contributor
from api.models.user import User

SNAKE_CASE_COLUMN_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def validate_columns_to_process(raw_columns):
    """
    Validate and normalize a comma-separated list of column names.

    Each column must be lowercase snake_case and must not contain commas.
    """
    raw_value = str(raw_columns).strip()
    if not raw_value:
        raise ValidationError("columns_to_process cannot be empty.")

    columns = []
    for part in raw_value.split(","):
        column = part.strip()
        if not column:
            raise ValidationError(
                "columns_to_process must be a comma-separated list of "
                "lowercase snake_case column names without empty entries."
            )
        if not SNAKE_CASE_COLUMN_PATTERN.match(column):
            raise ValidationError(
                f'Invalid column name "{column}": each value must be '
                "lowercase snake_case (letters, numbers, and underscores "
                "only, starting with a letter)."
            )
        columns.append(column)

    return ",".join(columns)


class PartnerDataFileUpload(models.Model):
    """
    Tracks Google Sheets queued for moderation-event ingestion.
    """

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )
    google_drive_file_link = models.URLField(
        max_length=2000,
        help_text="Link to a Google Sheet stored in Google Drive.",
    )
    columns_to_process = models.TextField(
        help_text=(
            "Comma-separated list of sheet columns that should be processed. "
            "Must include os_id plus one or more partner field column names, "
            "for example: os_id,estimated_emissions_activity,schema_field. "
            "Each column name must be lowercase snake_case."
        ),
    )
    contributor = models.ForeignKey(
        Contributor,
        on_delete=models.PROTECT,
        related_name="partner_data_file_uploads",
        help_text="Contributor attributed to created moderation events.",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_partner_data_file_uploads",
        help_text="Moderator who created this ingestion request.",
    )
    is_processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this file has already been processed.",
    )
    batch_job_id = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="AWS Batch job ID used for processing this file.",
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this file finished processing.",
    )
    processing_error = models.TextField(
        blank=True,
        default="",
        help_text="Terminal processing error when ingestion fails.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def clean(self):
        super().clean()
        try:
            self.columns_to_process = validate_columns_to_process(
                self.columns_to_process
            )
        except ValidationError as error:
            raise ValidationError(
                {"columns_to_process": error.messages}
            ) from error

    def __str__(self):
        return (
            f"PartnerDataFileUpload {self.uuid} "
            f"processed={self.is_processed}"
        )
