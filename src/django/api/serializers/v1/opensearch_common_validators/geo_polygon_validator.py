from typing import List
from api.serializers.v1.opensearch_validation_interface import (
    OpenSearchValidationInterface,
)
from api.constants import CoordinateLimits


class GeoPolygonValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors: List[dict] = []

        geo_polygon_data = data.get('geo_polygon', [])
        if not isinstance(geo_polygon_data, list):
            errors.append({
                "field": "geo_polygon",
                "detail": "geo_polygon must be a list of coordinates."
            })
            return errors

        if geo_polygon_data and len(geo_polygon_data) < 3:
            errors.append({
                "field": "geo_polygon",
                "detail": (
                    "At least 3 points are required in "
                    "geo_polygon to form a valid polygon."
                )
            })

        for point in geo_polygon_data:
            try:
                lat, lon = map(float, point.split(","))
            except (ValueError, TypeError):
                errors.append({
                    "field": "geo_polygon",
                    "detail": (
                        f"Invalid coordinate format: {point}, "
                        "must be 'lat,lon' as floats"
                    )
                })
                continue

            if not (
                CoordinateLimits.LAT_MIN <=
                lat <=
                CoordinateLimits.LAT_MAX
            ):
                errors.append({
                    "field": "geo_polygon",
                    "detail": (
                        f"Invalid latitude {lat}, "
                        "must be between -90 and 90."
                    )
                })

            if not (
                CoordinateLimits.LNG_MIN <=
                lon <=
                CoordinateLimits.LNG_MAX
            ):
                errors.append({
                    "field": "geo_polygon",
                    "detail": (
                        f"Invalid longitude {lon}, "
                        "must be between -180 and 180."
                    )
                })

        return errors
