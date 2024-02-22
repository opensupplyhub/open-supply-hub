from contricleaner.lib.dto.row_dto import RowDTO
import re
from unidecode import unidecode

from countries.get_country_code import get_country_code


def clean(column):
    """
    Remove punctuation and excess whitespace from a value before using it to
    find matches. This should be the same function used when developing the
    training data read from training.json as part of train_gazetteer.
    """
    column = unidecode(column)
    column = re.sub("\n", " ", column)
    column = re.sub("-", "", column)
    column = re.sub("/", " ", column)
    column = re.sub("'", "", column)
    column = re.sub(",", "", column)
    column = re.sub(":", " ", column)
    column = re.sub(" +", " ", column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column:
        column = None
    return column


class RowSectorValidator:
    def validate(self, str, value, row: dict) -> dict:
        return {"sector": [value]}


class RowCleanFieldValidator:
    def __init__(self, new_field) -> None:
        self.new_field = new_field

    def validate(self, key: str, value, row: dict) -> dict:
        clean_value = clean(value)
        if len(clean_value) == 0:
            return {
                "error": {
                    "message": "{} cannot be empty".format(self.new_field),
                    "type": "Error",
                }
            }
        return {self.new_field: clean_value}


class RowCleanedUserDataValidator:
    def validate(self, key: str, value, row: dict) -> dict:
        return {"cleaned_user_data": row.copy()}


class RowEmptyValidator:
    def validate(self, key: str, value, row: dict) -> dict:
        return {key: value}


class RowCountryValidator:
    def validate(self, key: str, value, row: dict) -> dict:
        try:
            return {"country_code": get_country_code(value)}
        except ValueError as exc:
            return {"error": {"message": str(exc), "type": "Error"}}


class RowCompositeValidator:
    def __init__(self):
        self.validators = {
            "name": [
                RowCleanFieldValidator("clean_name"),
                RowEmptyValidator(),
            ],
            "address": [
                RowCleanFieldValidator("clean_address"),
                RowEmptyValidator(),
            ],
            "sector": [
                RowSectorValidator(),
            ],
            "country": [
                RowCountryValidator(),
            ],
        }

        self.__any__ = RowEmptyValidator()
        self.__all__ = [RowCleanedUserDataValidator()]

    def get_validated_row(self, raw_row: dict):
        dict_res = {
            "errors": [],
            "fields": {},
        }
        standard_fields = {
            "name",
            "clean_name",
            "address",
            "clean_address",
            "country_code",
            "sector",
        }
        row = raw_row.copy()
        for key, value in row.items():
            validators = self.validators.get(key, [self.__any__]).copy()

            for validator in validators:
                res = validator.validate(key, value, row)
                for res_key, res_value in res.items():
                    if res_key == "errors":
                        dict_res["errors"].extend(res_value)
                    elif res_key in standard_fields:
                        dict_res.update({res_key: res_value})
                    else:
                        dict_res["fields"].update({res_key: res_value})
        
        for validator in self.__all__:
            res = validator.validate("", "", row)
            for res_key, res_value in res.items():
                if res_key == "errors":
                    dict_res["errors"].extend(res_value)
                elif res_key in standard_fields:
                    dict_res.update({res_key: res_value})
                else:
                    dict_res["fields"].update({res_key: res_value})


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
