from typing import List
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class PercentOfFemaleWorkersValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []

        percent_female_workers_min = data.get('percent_female_workers_min')
        percent_female_workers_max = data.get('percent_female_workers_max')

        if (percent_female_workers_min is not None and
                percent_female_workers_max is None) or (
                percent_female_workers_min is None and
                percent_female_workers_max is not None):
            errors.append({
                "field": "percent_female_workers",
                "detail": "Both min and max percentages must be provided."
            })

        if percent_female_workers_min is not None and \
                percent_female_workers_max is not None:
            if not (0 < percent_female_workers_min <= 100) or not (
                    0 < percent_female_workers_max <= 100):
                errors.append({
                    "field": "percent_female_workers",
                    "detail": "Percentages must be between 0 and 100."
                })
            if percent_female_workers_min > percent_female_workers_max:
                errors.append({
                    "field": "percent_female_workers",
                    "detail": (
                        "Minimum percentage must be less than or equal to "
                        "maximum percentage."
                    )
                })

        return errors
