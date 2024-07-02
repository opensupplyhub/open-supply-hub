from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer
)


class RowCoordinatesSerializer(RowSerializer):
    def validate(self, row: dict, current: dict) -> dict:
        lat_str = row.get('lat')
        lng_str = row.get('lng')

        if not lat_str and not lng_str:
            return current

        if not lat_str or not lng_str:
            current['lat'] = None
            current['lng'] = None
            return current

        try:
            lat = float(lat_str)
            lng = float(lng_str)

            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                current['lat'] = None
                current['lng'] = None
            else:
                current['lat'] = lat
                current['lng'] = lng

        except ValueError:
            current['lat'] = None
            current['lng'] = None

        return current
