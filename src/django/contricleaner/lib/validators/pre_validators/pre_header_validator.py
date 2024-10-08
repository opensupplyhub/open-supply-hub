from typing import List

from contricleaner.lib.validators.pre_validators \
    .pre_validator import PreValidator


class PreHeaderValidator(PreValidator):
    __primary_required_fields = {"name", "country"}
    __address_required_fields = {"address"}
    __coordinates_required_fields = {"lat", "lng"}

    def validate(self, rows: List[dict]) -> dict:
        missing_fields = []

        for row in rows:
            raw_row = row

            missing_primary_fields = self.__primary_required_fields.difference(
                raw_row.keys()
            )
            if missing_primary_fields:
                missing_fields.extend(missing_primary_fields)

            has_address = self.__address_required_fields.issubset(
                raw_row.keys()
            )
            has_coordinates = self.__coordinates_required_fields.issubset(
                raw_row.keys()
            )

            if not (has_address or has_coordinates):
                missing_fields.append("address or both lat and lng")

            if not missing_fields:
                return {}

        return {
            "message": "The following required fields are missing: {}".format(
                ', '.join(missing_fields)
            ),
            "type": "Error",
        }
