from contricleaner.lib.helpers.split_values import split_values
from contricleaner.lib.sector_cache_interface import SectorCacheInterface
from .row_serializer import RowSerializer


class RowSectorSerializer(RowSerializer):
    def __init__(self, sector_cache: SectorCacheInterface) -> None:
        self.sector_cache = sector_cache

    def validate(self, row: dict, current: dict) -> dict:
        values = split_values([
                row.get('sector', []),
                row.get('product_type', []),
                row.get('sector_product_type', []),
            ], ', ')

        sectors, product_types = self.parse_all_values(values)

        current['product_types'] = product_types
        current['sectors'] = sectors

        return current

    def parse_all_values(self, all_values):
        DEFAULT_SECTOR_NAME = 'Unspecified'

        sector_map = self.sector_cache.sector_map
        sectors = []
        product_types = []
        for value in all_values:
            clean_value = self.clean_value(value)
            if clean_value in sector_map:
                sectors.append(sector_map[clean_value])
            else:
                product_types.append(value)

        if not sectors:
            sectors.append(DEFAULT_SECTOR_NAME)

        sectors.sort()
        product_types.sort()

        return sectors, product_types

    @staticmethod
    def clean_value(value):
        return value.lower().strip()
