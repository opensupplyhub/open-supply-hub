import logging
import uuid

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from api.isic_taxonomy.builder import build_taxonomy, count_taxonomy_levels
from api.isic_taxonomy.constants import (
    JS_ARTIFACT_NAME,
    JSON_ARTIFACT_NAME,
    SOURCE_ARTIFACT_NAME,
    STAGING_PREFIX,
    TAXONOMY_S3_PREFIX,
)
from api.isic_taxonomy.errors import (
    IsicTaxonomyPublishError,
    IsicTaxonomyValidationError,
)
from api.isic_taxonomy.generator import generate_js_bundle, generate_json
from api.isic_taxonomy.parser import normalize_extension
from api.isic_taxonomy.runtime_config import invalidate_taxonomy_config_cache
from api.isic_taxonomy.validator import validate_file
from api.migrations._tigerline_helper import get_s3_client

logger = logging.getLogger(__name__)


def artifact_s3_keys(
    version: int,
    source_extension: str = '.bin',
) -> dict[str, str]:
    prefix = f'{TAXONOMY_S3_PREFIX}/v{version}'
    return {
        'json_s3_key': f'{prefix}/{JSON_ARTIFACT_NAME}',
        'bundle_s3_key': f'{prefix}/{JS_ARTIFACT_NAME}',
        'source_s3_key': f'{prefix}/{SOURCE_ARTIFACT_NAME}{source_extension}',
    }


def parse_and_validate(file_content: bytes, filename: str) -> dict:
    '''
    Stage 1 + 2: validate spreadsheet and build taxonomy tree in memory.
    '''
    rows = validate_file(file_content, filename)
    return build_taxonomy(rows)


def publish_taxonomy(
    *,
    file_content: bytes,
    filename: str,
    uploaded_by=None,
    activate: bool = True,
) -> dict:
    '''
    Atomic publish workflow: validate, stage to S3, update DB, promote.

    Returns a dict with taxonomy, counts, version, and S3 keys on success.
    On failure the active version is left unchanged and last_error is stored.
    '''
    from api.models.isic_taxonomy_config import IsicTaxonomyConfig

    config = IsicTaxonomyConfig.load()
    staging_id = uuid.uuid4().hex
    staging_prefix = f'{STAGING_PREFIX}/{staging_id}'
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    if not bucket_name:
        raise IsicTaxonomyPublishError(
            'AWS_STORAGE_BUCKET_NAME is not configured. '
            'Cannot publish ISIC taxonomy artifacts to S3.'
        )

    try:
        taxonomy = parse_and_validate(file_content, filename)
    except IsicTaxonomyValidationError as exc:
        _store_last_error(config, str(exc))
        raise

    counts = count_taxonomy_levels(taxonomy)
    source_extension = normalize_extension(filename)
    staging_keys = {
        'source': (
            f'{staging_prefix}/{SOURCE_ARTIFACT_NAME}{source_extension}'
        ),
        'json': f'{staging_prefix}/{JSON_ARTIFACT_NAME}',
        'bundle': f'{staging_prefix}/{JS_ARTIFACT_NAME}',
    }

    s3_client = get_s3_client()
    final_keys = None
    version = None
    try:
        _upload_staging_artifacts(
            s3_client,
            bucket_name,
            staging_keys,
            file_content,
            taxonomy,
        )
        version = config.version + 1
        final_keys = artifact_s3_keys(version, source_extension)
        _promote_staging_to_version(
            s3_client,
            bucket_name,
            staging_keys,
            final_keys,
        )
        _update_config_after_publish(
            config,
            version=version,
            final_keys=final_keys,
            counts=counts,
            uploaded_by=uploaded_by,
            activate=activate,
        )
    except Exception as exc:
        logger.exception('ISIC taxonomy publish failed during S3/DB update')
        _store_last_error(config, str(exc))
        raise IsicTaxonomyPublishError(str(exc)) from exc
    finally:
        _cleanup_staging_prefix(s3_client, bucket_name, staging_prefix)

    return {
        'taxonomy': taxonomy,
        'version': version,
        'counts': counts,
        **final_keys,
    }


def _upload_staging_artifacts(
    s3_client,
    bucket_name: str,
    staging_keys: dict[str, str],
    source_content: bytes,
    taxonomy: dict,
) -> None:
    s3_client.put_object(
        Bucket=bucket_name,
        Key=staging_keys['source'],
        Body=source_content,
        ContentType='application/octet-stream',
    )
    s3_client.put_object(
        Bucket=bucket_name,
        Key=staging_keys['json'],
        Body=generate_json(taxonomy),
        ContentType='application/json',
    )
    s3_client.put_object(
        Bucket=bucket_name,
        Key=staging_keys['bundle'],
        Body=generate_js_bundle(taxonomy),
        ContentType='application/javascript',
    )


def _promote_staging_to_version(
    s3_client,
    bucket_name: str,
    staging_keys: dict[str, str],
    final_keys: dict[str, str],
) -> None:
    key_pairs = (
        (staging_keys['source'], final_keys['source_s3_key']),
        (staging_keys['json'], final_keys['json_s3_key']),
        (staging_keys['bundle'], final_keys['bundle_s3_key']),
    )
    for source_key, destination_key in key_pairs:
        s3_client.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': source_key},
            Key=destination_key,
        )


def _update_config_after_publish(
    config,
    *,
    version: int,
    final_keys: dict[str, str],
    counts: dict[str, int],
    uploaded_by,
    activate: bool,
) -> None:
    with transaction.atomic():
        config.version = version
        config.json_s3_key = final_keys['json_s3_key']
        config.bundle_s3_key = final_keys['bundle_s3_key']
        config.section_count = counts['section_count']
        config.division_count = counts['division_count']
        config.group_count = counts['group_count']
        config.class_count = counts['class_count']
        config.uploaded_by = uploaded_by
        config.published_at = timezone.now()
        config.last_error = ''
        if activate:
            config.is_active = True
        config.save()
    invalidate_taxonomy_config_cache()


def _store_last_error(config, message: str) -> None:
    config.last_error = message
    config.save(update_fields=['last_error', 'updated_at'])


def _cleanup_staging_prefix(
    s3_client,
    bucket_name: str,
    staging_prefix: str,
) -> None:
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=f'{staging_prefix}/',
        )
        for item in response.get('Contents', []):
            s3_client.delete_object(Bucket=bucket_name, Key=item['Key'])
    except Exception:
        logger.exception(
            'Failed to clean up ISIC taxonomy staging prefix %s',
            staging_prefix,
        )
