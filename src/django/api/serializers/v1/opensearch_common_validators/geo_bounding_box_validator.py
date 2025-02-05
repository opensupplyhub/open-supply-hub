import json
from api.serializers.v1.opensearch_validation_interface import (
    OpenSearchValidationInterface,
)


class GeoBoundingBoxValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors = []
        geo_bounding_box_str = data.get('geo_bounding_box')
        geo_bounding_box = (
            json.loads(geo_bounding_box_str) if geo_bounding_box_str else None
        )

        if geo_bounding_box:
            required_keys = ['top_right', 'bottom_left']
            for key in required_keys:
                if key not in geo_bounding_box:
                    errors.append(
                        {
                            "field": "geo_bounding_box",
                            "detail": (
                                "The value must be a valid object with "
                                "`top_right` and `bottom_left` properties."
                            ),
                        }
                    )

                if not isinstance(geo_bounding_box[key], dict):
                    errors.append(
                        {
                            "field": "geo_bounding_box",
                            "detail": (
                                "The value must be a valid object with "
                                "`lat` and `lon` properties."
                            ),
                        }
                    )

                for coord in ['lat', 'lon']:
                    if coord not in geo_bounding_box[key]:
                        errors.append(
                            {
                                "field": "geo_bounding_box",
                                "detail": (f"Missing {coord} in {key}."),
                            }
                        )

                    try:
                        value = float(geo_bounding_box[key][coord])
                    except ValueError:
                        errors.append(
                            {
                                "field": "geo_bounding_box",
                                "detail": (
                                    f"The '{coord}' in '{key}' must be "
                                    "a number."
                                ),
                            }
                        )

                    if coord == 'lat' and not (-90 <= value <= 90):
                        errors.append(
                            {
                                "field": "geo_bounding_box",
                                "detail": (
                                    f"The 'lat' in '{key}' must be between "
                                    "-90 and 90."
                                ),
                            }
                        )

                    if coord == 'lon' and not (-180 <= value <= 180):
                        errors.append(
                            {
                                "field": "geo_bounding_box",
                                "detail": (
                                    f"The 'lon' in '{key}' must be between "
                                    "-180 and 180."
                                ),
                            }
                        )

            if (
                geo_bounding_box['top_right']['lat']
                < geo_bounding_box['bottom_left']['lat']
            ):
                errors.append(
                    {
                        "field": "geo_bounding_box",
                        "detail": (
                            "Top right latitude must be greater than "
                            "bottom left latitude."
                        ),
                    }
                )

            if (
                geo_bounding_box['top_right']['lon']
                < geo_bounding_box['bottom_left']['lon']
            ):
                errors.append(
                    {
                        "field": "geo_bounding_box",
                        "detail": (
                            "Top right longitude must be greater than "
                            "bottom left longitude."
                        ),
                    }
                )

        return errors
