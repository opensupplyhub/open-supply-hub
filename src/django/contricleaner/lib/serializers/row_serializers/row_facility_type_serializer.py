from typing import Union
from contricleaner.lib.helpers.is_valid_type import (
    is_valid_type,
)
from contricleaner.lib.helpers.split_values import split_values
from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)


class RowFacilityTypeSerializer(RowSerializer):
    def __init__(self, split_pattern: str) -> None:
        self.split_pattern = split_pattern

    def validate(self, row: dict, current: dict) -> dict:
        facility_type = row.get('facility_type')
        processing_type = row.get('processing_type')
        facility_type_processing_type = row.get(
            'facility_type_processing_type'
        )

        if not any(
            (facility_type, processing_type, facility_type_processing_type)
        ):
            return current

        facility_type_errors = []

        fields = [
            'facility_type',
            'processing_type',
            'facility_type_processing_type',
        ]
        for field, value in zip(
            fields,
            [facility_type, processing_type, facility_type_processing_type],
        ):
            if value and not is_valid_type(value):
                facility_type_errors.append(
                    {
                        'message': 'Expected value for {} to be a string '
                        'or a list of strings but '
                        'got {}.'.format(field, value),
                        'field': field,
                        'type': 'ValueError',
                    }
                )

        if facility_type_errors:
            current['errors'].extend(facility_type_errors)
            return current

        if facility_type_processing_type:
            if facility_type is None:
                facility_type = facility_type_processing_type

            if processing_type is None:
                processing_type = facility_type_processing_type

        elif processing_type and not facility_type:
            facility_type = processing_type

        elif facility_type and not processing_type:
            processing_type = facility_type

        current['facility_type'] = self.create_values(facility_type)
        current['processing_type'] = self.create_values(processing_type)

        return current

    def create_values(self, value: Union[str, list, set]) -> dict:
        return {
            'raw_values': value,
            'processed_values': split_values(value, self.split_pattern),
        }
