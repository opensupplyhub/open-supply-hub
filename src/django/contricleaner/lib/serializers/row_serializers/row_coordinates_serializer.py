from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)


class RowCoordinatesSerializer(RowSerializer):
    __LAT_KEY = 'lat'
    __LNG_KEY = 'lng'
    __LAT_MIN = -90
    __LAT_MAX = 90
    __LNG_MIN = -180
    __LNG_MAX = 180

    def validate(self, row: dict, current: dict) -> dict:
        if self.__LAT_KEY in row and self.__LNG_KEY in row:
            lat_str = row.get(self.__LAT_KEY)
            lng_str = row.get(self.__LNG_KEY)

            if lat_str and lng_str:
                try:
                    lat = float(lat_str)
                    lng = float(lng_str)

                    if self.__is_valid_lat_lng(lat, lng):
                        current[self.__LAT_KEY] = lat
                        current[self.__LNG_KEY] = lng
                    else:
                        self.__set_none_coordinates(current)
                except ValueError:
                    self.__set_none_coordinates(current)
            else:
                self.__set_none_coordinates(current)

        return current

    def __is_valid_lat_lng(self, lat: float, lng: float) -> bool:
        return (
            self.__LAT_MIN <= lat <= self.__LAT_MAX
            and self.__LNG_MIN <= lng <= self.__LNG_MAX
        )

    def __set_none_coordinates(self, current: dict) -> None:
        current[self.__LAT_KEY] = None
        current[self.__LNG_KEY] = None
