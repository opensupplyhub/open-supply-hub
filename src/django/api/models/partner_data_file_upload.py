import uuid

from django.db import models

from api.models.contributor.contributor import Contributor
from api.models.user import User


class PartnerDataFileUpload(models.Model):
    """
    Tracks Google Sheets queued for moderation-event ingestion.
    """

    DEVELOPER_PROCESSING_ERROR_PREFIX = "Contact developers: "
    DEVELOPER_ERROR_HINTS = (
        "Google Service Account",
        "AWS credentials",
        "BATCH_JOB_QUEUE_NAME",
        "BATCH_JOB_DEF_NAME",
    )

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        PROCESSED = "PROCESSED", "Processed"
        FAILED = "FAILED", "Failed"

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )
    google_drive_file_link = models.URLField(
        max_length=2000,
        help_text=(
            "Link to a Google Sheet stored in Google Drive. The sheet must "
            "include an os_id column and partner field columns the "
            "contributor is authorized to write."
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
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text=(
            "Updated automatically when the partner list file is processed. "
            "PENDING: saved and waiting to be queued. PROCESSING: the file "
            "is being read and partner data is being applied. PROCESSED: "
            "finished successfully (check the Google Sheet error column "
            "for any individual rows that need fixes). FAILED: the file "
            "could not be processed—read Processing error for what went "
            "wrong, correct the sheet or settings, and submit a new upload."
        ),
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
        help_text=(
            "When status is Failed, explains what went wrong. Messages "
            "starting with 'Contact developers:' are for the engineering "
            "team. Other messages usually mean fixes are needed in the "
            "Google Sheet before you submit again."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    @classmethod
    def format_developer_processing_error(cls, message: str) -> str:
        message = (message or "").strip()
        if message.startswith(cls.DEVELOPER_PROCESSING_ERROR_PREFIX):
            return message
        return f"{cls.DEVELOPER_PROCESSING_ERROR_PREFIX}{message}"

    @classmethod
    def format_upload_processing_error(cls, error: Exception) -> str:
        """
        Sheet or list issues stay as-is for moderators. Infrastructure,
        configuration, and unexpected failures are prefixed so moderators
        know to contact developers.
        """
        message = str(error).strip()
        if isinstance(error, ValueError):
            if any(hint in message for hint in cls.DEVELOPER_ERROR_HINTS):
                return cls.format_developer_processing_error(message)
            return message
        return cls.format_developer_processing_error(message)

    def __str__(self):
        return f"PartnerDataFileUpload {self.uuid} status={self.status}"
