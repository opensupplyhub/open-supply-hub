from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class CoordinatesValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors = []

        lat = data.get('coordinates_lat')
        lng = data.get('coordinates_lng')

        if ((lat is not None and lng is None) or
                (lat is None and lng is not None)):
            errors.append({
                "field": "coordinates",
                "message": "Both latitude and longitude must be provided."
            })

        if lat is not None:
            if not (-90 <= lat <= 90):
                errors.append({
                    "field": "coordinates",
                    "message": "Latitude must be between -90 and 90 degrees."
                })

        if lng is not None:
            if not (-180 <= lng <= 180):
                errors.append({
                    "field": "coordinates",
                    "message":
                        "Longitude must be between -180 and 180 degrees."
                })

        return errors
