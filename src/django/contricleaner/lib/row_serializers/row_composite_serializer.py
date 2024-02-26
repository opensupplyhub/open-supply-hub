from contricleaner.lib.dto.row_dto import RowDTO

from .row_clean_field_serializer import RowCleanFieldSerializer
from .row_composite_serializer import RowSectorSerializer
from .row_country_serializer import RowCountrySerializer
from .row_empty_serializer import RowEmptySerializer


class RowCompositeSerializer:
    def __init__(self):
        self.validators = [
            RowCleanFieldSerializer("name", "clean_name"),
            RowCleanFieldSerializer("address", "clean_address"),
            RowSectorSerializer(),
            RowCountrySerializer(),
            RowEmptySerializer(),
        ]

    def get_validated_row(self, raw_row: dict):

        standard_fields = {
            "name",
            "clean_name",
            "address",
            "clean_address",
            "country_code",
            "sector",
        }

        res = {
            "errors": [],
        }
        row = raw_row.copy()

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
            sector=dict_res.get("sector", ""),
            fields=dict_res.get("fields", {}),
            errors=dict_res.get("errors", []),
        )
