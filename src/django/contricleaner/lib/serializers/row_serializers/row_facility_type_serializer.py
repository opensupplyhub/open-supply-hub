from contricleaner.lib.serializers.row_serializers.row_serializer \
    import RowSerializer


class RowFacilityTypeSerializer(RowSerializer):

    def validate(self, row: dict, current: dict) -> dict:
        # facility_type_processing_type is a special "meta" field that
        # attempts to simplify the submission process for contributors.
        if (row.get('facility_type_processing_type')):
            if row.get('facility_type') is None:
                current['facility_type'] = row['facility_type_processing_type']
            if row.get('processing_type') is None:
                current['processing_type'] = row['facility_type_processing_type']
        # Add a facility_type extended field if the user only
        # submitted a processing_type
        elif (row.get('processing_type') and
                row.get('facility_type') is None):
            current['facility_type'] = row['processing_type']
        # Add a processing_type extended field if the user only
        # submitted a facility_type
        elif (row.get('facility_type') and
                row.get('processing_type') is None):
            current['processing_type'] = row['facility_type']

        return current
