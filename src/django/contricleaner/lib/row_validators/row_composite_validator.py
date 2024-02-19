from contricleaner.lib.dto.row_dto import RowDTO
import re
from unidecode import unidecode


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


class RowCleanFieldValidator:
    def __init__(self, test_field, new_field) -> None:
        self.test_field = test_field
        self.new_field = new_field

    def validate(self, row: dict) -> dict:
        return {self.new_field: clean(row.get(self.test_field, ""))}

        

class RowEmptyValidator:
    def validate(self, row: dict) -> dict:
        return row.copy()


class RowCompositeValidator:
    def __init__(self):
        self.validators = [
            RowCleanFieldValidator("name", "clean_name"),
            RowCleanFieldValidator("address", "clean_address"),
            RowEmptyValidator(),
        ]

    def get_validated_row(self, raw_row: dict):
        dict_res = {
            "errors": [],
            "fields": {},
        }
        standard_fields = [
            "name",
            "clean_name",
            "address",
            "clean_address",
            "country_code",
            "sector",
        ]
        row = raw_row.copy()
        for validator in self.validators:
            res = validator.validate(row)
            for key in res:
                print("<<<< {}".format(key))
                if key == "errors":
                    dict_res["errors"].extend(res["errors"])
                elif key in standard_fields:
                    dict_res[key] = res[key]
                else:
                    dict_res["fields"].update(res[key])

                if key in row:
                    del row[key]

        return RowDTO(
            raw_json=raw_row,
            name=dict_res.get("name", ""),
            clean_name=dict_res.get("clean_name", ""),
            address=dict_res.get("address", ""),
            clean_address=dict_res.get("clean_address", ""),
            country_code=dict_res.get("country_code", ""),
            sector=dict_res.get("sector", ""),
            fields=dict_res.get("fields", {}),
            errors=dict_res.get("errors", [])
        )
