import mimetypes
import re
import threading
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import boto3
from unidecode import unidecode

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

_SEPARATOR_RUN = re.compile(r'[-\s]+')

# Characters that would close the quoted filename and open a parameter of
# their own. Stripped after transliteration, not before: unidecode maps
# several ordinary letters onto them, including the Japanese iteration
# mark 々 -> " and 〆 -> /, both of which occur in real names.
_HEADER_UNSAFE = re.compile(r'["<>;,\\/\r\n]')


def _to_ascii(value):
    '''
    Render one filename part as hyphen-separated ASCII. unidecode is used
    rather than an NFKD fold because NFKD drops any letter it cannot
    decompose, turning "çalıştırma" into "calstrma" and a CJK name into
    nothing at all.
    '''
    transliterated = _HEADER_UNSAFE.sub('', unidecode(value))
    return _SEPARATOR_RUN.sub('-', transliterated).strip('-')


def build_content_disposition(file_name):
    '''
    Build an RFC 6266 Content-Disposition carrying both a transliterated
    ASCII `filename=` and the RFC 5987 `filename*=UTF-8''` form. HTTP
    header values are ISO-8859-1, so a Turkish or CJK name in the plain
    form alone makes S3 reject the presigned request (OSDEV-3600).
    '''
    stem, dot, extension = file_name.rpartition('.')
    if not dot:
        stem, extension = file_name, ''

    # Name both forms, not just the fallback: slugify reduces a stem of
    # only emoji or punctuation to nothing, and a bare ".pdf" in
    # filename* makes a browser save a hidden, stem-less dotfile.
    def _join(part_stem, part_extension):
        if part_extension:
            return f'{part_stem}.{part_extension}'
        return part_stem

    ascii_name = _join(_to_ascii(stem) or 'attachment', _to_ascii(extension))
    display_name = _join(stem or 'attachment', extension)

    # quote() leaves the RFC 5987 attr-chars (ALPHA/DIGIT/-._~) alone and
    # percent-encodes the rest as UTF-8, so no delimiter survives here.
    encoded_name = quote(display_name, safe='')

    return (
        f'attachment; filename="{ascii_name}"; '
        f"filename*=UTF-8''{encoded_name}"
    )


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
    expiry, single object key, an RFC 6266 Content-Disposition carrying
    the original display filename (see build_content_disposition), and
    the content type derived from the validated extension (never the
    uploader's declared type).

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
    disposition = build_content_disposition(attachment.file_name)

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
