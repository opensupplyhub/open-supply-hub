from contricleaner.lib.helpers.clean import clean
from contricleaner.lib.serializers.row_serializers.row_serializer import (
    RowSerializer,
)


class RowGeolocationSerializer(RowSerializer):
    __ADDRESS_KEY = 'address'
    __CLEAN_ADDRESS_KEY = 'clean_address'
    __LAT_KEY = 'lat'
    __LNG_KEY = 'lng'
    __LAT_MIN = -90
    __LAT_MAX = 90
    __LNG_MIN = -180
    __LNG_MAX = 180

    def validate(self, row: dict, current: dict) -> dict:
        address = row.get(self.__ADDRESS_KEY)
        lat_str = row.get(self.__LAT_KEY)
        lng_str = row.get(self.__LNG_KEY)

        clean_address = clean(address) if address else None
        valid_lat_lng = self.__is_valid_lat_lng(lat_str, lng_str)

        if address and lat_str and lng_str:
            return self.__handle_full_data(
                clean_address, lat_str, lng_str, current, valid_lat_lng
            )

        if not address and lat_str and lng_str:
            return self.__handle_lat_lng_only(
                lat_str, lng_str, current, valid_lat_lng
            )

        if address and not (lat_str and lng_str):
            return self.__handle_address_only(clean_address, current)

        return current

    def __is_valid_lat_lng(self, lat_str: str, lng_str: str) -> bool:
        try:
            lat = float(lat_str)
            lng = float(lng_str)
            return (
                self.__LAT_MIN <= lat <= self.__LAT_MAX
                and self.__LNG_MIN <= lng <= self.__LNG_MAX
            )
        except (ValueError, TypeError):
            return False

    def __handle_full_data(
        self, clean_address, lat_str, lng_str, current, valid_lat_lng
    ):
        if not clean_address and not valid_lat_lng:
            return self.__add_error(
                current, "Address and lat, lng are not valid"
            )

        if clean_address and not valid_lat_lng:
            current[self.__CLEAN_ADDRESS_KEY] = clean_address
            current[self.__LAT_KEY] = None
            current[self.__LNG_KEY] = None

        elif not clean_address and valid_lat_lng:
            current[self.__ADDRESS_KEY] = ''
            current[self.__CLEAN_ADDRESS_KEY] = ''
            current[self.__LAT_KEY] = float(lat_str)
            current[self.__LNG_KEY] = float(lng_str)

        else:
            current[self.__CLEAN_ADDRESS_KEY] = clean_address
            current[self.__LAT_KEY] = float(lat_str)
            current[self.__LNG_KEY] = float(lng_str)

        return current

    def __handle_lat_lng_only(self, lat_str, lng_str, current, valid_lat_lng):
        if valid_lat_lng:
            current[self.__ADDRESS_KEY] = ''
            current[self.__CLEAN_ADDRESS_KEY] = ''
            current[self.__LAT_KEY] = float(lat_str)
            current[self.__LNG_KEY] = float(lng_str)

        else:
            return self.__add_error(current, "Lat, lng are not valid")

        return current

    def __handle_address_only(self, clean_address, current):
        if not clean_address:
            return self.__add_error(current, "Address is not valid")

        current[self.__CLEAN_ADDRESS_KEY] = clean_address

        return current

    def __add_error(self, current, message):
        current['errors'].append({'message': message, 'type': 'Error'})

        return current
