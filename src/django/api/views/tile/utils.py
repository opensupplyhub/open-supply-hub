from datetime import datetime
from typing import Tuple

from django.utils import timezone

from api.models.tile_cache import TileCache
from api.models.dynamic_setting import DynamicSetting


def retrieve_cached_tile(request_full_path: str) -> Tuple[TileCache, bool]:
    cached_tile, created = TileCache.objects \
        .select_for_update().get_or_create(path=request_full_path)

    return cached_tile, created


def is_tile_cache_valid(creation_date: datetime) -> bool:
    settings = DynamicSetting.load()
    current_datetime = timezone.now()
    expiration_date = current_datetime - timezone.timedelta(
        seconds=settings.cached_tile_expiration_time)

    return creation_date > expiration_date
