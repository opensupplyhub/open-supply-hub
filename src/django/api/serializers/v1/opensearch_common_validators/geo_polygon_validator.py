import logging
from typing import List
from api.serializers.v1.opensearch_validation_interface import (
    OpenSearchValidationInterface,
)

logger = logging.getLogger(__name__)

class GeoPolygonValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors: List[dict] = []

        logger.info(f'### data for geo_polygon in validator {data}')

        try:
            lat, lon = map(float, data.split(","))
        except ValueError:
            errors.append(f"Invalid geo_polygon format: {data}. Expected 'lat,lon'.")

        if not (-90 <= lat <= 90):
            errors.append(f"Invalid latitude {lat}. Must be between -90 and 90.")
        if not (-180 <= lon <= 180):
            errors.append(f"Invalid longitude {lon}. Must be between -180 and 180.")

        return errors
