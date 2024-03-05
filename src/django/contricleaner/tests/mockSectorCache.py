from contricleaner.lib.sector_cache_interface import SectorCacheInterface


class MockSectorCache(SectorCacheInterface):
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