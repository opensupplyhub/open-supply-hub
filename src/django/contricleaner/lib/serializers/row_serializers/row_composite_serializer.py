import re
from typing import Dict
from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.sector_cache_interface import SectorCacheInterface
from contricleaner.lib.serializers.row_serializers.row_clean_field_serializer \
    import RowCleanFieldSerializer
from contricleaner.lib.serializers.row_serializers.row_country_serializer \
    import RowCountrySerializer
from contricleaner.lib.serializers.row_serializers.row_empty_serializer \
    import RowEmptySerializer
from contricleaner.lib.serializers.row_serializers.\
    row_facility_type_serializer import RowFacilityTypeSerializer
from contricleaner.lib.serializers.row_serializers.row_sector_serializer \
    import RowSectorSerializer
from contricleaner.lib.serializers.row_serializers \
    .row_required_fields_serializer \
    import RowRequiredFieldsSerializer


class RowCompositeSerializer:
    def __init__(
        self, sector_cache: SectorCacheInterface, sector_split_pattern: str
    ):
        self.validators = [
            RowCleanFieldSerializer("name", "clean_name"),
            RowCleanFieldSerializer("address", "clean_address"),
            RowSectorSerializer(sector_cache, sector_split_pattern),
            RowCountrySerializer(),
            RowRequiredFieldsSerializer(),
            RowFacilityTypeSerializer(),
            RowEmptySerializer(),
        ]

    @staticmethod
    def clean_row(row: str) -> str:
        return RowCompositeSerializer.__clean_and_replace_data(row)

    @staticmethod
    def __clean_and_replace_data(data: Dict[str, str]) -> Dict[str, str]:
        invalid_keywords = ['N/A', 'n/a']
        dup_pattern = ',' + '{2,}'
        result_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Remove invalid keywords.
                for keyword in invalid_keywords:
                    value = value.replace(keyword, '')
                # Remove duplicates commas if exist.
                value = re.sub(dup_pattern, ',', value)
                # Remove comma in the end of the string if exist.
                value = value.rstrip(',')
                # Remove extra spaces if exist.
                value = value.strip()
            result_data[key] = value
        return result_data

    def get_validated_row(self, raw_row: dict):
        standard_fields = {
            "name",
            "clean_name",
            "address",
            "clean_address",
            "country_code",
            "sector",
            "errors"
        }

        res = {
            "errors": [],
        }

        row = raw_row.copy()
        row = RowCompositeSerializer.clean_row(row)

        for validator in self.validators:
            res = validator.validate(row, res)

        dict_res = {
            "fields": {},
        }

        for res_key, res_value in res.items():
            if res_key in standard_fields:
                dict_res[res_key] = res_value
            else:
                dict_res["fields"][res_key] = res_value

        return RowDTO(
            raw_json=raw_row,
            name=dict_res.get("name", ""),
            clean_name=dict_res.get("clean_name", ""),
            address=dict_res.get("address", ""),
            clean_address=dict_res.get("clean_address", ""),
            country_code=dict_res.get("country_code", ""),
            sector=dict_res.get("sector", []),
            fields=dict_res.get("fields", {}),
            errors=dict_res.get("errors", []),
        )
