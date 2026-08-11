import logging

from django.conf import settings
from django.core.cache import caches

from api.migrations._tigerline_helper import get_s3_client
from api.models.isic_taxonomy_config import IsicTaxonomyConfig

logger = logging.getLogger(__name__)

TAXONOMY_CONFIG_CACHE_KEY = 'taxonomy_config:isic4'
TAXONOMY_CONFIG_CACHE_TIMEOUT_SECONDS = 60
BUNDLE_URL_EXPIRES_IN_SECONDS = 3600


def invalidate_taxonomy_config_cache() -> None:
    try:
        caches['view_cache'].delete(TAXONOMY_CONFIG_CACHE_KEY)
    except Exception:
        logger.exception('Failed to invalidate ISIC taxonomy config cache')


def get_isic4_bundle_url(bundle_s3_key: str) -> str | None:
    if not bundle_s3_key:
        return None

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    if not bucket_name:
        return None

    s3_client = get_s3_client()
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': bundle_s3_key},
        ExpiresIn=BUNDLE_URL_EXPIRES_IN_SECONDS,
    )


def build_isic4_config(*, config: IsicTaxonomyConfig | None = None) -> dict:
    if config is None:
        config = IsicTaxonomyConfig.load()

    bundle_url = None
    if config.is_active and config.bundle_s3_key:
        bundle_url = get_isic4_bundle_url(config.bundle_s3_key)

    return {
        'enabled': config.is_active,
        'version': config.version,
        'bundleUrl': bundle_url,
    }


def get_isic4_environment_vars(
    *,
    config: IsicTaxonomyConfig | None = None,
) -> dict:
    isic4 = build_isic4_config(config=config)
    return {
        'ISIC4_TAXONOMY_ENABLED': 'true' if isic4['enabled'] else 'false',
        'ISIC4_TAXONOMY_VERSION': str(isic4['version']),
        'ISIC4_TAXONOMY_BUNDLE_URL': isic4['bundleUrl'] or '',
    }


def get_taxonomy_config() -> dict:
    cache = caches['view_cache']
    try:
        cached = cache.get(TAXONOMY_CONFIG_CACHE_KEY)
        if cached is not None:
            return cached
    except Exception:
        logger.exception('Failed to read ISIC taxonomy config cache')

    payload = {'isic4': build_isic4_config()}
    try:
        cache.set(
            TAXONOMY_CONFIG_CACHE_KEY,
            payload,
            TAXONOMY_CONFIG_CACHE_TIMEOUT_SECONDS,
        )
    except Exception:
        logger.exception('Failed to write ISIC taxonomy config cache')

    return payload
