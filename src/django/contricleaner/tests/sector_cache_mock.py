from contricleaner.lib.client_abstractions.sector_cache_interface import (
    SectorCacheInterface
)


class SectorCacheMock(SectorCacheInterface):
    def __init__(self):
        # One sector was set to a very long string to test that the
        # validation of long sector values works.
        self._sector_map = {
            'unspecified': 'Unspecified',
            'accessories': 'Accessories',
            'agriculture': 'Agriculture',
            'apparel': 'Apparel',
            'technology': 'Technology',
            'healthcare': 'Healthcare',
            'finance': 'Finance',
            ('agriculture agricultureagricultureagricultureagricultureagricu'
             'ltureagricultureagricultureagricultureagricultureagricultureag'
             'ricultureagricultureagricultureagricultureagricultureagricultu'
             'reagricultureagricultureagricultureagriculture'): (
                 'Agriculture AgricultureAgricultureAgricultureAgricultureAg'
                 'ricultureAgricultureAgricultureAgricultureAgricultureAgric'
                 'ultureAgricultureAgricultureAgricultureAgricultureAgricult'
                 'ureAgricultureAgricultureAgricultureAgricultureAgriculture')
        }

    @property
    def sector_map(self):
        return self._sector_map
