import uuid

import boto3
from botocore.config import Config
from django.conf import settings

BATCH_CLIENT_CONFIG = Config(
    connect_timeout=5,
    read_timeout=15,
    retries={"max_attempts": 2},
)

_BEFORE_SUBMIT_MSG = (
    "before submitting a partner data file for processing."
)


def validate_aws_batch_prerequisites():
    for setting_name in (
        "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_QUEUE_NAME",
        "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_DEF_NAME",
    ):
        if not getattr(settings, setting_name, None):
            raise ValueError(
                f"{setting_name} is not configured. Set it in the environment "
                f"{_BEFORE_SUBMIT_MSG}"
            )

    credentials = boto3.Session().get_credentials()
    if credentials is None:
        raise ValueError(
            "AWS credentials are not configured. Set AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY, configure AWS_PROFILE, or use another "
            f"supported credential source {_BEFORE_SUBMIT_MSG}"
        )

    frozen = credentials.get_frozen_credentials()
    if not frozen.access_key or not frozen.secret_key:
        raise ValueError(
            "AWS credentials are incomplete. Check AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY (and AWS_SESSION_TOKEN if required)."
        )


def submit_partner_data_file_upload_job(queue_entry_uuid) -> str:
    """Queue an AWS Batch job to process a partner data file upload."""
    validate_aws_batch_prerequisites()

    job_name = (
        f"partner-data-file-{str(queue_entry_uuid)[:8]}-"
        f"{uuid.uuid4().hex[:8]}"
    )
    batch_client = boto3.client("batch", config=BATCH_CLIENT_CONFIG)
    response = batch_client.submit_job(
        jobName=job_name,
        jobQueue=settings.BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_QUEUE_NAME,
        jobDefinition=settings.BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_DEF_NAME,
        parameters={"queueentryuuid": str(queue_entry_uuid)},
    )

    job_id = response.get("jobId")
    if not job_id:
        raise RuntimeError(
            f"Batch submit response missing jobId: {response}"
        )
    return job_id
