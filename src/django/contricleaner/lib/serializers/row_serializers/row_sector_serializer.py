from .row_serializer import RowSerializer
from typing import List


class SectorCacheInterface:
    @property
    def sector_map(self) -> dict:
        pass


class RowSectorSerializer(RowSerializer):
    def __init__(self, sector_cache: SectorCacheInterface) -> None:
        self.sector_cache = sector_cache

    # @staticmethod
    # def split_values(value: any) -> List[str]:
    #     if isinstance(value, str):
    #         return value.split(', ')
    #     elif isinstance(value, list):
    #         return [RowSectorSerializer.split_values(v) for v in value]
    #     else:
    #         pass
    #         # raise ValueError("Unsupported value type: {}".format(type(value)))
    @staticmethod
    def split_values(value: any) -> List[str]:
        if isinstance(value, str):
            return value.split(', ')
        elif isinstance(value, list):
            return [item for sublist in map(RowSectorSerializer.split_values, value) for item in sublist]
        else:
            return []

    def validate(self, row: dict, current: dict) -> dict:

        values = [
                row.get('sector'),
                row.get('product_type'),
                row.get('sector_product_type'),
            ]
        print('values', values)
        result_set = set()

        for value in values:
            if value and isinstance(value, str):
                result_set.union(self.split_values(value))
            elif value and isinstance(value, list):
                result_set.union(self.split_values(tuple(value)))
            else:
                pass

        print('result_set', result_set)

        sectors, product_types = self.parse_all_values(result_set)

        current['product_types'] = product_types
        current['sectors'] = sectors
        print('current', current)
        return current

    def parse_all_values(self, all_values):
        DEFAULT_SECTOR_NAME = 'Unspecified'

        sector_map = self.sector_cache.sector_map
        sectors = []
        product_types = []
        for value in all_values:
            clean_value = self.clean_value(value)
            if (clean_value in sector_map):
                sectors.append(sector_map[clean_value])
            else:
                product_types.append(value)

        if len(sectors) == 0:
            sectors.append(DEFAULT_SECTOR_NAME)
        
        sectors.sort()
        product_types.sort()
        
        return sectors, product_types

    def clean_value(self, value):
        return value.lower().strip()
