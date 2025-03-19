import logging
from typing import List
from api.serializers.v1.opensearch_validation_interface import (
    OpenSearchValidationInterface,
)
from api.constants import CoordinateLimits

logger = logging.getLogger(__name__)

class GeoPolygonValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors: List[dict] = []
        geo_polygon_data = data['geo_polygon'][0]

        try:
            lat, lon = map(float, geo_polygon_data.split(","))
        except ValueError:
            errors.append({f"Invalid geo_polygon format: {geo_polygon_data}. Expected 'lat,lon'."})

        if not (CoordinateLimits.LAT_MIN <= lat <= CoordinateLimits.LAT_MAX):
            errors.append({
                "field": "geo_polygon",
                "detail": f"Invalid latitude {lat}. Must be between -90 and 90."
            })
        if not (CoordinateLimits.LNG_MIN <= lon <= CoordinateLimits.LNG_MAX):
            errors.append({
                "field": "geo_polygon",
                "detail": f"Invalid longitude {lon}. Must be between -180 and 180."
            })

        logger.info(f'$$$ errors {errors}')
        return errors
