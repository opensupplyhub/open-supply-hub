from countries.lib.get_country_code import get_country_code

from contricleaner.lib.dto.row_dto import RowDTO
from contricleaner.lib.helpers.clean import clean


class RowSectorSerializer:
    def validate(self, row: dict, current: dict) -> dict:
        current["sector"] = row["sector"].split(",")


class RowCleanFieldSerializer:
    def __init__(self, field: str, new_field: str) -> None:
        self.field = field
        self.new_field = new_field

    def validate(self, row: dict, current: dict) -> dict:
        clean_value = clean(row[self.field])
        if len(clean_value) == 0:
            current["errors"].append(
                {
                    "message": "{} cannot be empty".format(self.new_field),
                    "type": "Error",
                }
            )
            return current

        current[self.new_field] = clean_value
        return current


class RowCleanedUserDataSerializer:
    def validate(self, row: dict, current: dict) -> dict:
        current["cleaned_user_data"] = row.copy()
        return current


class RowEmptySerializer:
    def validate(self, row: dict, current: dict) -> dict:
        keys = set(row.keys()).difference(current.keys())
        for key in keys:
            current[key] = row[key]

        return current


class RowCountrySerializer:
    def validate(self, row: dict, current: dict) -> dict:
        try:
            current["country_code"] = get_country_code(row["country"])
            return current
        except ValueError as exc:
            current["errors"].append(
                {
                    "message": str(exc),
                    "type": "Error",
                }
            )
            return current


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
