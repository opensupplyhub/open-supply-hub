from datetime import datetime, timedelta
from api.models import Sector
from contricleaner.lib.client_abstractions.sector_cache_interface import (
    SectorCacheInterface
)


class SectorCache(SectorCacheInterface):
    REFRESH_INTERVAL = timedelta(seconds=300)

    def __init__(self) -> None:
        self.map = None

    def refetch_sectors(self):
        self.map = {
            sector.name.lower(): sector.name
            for sector in Sector.objects.all()
        }
        self.fetch_time = datetime.now()

    def refresh_if_needed(self):
        if self.map is None or (
            datetime.now() > self.fetch_time + SectorCache.REFRESH_INTERVAL
        ):
            self.refetch_sectors()

    @property
    def sector_map(self):
        self.refresh_if_needed()
        return self.map
