from .row_serializer import RowSerializer
from typing import Union, Set


class SectorCacheInterface:
    @property
    def sector_map(self) -> dict:
        pass


class RowSectorSerializer(RowSerializer):
    def __init__(self, sector_cache: SectorCacheInterface) -> None:
        self.sector_cache = sector_cache

    def validate(self, row: dict, current: dict) -> dict:
        values = RowSectorSerializer.split_values([
                row.get('sector', []),
                row.get('product_type', []),
                row.get('sector_product_type', []),
            ], ', ')

        sectors, product_types = self.parse_all_values(values)

        current['product_types'] = product_types
        current['sectors'] = sectors

        return current

    @staticmethod
    def split_values(value: Union[str, list], split: str) -> Set[str]:
        if isinstance(value, str):
            return set(value.split(split))
        elif isinstance(value, list) or isinstance(value, set):
            res = set()
            for v in value:
                res = res.union(RowSectorSerializer.split_values(v, split))
            return res
        else:
            raise ValueError("Unsupported value type: {}".format(type(value)))

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
