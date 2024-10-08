from typing import List, Dict

from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)


class RowRequiredFieldsSerializer(RowSerializer):
    __primary_required_fields = {"name", "country"}
    __address_required_fields = {"address"}
    __coordinates_required_fields = {"lat", "lng"}

    __valid_field_value_lengths = {
        'name': 200,
        'address': 200,
    }

    def validate(self, row: dict, current: dict) -> dict:
        missing_primary_fields = self.__primary_required_fields.difference(
            row.keys()
        )
        has_address = self.__address_required_fields.issubset(row.keys())
        has_coordinates = self.__coordinates_required_fields.issubset(
            row.keys()
        )

        if not has_address and not has_coordinates:
            current["errors"].append(
                {
                    "message": "Either 'address' or both 'lat' and 'lng' "
                    "must be provided.",
                    "type": "Error",
                }
            )

        if missing_primary_fields:
            current["errors"].append(
                {
                    "message": "The following required fields are "
                    "missing: {}.".format(', '.join(missing_primary_fields)),
                    "type": "Error",
                }
            )

        field_value_length_errors = self.__validate_field_value_lengths(row)
        current['errors'].extend(field_value_length_errors)

        return current

    def __validate_field_value_lengths(self, input_row: Dict) -> List[Dict]:
        errors = []

        for field, max_length in self.__valid_field_value_lengths.items():
            if field in input_row:
                value_len = len(input_row[field])
                if value_len > max_length:
                    errors.append(
                        {
                            'message': (
                                'There is a problem with the {0}: '
                                'Ensure this value has at most {2} '
                                'characters. (it has {1})'
                            ).format(field, value_len, max_length),
                            'type': 'ValidationError',
                        }
                    )

        return errors
