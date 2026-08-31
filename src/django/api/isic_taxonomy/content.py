import json
import logging

from django.conf import settings
from django.core.cache import caches

from api.migrations._tigerline_helper import get_s3_client
from api.models.isic_taxonomy_config import IsicTaxonomyConfig

logger = logging.getLogger(__name__)

TAXONOMY_CONTENT_CACHE_KEY_PREFIX = 'taxonomy_content:isic4'
TAXONOMY_CONTENT_CACHE_TIMEOUT_SECONDS = 3600


class IsicTaxonomyNotAvailable(Exception):
    pass


def _content_cache_key(version: int) -> str:
    return f'{TAXONOMY_CONTENT_CACHE_KEY_PREFIX}:v{version}'


def invalidate_isic4_taxonomy_content_cache(
    *,
    version: int | None = None,
) -> None:
    cache = caches['view_cache']
    try:
        resolved_version = version
        if resolved_version is None:
            resolved_version = IsicTaxonomyConfig.load().version
        cache.delete(_content_cache_key(resolved_version))
    except Exception:
        logger.exception('Failed to invalidate ISIC taxonomy content cache')


def _load_json_from_s3(s3_key: str) -> dict:
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    if not bucket_name:
        raise IsicTaxonomyNotAvailable('S3 bucket is not configured.')

    s3_client = get_s3_client()
    response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    body = response['Body'].read().decode('utf-8')
    return json.loads(body)


def load_published_isic4_taxonomy(
    *,
    config: IsicTaxonomyConfig | None = None,
) -> dict:
    '''
    Load the published taxonomy JSON from object storage.

    Used by the public API (when active) and the Django admin page (always
    after a successful publish, even when the taxonomy is disabled).
    '''
    if config is None:
        config = IsicTaxonomyConfig.load()

    if not config.json_s3_key:
        raise IsicTaxonomyNotAvailable(
            'ISIC taxonomy has not been published to object storage.',
        )

    cache = caches['view_cache']
    cache_key = _content_cache_key(config.version)
    try:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    except Exception:
        logger.exception('Failed to read ISIC taxonomy content cache')

    taxonomy = _load_json_from_s3(config.json_s3_key)

    try:
        cache.set(
            cache_key,
            taxonomy,
            TAXONOMY_CONTENT_CACHE_TIMEOUT_SECONDS,
        )
    except Exception:
        logger.exception('Failed to write ISIC taxonomy content cache')

    return taxonomy


def load_isic4_taxonomy_content(
    *,
    config: IsicTaxonomyConfig | None = None,
) -> dict:
    if config is None:
        config = IsicTaxonomyConfig.load()

    if not config.is_active:
        raise IsicTaxonomyNotAvailable('ISIC taxonomy is disabled.')

    return load_published_isic4_taxonomy(config=config)
