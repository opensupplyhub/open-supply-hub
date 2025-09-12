from api.serializers.v1.coordinates_serializer \
  import CoordinatesSerializer
from api.serializers.v1.number_of_workers_serializer \
  import NumberOfWorkersSerializer
from api.serializers.v1.string_or_list_field import StringOrListField
from rest_framework import serializers


class ProductionLocationSchemaSerializer(serializers.Serializer):
    abstract = True
    core_fields = ('name', 'address', 'country')

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
        max_length=200,
        required=False,
        error_messages={
            'invalid': 'Field parent_company must be a valid string.'
        },
    )
    product_type = StringOrListField(required=False)
    location_type = StringOrListField(required=False)
    processing_type = StringOrListField(required=False)
    number_of_workers = NumberOfWorkersSerializer(required=False)
    coordinates = CoordinatesSerializer(
        required=False,
        error_messages={
            'required': 'The lat and lng fields are required!',
            'invalid': 'Field coordinates must be a valid geopoint.'
        },
    )

    # Use only subclasses.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__class__ is ProductionLocationSchemaSerializer:
            raise TypeError(
                'ProductionLocationSchemaSerializer is abstract;'
                ' use a concrete subclass.'
            )

    def set_core_required(self, required: bool) -> None:
        for f in self.core_fields:
            if f in self.fields:
                self.fields[f].required = required

    def _validate_string_field(self, data, field_name):
        if (
            field_name in data and
            isinstance(data[field_name], str) and
            data[field_name].isdigit()
        ):
            return {
                "field": field_name,
                "detail": f"Field {field_name} must be a string, not a number."
            }
        return None

    def validate(self, data):
        errors = []
        for f in self.core_fields:
            err = self._validate_string_field(data, f)
            if err:
                errors.append(err)

        err = self._validate_string_field(data, 'parent_company')
        if err:
            errors.append(err)

        if errors:
            raise serializers.ValidationError(errors)
        return data
