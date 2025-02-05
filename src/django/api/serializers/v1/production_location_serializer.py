from api.serializers.v1.coordinates_serializer \
  import CoordinatesSerializer
from api.serializers.v1.number_of_workers_serializer \
  import NumberOfWorkersSerializer
from api.serializers.v1.string_or_list_field import StringOrListField
from django.core.validators import RegexValidator
from rest_framework import serializers


class ProductionLocationSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Name is a required field!',
            'invalid': 'Name must be a valid string.'
            },)
    address = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Address is a required field!',
            'invalid': 'Address must be a valid string.'
            },)
    country = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Country is a required field!',
            'invalid': 'Country must be a valid string.'
            },)
    sector = StringOrListField(required=False)
    parent_company = serializers.CharField(
        required=False,
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s.,&()-]*$',
                message="Parent company must contain only letters, numbers, \
                    spaces, and allowed symbols (, . & - ())."
            )
        ],
        error_messages={
            'max_length': 'Parent company cannot exceed 255 characters!',
            'invalid': 'Parent company must be a valid string.'
            },)
    product_type = StringOrListField(required=False)
    location_type = StringOrListField(required=False)
    processing_type = StringOrListField(required=False)
    number_of_workers = NumberOfWorkersSerializer(
        required=False,
        error_messages={
            'required': 'Min and Max is a required fields!',
            'invalid': 'Number of workers must be a valid range.'
        },)
    coordinates = CoordinatesSerializer(
        required=False,
        error_messages={
            'required': 'Lat and Lng are required fields!',
            'invalid': 'Coordinates must be a valid geo point.'
        },)

    def validate(self, data):
        errors = []

        if data.get('name').isdigit():
            errors.append({
                "field": "name",
                "detail": "Name must be a string, not a number"
            },)

        if data.get('address').isdigit():
            errors.append({
                "field": "address",
                "detail": "Address must be a string, not a number"
            },)

        if data.get('country').isdigit():
            errors.append({
                "field": "country",
                "detail": "Country must be a string, not a number"
            },)

        if 'parent_company' in data and data.get('parent_company').isdigit():
            errors.append({
                "field": "parent_company",
                "detail": "Parent company must be a string, not a number"
            },)

        if len(errors) > 0:
            raise serializers.ValidationError(errors)
        return data
