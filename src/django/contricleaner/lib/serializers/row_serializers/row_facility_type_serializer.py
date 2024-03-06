from typing import Union, List
from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)


class RowFacilityTypeSerializer(RowSerializer):

    def validate(self, row: dict, current: dict) -> dict:
        facility_type = row.get('facility_type')
        processing_type = row.get('processing_type')
        facility_type_processing_type = row.get(
            'facility_type_processing_type'
        )

        # facility_type_processing_type is a special "meta" field that
        # attempts to simplify the submission process for contributors.
        if facility_type_processing_type:
            if facility_type is None:
                facility_type = facility_type_processing_type

            if processing_type is None:
                processing_type = facility_type_processing_type

        # Add a facility_type extended field if the user only
        # submitted a processing_type
        elif processing_type and not facility_type:
            facility_type = processing_type
        # Add a processing_type extended field if the user only
        # submitted a facility_type
        elif facility_type and not processing_type:
            processing_type = facility_type

        current['facility_type'] = self.split_values(facility_type)
        current['processing_type'] = self.split_values(processing_type)

        return current

    @staticmethod
    def split_values(value: Union[str, list]) -> List[str]:
        if isinstance(value, str):
            return value.split('|')
        elif isinstance(value, list):
            return value
        else:
            raise ValueError("Unsupported value type: {}".format(type(value)))
