import mimetypes
import threading
from datetime import datetime, timedelta, timezone

import boto3
from django.conf import settings
from django.core.files.storage import default_storage

# Presigned download URLs are deliberately short-lived: they are bearer
# tokens, so the window in which a leaked URL is usable should be no
# longer than a browser needs to follow the redirect.
DOWNLOAD_URL_EXPIRY_SECONDS = 60

# An assumed-role session must comfortably outlive the URLs it signs: a
# presigned URL dies with the credentials that signed it, regardless of
# its own expiry.
_SESSION_DURATION_SECONDS = 900
_SESSION_REFRESH_MARGIN = timedelta(minutes=5)

_credentials_lock = threading.Lock()
_cached_credentials = None
_cached_credentials_expiry = None


def _get_signing_credentials():
    '''
    Return temporary credentials for the dedicated claim-attachments
    signing role, refreshing the cached session when it nears expiry.
    Returns None when no role is configured (local development, tests),
    in which case the default storage credentials are used instead.
    '''
    global _cached_credentials, _cached_credentials_expiry

    role_arn = getattr(
        settings, 'CLAIM_ATTACHMENTS_SIGNING_ROLE_ARN', None
    )
    if not role_arn:
        return None

    now = datetime.now(timezone.utc)
    with _credentials_lock:
        if (
            _cached_credentials is None
            or _cached_credentials_expiry is None
            or _cached_credentials_expiry - now < _SESSION_REFRESH_MARGIN
        ):
            response = boto3.client('sts').assume_role(
                RoleArn=role_arn,
                RoleSessionName='claim-attachment-downloads',
                DurationSeconds=_SESSION_DURATION_SECONDS,
            )
            _cached_credentials = response['Credentials']
            _cached_credentials_expiry = _cached_credentials['Expiration']
        return _cached_credentials


def generate_attachment_download_url(attachment):
    '''
    Mint a presigned GET URL for one claim attachment: 60-second
    expiry, single object key, Content-Disposition attachment with the
    original display filename, and the content type derived from the
    validated extension (never the uploader's declared type).

    When CLAIM_ATTACHMENTS_SIGNING_ROLE_ARN is configured, URLs are
    signed by that dedicated role (scoped to s3:GetObject on claim
    attachments) instead of the app task role. Locally and in tests it
    falls back to the default storage's URL generation.
    '''
    key = attachment.claim_attachment.name
    content_type = (
        mimetypes.guess_type(attachment.file_name)[0]
        or 'application/octet-stream'
    )
    # RFC 6266/5987 filename for the browser's save dialog. The display
    # name is already slugified at upload; strip quotes defensively.
    safe_name = attachment.file_name.replace('"', '')
    disposition = f'attachment; filename="{safe_name}"'

    credentials = _get_signing_credentials()
    if credentials is None:
        # Local dev / MinIO / test storage path.
        try:
            return default_storage.url(
                key,
                parameters={
                    'ResponseContentDisposition': disposition,
                    'ResponseContentType': content_type,
                },
                expire=DOWNLOAD_URL_EXPIRY_SECONDS,
            )
        except TypeError:
            # FileSystemStorage (tests) accepts no extra arguments.
            return default_storage.url(key)

    client = boto3.client(
        's3',
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
    return client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': key,
            'ResponseContentDisposition': disposition,
            'ResponseContentType': content_type,
        },
        ExpiresIn=DOWNLOAD_URL_EXPIRY_SECONDS,
    )
