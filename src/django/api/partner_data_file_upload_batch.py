import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import (
    NoCredentialsError,
    PartialCredentialsError,
)
from django.conf import settings

BATCH_CLIENT_CONFIG = Config(
    connect_timeout=5,
    read_timeout=15,
    retries={"max_attempts": 2},
)


def validate_aws_batch_prerequisites():
    if not settings.BATCH_JOB_QUEUE_NAME:
        raise ValueError(
            "BATCH_JOB_QUEUE_NAME is not configured. Set it in the environment "
            "before submitting a partner data file for processing."
        )

    if not settings.BATCH_JOB_DEF_NAME:
        raise ValueError(
            "BATCH_JOB_DEF_NAME is not configured. Set it in the environment "
            "before submitting a partner data file for processing."
        )

    credentials = boto3.Session().get_credentials()
    if credentials is None:
        raise ValueError(
            "AWS credentials are not configured. Set AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY, configure AWS_PROFILE, or use another "
            "supported credential source before submitting a partner data file."
        )

    frozen = credentials.get_frozen_credentials()
    if not frozen.access_key or not frozen.secret_key:
        raise ValueError(
            "AWS credentials are incomplete. Check AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY (and AWS_SESSION_TOKEN if required)."
        )


def submit_partner_data_file_upload_job(queue_entry_uuid) -> str:
    """
    Queue an AWS Batch job to process a partner data file upload.
    Validates configuration and credentials before calling AWS.
    """
    validate_aws_batch_prerequisites()

    job_name = (
        f"partner-data-file-{str(queue_entry_uuid)[:8]}-"
        f"{uuid.uuid4().hex[:8]}"
    )
    try:
        batch_client = boto3.client("batch", config=BATCH_CLIENT_CONFIG)
        response = batch_client.submit_job(
            jobName=job_name,
            jobQueue=settings.BATCH_JOB_QUEUE_NAME,
            jobDefinition=settings.BATCH_JOB_DEF_NAME,
            parameters={"queueentryuuid": str(queue_entry_uuid)},
        )
    except (NoCredentialsError, PartialCredentialsError) as error:
        raise ValueError(
            "AWS credentials are not configured. Set AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY, configure AWS_PROFILE, or use another "
            "supported credential source before submitting a partner data "
            "file."
        ) from error

    job_id = response.get("jobId")
    if not job_id:
        raise RuntimeError(
            f"Batch submit response missing jobId: {response}"
        )
    return job_id
