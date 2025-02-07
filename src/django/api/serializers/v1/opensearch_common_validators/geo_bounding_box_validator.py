from api.serializers.v1.opensearch_validation_interface import (
    OpenSearchValidationInterface,
)


class GeoBoundingBoxValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors = []

        fields = ['top', 'left', 'bottom', 'right']
        coords = {
            field: data.get(f'geo_bounding_box_{field}') for field in fields
        }

        if any(value is not None for value in coords.values()) and not all(
            value is not None for value in coords.values()
        ):
            errors.append(
                {
                    "field": "geo_bounding_box",
                    "detail": "All coordinates (top, left, bottom, right) "
                    "must be provided.",
                }
            )

            return errors

        if not any(value is not None for value in coords.values()):
            return errors

        range_limits = {
            'top': (-90, 90),
            'bottom': (-90, 90),
            'left': (-180, 180),
            'right': (-180, 180),
        }

        for field, (min_val, max_val) in range_limits.items():
            value = coords[field]

            if value < min_val or value > max_val:
                errors.append(
                    {
                        "field": "geo_bounding_box",
                        "detail": f"The {field} value must be between {min_val} and {max_val}.",
                    }
                )

        if coords['top'] <= coords['bottom']:
            errors.append(
                {
                    "field": "geo_bounding_box",
                    "detail": "The top must be greater than bottom.",
                }
            )

        if coords['right'] <= coords['left']:
            errors.append(
                {
                    "field": "geo_bounding_box",
                    "detail": "The right must be greater than left.",
                }
            )

        return errors
