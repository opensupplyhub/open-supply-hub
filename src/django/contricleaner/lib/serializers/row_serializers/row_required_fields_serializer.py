from typing import Tuple

from .row_serializer import RowSerializer
from contricleaner.constants import VALID_FIELD_VALUE_LENGTHS


class RowRequiredFieldsSerializer(RowSerializer):
    required_fields = {"name",
                       "address",
                       "country"}

    fields_to_validate_length = ("name", "address")

    def validate(self, row: dict, current: dict) -> dict:
        diff = self.required_fields.difference(row.keys())

        if len(diff) > 0:
            current["errors"].append(
                {
                    "message": "{} are missing".format(', '.join(diff)),
                    "type": "Error",
                }
            )

        for field in self.fields_to_validate_length:
            if (field not in diff):
                value_len, is_valid_length = self.__check_field_value_length(
                    row[field], field)
                if not is_valid_length:
                    current["errors"].append(
                        {
                            "message": ("There is a problem with the {0}: "
                                        "Ensure this value has at most 200 "
                                        "characters. (it has {1})").format(
                                            field, value_len),
                            "type": "ValidationError",
                        }
                    )

        return current

    def __check_field_value_length(self, value: str,
                                   field: str) -> Tuple[int, bool]:
        value_len = len(value)
        is_valid_length = not value_len > VALID_FIELD_VALUE_LENGTHS[field]
        return (value_len, is_valid_length)
