from datetime import datetime, timedelta
from django.core.paginator import Paginator
from api.models import Facility
from contricleaner.lib.client_abstractions.cache_interface import (
    CacheInterface
)


class OSIDCache(CacheInterface):
    REFRESH_INTERVAL = timedelta(seconds=300)
    BATCH_SIZE = 10000

    def __init__(self) -> None:
        self.map = None

    def refetch_os_ids(self):
        paginator = Paginator(Facility.objects.only('id').values_list('id', flat=True), OSIDCache.BATCH_SIZE)

        self.map = {}
        for page_num in paginator.page_range:
            for facility_id in paginator.page(page_num).object_list:
                self.map[facility_id.lower()] = facility_id
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
