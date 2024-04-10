from contricleaner.constants import DEFAULT_SECTOR_NAME, MAX_PRODUCT_TYPE_COUNT

from contricleaner.lib.helpers.is_valid_type import (
    is_valid_type,
)
from contricleaner.lib.helpers.split_values import split_values

from contricleaner.lib.client_abstractions.sector_cache_interface import (
    SectorCacheInterface
)
from .row_serializer import RowSerializer


class RowSectorSerializer(RowSerializer):
    def __init__(
        self, sector_cache: SectorCacheInterface, split_pattern: str
    ) -> None:
        self.sector_cache = sector_cache
        self.split_pattern = split_pattern

    def validate(self, row: dict, current: dict) -> dict:
        fields = ['sector', 'product_type', 'sector_product_type']

        values = []
        sector_errors = []

        for field in fields:
            value = row.get(field)
            if field in row and value:

                if not is_valid_type(value):
                    sector_errors.append(
                        {
                            "message": "Expected value for {} to be a string "
                            "or a list of strings but got {}".format(
                                field, value
                            ),
                            "type": "ValueError",
                        }
                    )
                else:
                    values.append(value)

        if sector_errors:
            current["errors"].extend(sector_errors)
            return current

        splitted_values = split_values(values, self.split_pattern)

        sectors, product_types = self.parse_all_values(splitted_values)

        if len(product_types) > MAX_PRODUCT_TYPE_COUNT:
            current["errors"].append(
                {
                    "message": "You may submit a maximum of {} product types, "
                    "not {}".format(
                        MAX_PRODUCT_TYPE_COUNT, len(product_types)
                    ),
                    "type": "ValidationError",
                }
            )
            return current

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
    def clean_value(value: str) -> str:
        return value.lower().strip()
