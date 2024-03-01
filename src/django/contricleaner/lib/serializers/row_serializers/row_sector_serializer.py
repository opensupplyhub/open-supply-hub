from .row_serializer import RowSerializer


class SectorCacheInterface:
    @property
    def sector_map(self) -> dict:
        pass


class RowSectorSerializer(RowSerializer):
    def __init__(self, cache=SectorCacheInterface):
        self.cache = cache
        self.sectors = []
        self.product_types = []

    def validate(self, row: dict, current: dict) -> dict:
        # self.parse_all_values(
        #     set([
        #         *row.get('sector', []),
        #         *row.get('product_type', []),
        #         *row.get('sector_product_type', [])
        #     ])
        # )

        current["sector"] = row["sector"].split(",")
        print('current', current)
        return current

    # def parse_all_values(self, all_values):
    #     DEFAULT_SECTOR_NAME = 'Unspecified'

    #     sector_map = SectorCacheInterface.sector_map

    #     for value in all_values:
    #         clean_value = self.clean_value(value)
    #         if (clean_value in sector_map):
    #             self.sectors.append(sector_map[clean_value])
    #         else:
    #             self.product_types.append(value)

    #         if len(self.sectors) == 0:
    #             self.sectors.append(DEFAULT_SECTOR_NAME)

    # def sort_values(self):
    #     self.sectors.sort()
    #     self.product_types.sort()

    # def clean_value(self, value):
    #     return value.lower().strip()
