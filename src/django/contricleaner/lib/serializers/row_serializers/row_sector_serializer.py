from django.core.exceptions import ValidationError
from contricleaner.constants import DEFAULT_SECTOR_NAME, MAX_PRODUCT_TYPE_COUNT
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

        if len(product_types) > MAX_PRODUCT_TYPE_COUNT:
            raise ValidationError(
                f'You may submit a maximum of {MAX_PRODUCT_TYPE_COUNT} '
                f'product types, not {len(product_types)}')

        if product_types:
            current['product_type'] = product_types

        current['sector'] = sectors

        return current

    def parse_all_values(self, all_values):
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
