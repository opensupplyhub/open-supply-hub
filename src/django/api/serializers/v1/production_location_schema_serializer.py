from api.serializers.v1.coordinates_serializer \
  import CoordinatesSerializer
from api.serializers.v1.number_of_workers_serializer \
  import NumberOfWorkersSerializer
from api.serializers.v1.string_or_list_field import StringOrListField
from django.core.validators import RegexValidator
from rest_framework import serializers


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
    parent_company = serializers.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[\p{L}\p{N}\s.,&()/@-]*$',
                message=("Field parent_company must contain only letters, "
                         "numbers, spaces, and allowed symbols (, . & - () / @).")
            )
        ],
        error_messages={
            'invalid': 'Field parent_company must be a valid string.'
        },
    )
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

    def _validate_string_field(self, data, field_name):
        """Helper method to validate string fields aren't numeric."""
        if field_name in data and data[field_name].isdigit():
            return {
                "field": field_name,
                "detail": f"Field {field_name} must be a string, not a number."
            }

        return None

    def validate(self, data):
        errors = []

        for field in ['name', 'address', 'country']:
            error = self._validate_string_field(data, field)
            if error:
                errors.append(error)

        error = self._validate_string_field(data, 'parent_company')
        if error:
            errors.append(error)

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data
