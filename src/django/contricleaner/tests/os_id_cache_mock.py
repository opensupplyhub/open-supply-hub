from contricleaner.lib.client_abstractions.cache_interface import (
    CacheInterface
)


class OSIDCacheMock(CacheInterface):
    def __init__(self):
        # One sector was set to a very long string to test that the
        # validation of long sector values works.
        self._os_id_map = {
            'us2025125qgxb8g': 'US2025125QGXB8G',
            'bd2025125418yvx': 'BD2025125418YVX',
        }

    @property
    def value_map(self):
        return self._os_id_map
