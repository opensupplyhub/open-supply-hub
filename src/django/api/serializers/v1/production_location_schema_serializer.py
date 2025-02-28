import logging


import bleach
from api.serializers.v1.coordinates_serializer \
    import CoordinatesSerializer
from api.serializers.v1.number_of_workers_serializer \
    import NumberOfWorkersSerializer
from api.serializers.v1.string_or_list_field import StringOrListField
from django.core.validators import RegexValidator
from rest_framework import serializers

logger = logging.getLogger(__name__)
class ProductionLocationSchemaSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=200,
        required=True,
        error_messages={
            'required': 'Field name is required!',
            'invalid': 'Field name must be a valid string.',
            'max_length': 'Field name cannot be longer than 200 characters.'
        },
    )
    address = serializers.CharField(
        max_length=200,
        required=True,
        error_messages={
            'required': 'Field address is required!',
            'invalid': 'Field address must be a valid string.',
            'max_length': 'Field address cannot be longer than 200 characters.'
        },
    )
    country = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Field country is required!',
            'invalid': 'Field country must be a valid string.'
        },
    )
    sector = StringOrListField(required=False)
    parent_company = serializers.CharField(required=False)
    product_type = StringOrListField(required=False)
    location_type = StringOrListField(required=False)
    processing_type = StringOrListField(required=False)
    number_of_workers = NumberOfWorkersSerializer(
        required=False,
        validators=[NumberOfWorkersSerializer.validate_object],
        error_messages={
            'invalid': 'Invalid data. Expected a dictionary(object).'
        },
    )
    coordinates = CoordinatesSerializer(
        required=False,
        error_messages={
            'required': 'The lat and lng fields are required!',
            'invalid': 'Field coordinates must be a valid geopoint.'
        },
    )

    def __sanitize_check(self, field, value):
        invalid_input_data_msg = {
            "field": field,
            "detail": "Invalid input data"
        }

        def raise_sanitize_error():
            raise serializers.ValidationError([invalid_input_data_msg])

        if isinstance(value, list):
            sanitized_list = [bleach.clean(str(item)) for item in value]
            '''
            Force bleach module to omit ampersand but preserve other checks
            https://github.com/mozilla/bleach/issues/192
            '''
            sanitized_list = [item.replace('&amp;', '&') for item in sanitized_list]
            sanitized_list = [bleach.clean(str(item).replace('"', 'QUOTE')) for item in value]
            sanitized_list = [item.replace('QUOTE', '"') for item in sanitized_list]
            if sanitized_list != value:
                raise_sanitize_error()
            return sanitized_list

        elif isinstance(value, str):
            value_updated = value.replace('"', 'QUOTE')
            print(f'Updated value with changed QUOTE: {value_updated}')
            sanitized_value = bleach.clean(value_updated)
            sanitized_value = sanitized_value.replace('&amp;', '&')
            sanitized_value = sanitized_value.replace('QUOTE', '"')
            print(f'### sanitized value is: {sanitized_value}')
            print(f'### initial value is: {value}')
            '''
            Double quotes will be removed by bleach and ContriCleaner,
            see CompositeRowSerializer.__remove_double_quotes()
            so we have to re-insert them to avoid triggering errors on this level
            '''
            if sanitized_value != value:
                raise_sanitize_error()
            return sanitized_value

    def __sanitize_all_fields(self, data):
        for field, value in data.items():
            if value is not None:
                data[field] = self.__sanitize_check(field, value)
        return data

    def __validate_string_only_field(self, data, errors):
        for field in ['name', 'address', 'country']:
            if data.get(field) and data[field].isdigit():
                errors.append({
                    "field": field,
                    "detail": f"Field {field} must be a string, not a number."
                })

        return errors

    def validate(self, data):
        data = self.__sanitize_all_fields(data)

        # TODO: refactor error array to keep errors from self.__sanitize_all_fields
        errors = []

        self.__validate_string_only_field(data, errors)

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data
