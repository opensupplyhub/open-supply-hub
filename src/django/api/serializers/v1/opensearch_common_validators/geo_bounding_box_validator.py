from api.serializers.v1.opensearch_validation_interface import (
    OpenSearchValidationInterface,
)


class GeoBoundingBoxValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data):
        errors = []

        top = data.get('geo_bounding_box_top')
        left = data.get('geo_bounding_box_left')
        bottom = data.get('geo_bounding_box_bottom')
        right = data.get('geo_bounding_box_right')

        bounding_box_fields = [top, left, bottom, right]

        if any(bounding_box_fields) and not all(bounding_box_fields):
            errors.append(
                {
                    "field": "geo_bounding_box",
                    "detail": (
                        "All of the following fields are required: "
                        "`geo_bounding_box_top`, `geo_bounding_box_left`, "
                        "`geo_bounding_box_bottom`, `geo_bounding_box_right`."
                    ),
                }
            )

        if all(bounding_box_fields):
            for coord in ['top', 'left', 'bottom', 'right']:
                value = data.get(f'geo_bounding_box_{coord}')

                if not value:
                    errors.append(
                        {
                            "field": "geo_bounding_box_{coord}",
                            "detail": (f"Missing geo_bounding_box_{coord}."),
                        }
                    )

                if coord in ['top', 'bottom'] and not (-90 <= value <= 90):
                    errors.append(
                        {
                            "field": f'geo_bounding_box_{coord}',
                            "detail": (
                                f"The 'geo_bounding_box_{coord}' must be "
                                "between -90 and 90."
                            ),
                        }
                    )

                if coord in ['left', 'right'] and not (-180 <= value <= 180):
                    errors.append(
                        {
                            "field": "geo_bounding_box_{coord}",
                            "detail": (
                                f"The 'geo_bounding_box_{coord}' must be "
                                "between -180 and 180."
                            ),
                        }
                    )

            if top <= bottom:
                errors.append(
                    {
                        "field": "geo_bounding_box_top",
                        "detail": (
                            "Top latitude must be greater than bottom latitude."
                        ),
                    }
                )

            if right <= left:
                errors.append(
                    {
                        "field": "geo_bounding_box_right",
                        "detail": (
                            "Right longitude must be greater than left longitude."
                        ),
                    }
                )

        return errors
