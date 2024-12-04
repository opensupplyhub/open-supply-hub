from typing import List
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class DateRangeValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []

        date_gte = data.get('date_gte')
        date_lt = data.get('date_lt')

        if date_gte and date_lt and date_gte > date_lt:
            errors.append({
                "field": "date_gte",
                "detail": (
                    "The 'date_gte' must be "
                    "less than or equal to 'date_lt'."
                )
            })

        return errors
