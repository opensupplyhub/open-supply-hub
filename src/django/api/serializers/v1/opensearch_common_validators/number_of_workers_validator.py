from typing import List
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class NumberOfWorkersValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []

        min_value = data.get('number_of_workers_min')
        max_value = data.get('number_of_workers_max')

        if ((min_value is not None and max_value is None) or
                (min_value is None and max_value is not None)):
            errors.append({
                "field": "number_of_workers",
                "detail": (
                    "The value must be a valid object with `min` and `max` "
                    "properties."
                )
            })

        if (min_value is not None and max_value is not None and
                min_value > max_value):
            errors.append({
                "field": "number_of_workers",
                "detail": (
                    "Minimum value must be less than or equal "
                    "to maximum value."
                )
            })

        return errors
