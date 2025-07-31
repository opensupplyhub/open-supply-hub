from typing import List
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class ClaimDateRangeValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []

        claimed_at_gt = data.get('claimed_at_gt')
        claimed_at_lt = data.get('claimed_at_lt')

        if claimed_at_gt and claimed_at_lt and claimed_at_gt > claimed_at_lt:
            errors.append({
                "field": "claimed_at_gt",
                "detail": (
                    "The 'claimed_at_gt' must be "
                    "less than or equal to 'claimed_at_lt'."
                )
            })

        return errors
