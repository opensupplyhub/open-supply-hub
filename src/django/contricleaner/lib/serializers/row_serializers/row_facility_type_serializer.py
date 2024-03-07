from contricleaner.lib.helpers.split_values import split_values
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

        if not any(
            (facility_type, processing_type, facility_type_processing_type)
        ):
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

    @staticmethod
    def create_values(value):
        return {
            'raw_values': value,
            'processed_values': split_values(value, '|'),
        }
