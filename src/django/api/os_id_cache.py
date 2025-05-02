from datetime import datetime, timedelta
from api.models import Facility
from django.contricleaner.lib.client_abstractions.cache_interface import (
    CacheInterface
)


class OSIDCache(CacheInterface):
    REFRESH_INTERVAL = timedelta(seconds=300)

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
    def value_map(self):
        self.refresh_if_needed()
        return self.map
