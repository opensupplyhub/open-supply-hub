from rest_framework import serializers


class CoordinatesSerializer(serializers.Serializer):
    lat = serializers.FloatField(
        required=True,
        error_messages={
            'required': "Both latitude and longitude must be provided.",
        },
    )
    lng = serializers.FloatField(
        required=True,
        error_messages={
            'required': "Both latitude and longitude must be provided."
        },
    )

    def validate(self, data):
        errors = []

        lat = data.get('lat') if 'lat' in data else None
        lng = data.get('lng') if 'lng' in data else None

        if lat is not None and not (-90 <= lat <= 90):
            errors.append({
                "field": "coordinates",
                "detail": "Latitude must be between -90 and 90 degrees."
            })

        if lng is not None and not (-180 <= lng <= 180):
            errors.append({
                "field": "coordinates",
                "detail":
                    "Longitude must be between -180 and 180 degrees."
            })

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data
