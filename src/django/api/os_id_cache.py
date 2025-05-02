from datetime import datetime, timedelta
from api.models import Facility
from contricleaner.lib.client_abstractions.sector_cache_interface import (
    SectorCacheInterface
)


class OSIDCache(SectorCacheInterface):
    REFRESH_INTERVAL = timedelta(seconds=600)

    def __init__(self) -> None:
        self.map = None

    def refetch_os_ids(self):
        self.map = {
            facility.id.lower(): facility.id
            for facility in Facility.objects.all()
        }
        self.fetch_time = datetime.now()

    def refresh_if_needed(self):
        if self.map is None or (
            datetime.now() > self.fetch_time + OSIDCache.REFRESH_INTERVAL
        ):
            self.refetch_os_ids()

    @property
    def sector_map(self):
        self.refresh_if_needed()
        return self.map
