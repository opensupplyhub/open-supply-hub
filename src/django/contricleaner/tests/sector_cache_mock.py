from contricleaner.lib.client_abstractions.sector_cache_interface import (
    SectorCacheInterface
)


class SectorCacheMock(SectorCacheInterface):
    def __init__(self):
        self._sector_map = {
            'unspecified': 'Unspecified',
            'accessories': 'Accessories',
            'agriculture': 'Agriculture',
            'apparel': 'Apparel',
            'technology': 'Technology',
            'healthcare': 'Healthcare',
            'finance': 'Finance',
        }

    @property
    def sector_map(self):
        return self._sector_map
