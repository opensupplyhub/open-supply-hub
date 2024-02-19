from typing import List
from contricleaner.lib.dto.header_dto import HeaderDTO


class HeaderNoDuplicationsValidator:
    def validate(self, raw_header: List[str]) -> dict:
        if len(raw_header) > len(set(raw_header)):
            return {
                "error": {
                    "message": "One or more fields are duplicated",
                    "type": "Error",
                }
            }
        return {}


class HeaderRequredValidator:
    required_fields = {"name", "address"}

    def validate(self, raw_header: List[str]) -> dict:
        if set(raw_header).intersection(HeaderRequredValidator.required_fields) != set(
            HeaderRequredValidator.required_fields
        ):
            return {
                "error": {
                    "message": "'name' or 'address' are missing",
                    "type": "Error",
                },
            }
        return {}


class HeaderFieldsValidator:
    def validate(self, raw_header: List[str]) -> dict:
        return {
            "fields": set(raw_header),
        }


class HeaderNonStandardFieldsValidator:
    standard_fields = [
        "sector",
        "country",
        "name",
        "address",
        "lat",
        "lng",
    ]

    def validate(self, raw_header: List[str]) -> dict:
        return {
            "non_standard_fields": set(raw_header).difference(
                HeaderNonStandardFieldsValidator.standard_fields
            ),
        }


class HeaderCompositeValidator:
    def __init__(self):
        self.validators = [
            HeaderNonStandardFieldsValidator(),
            HeaderFieldsValidator(),
            HeaderRequredValidator(),
            HeaderNoDuplicationsValidator(),
        ]

    def get_validated_header(self, raw_header: List[str]) -> HeaderDTO:
        header_dict = {
            "raw_header": raw_header,
            "fields": set(),
            "non_standard_fields": set(),
            "errors": [],
        }
        raw_header_lowecased = list(map(str.lower, raw_header))
        for validator in self.validators:
            res = validator.validate(raw_header_lowecased)

            if "error" in res:
                header_dict["errors"].append(res["error"])

            if "fields" in res:
                header_dict["fields"].update(res["fields"])

            if "non_standard_fields" in res:
                header_dict["non_standard_fields"].update(res["non_standard_fields"])

        return HeaderDTO(
            raw_header=raw_header,
            fields=header_dict["fields"],
            errors=header_dict["errors"],
            non_standard_fields=header_dict["non_standard_fields"],
        )
