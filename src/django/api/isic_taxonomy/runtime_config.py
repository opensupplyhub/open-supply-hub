import logging

from django.core.cache import caches
from django.urls import reverse

from api.isic_taxonomy.content import invalidate_isic4_taxonomy_content_cache
from api.models.isic_taxonomy_config import IsicTaxonomyConfig

logger = logging.getLogger(__name__)

TAXONOMY_CONFIG_CACHE_KEY = 'taxonomy_config:isic4'
TAXONOMY_CONFIG_CACHE_TIMEOUT_SECONDS = 60
TAXONOMY_CONFIG_BROWSER_CACHE_CONTROL = (
    f'public, max-age={TAXONOMY_CONFIG_CACHE_TIMEOUT_SECONDS}'
)


def invalidate_taxonomy_config_cache(*, version: int | None = None) -> None:
    try:
        caches['view_cache'].delete(TAXONOMY_CONFIG_CACHE_KEY)
    except Exception:
        logger.exception('Failed to invalidate ISIC taxonomy config cache')
    invalidate_isic4_taxonomy_content_cache(version=version)


def get_isic4_taxonomy_url(
    *,
    config: IsicTaxonomyConfig | None = None,
) -> str:
    if config is None:
        config = IsicTaxonomyConfig.load()
    return f'{reverse("isic_taxonomy")}?v={config.version}'


def build_isic4_config(*, config: IsicTaxonomyConfig | None = None) -> dict:
    if config is None:
        config = IsicTaxonomyConfig.load()

    taxonomy_url = None
    if config.is_active:
        taxonomy_url = get_isic4_taxonomy_url(config=config)

    return {
        'enabled': config.is_active,
        'version': config.version,
        'taxonomyUrl': taxonomy_url,
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
