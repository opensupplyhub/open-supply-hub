from typing import List
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class ClaimStatusValidator(OpenSearchValidationInterface):
    VALID_CLAIM_STATUSES = {
        'unclaimed',
        'claimed',
        'pending',
    }

    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []
        claim_status = data.get('claim_status')

        if not claim_status:
            return errors

        if isinstance(claim_status, str):
            claim_status = [claim_status]

        if not isinstance(claim_status, list):
            errors.append({
                "field": "claim_status",
                "detail": "Claim status must be a string or list of values."
            })

        elif not all(
            item in self.VALID_CLAIM_STATUSES for item in claim_status
        ):
            invalid_statuses = [
                item for item in claim_status if
                item not in self.VALID_CLAIM_STATUSES
            ]
            allowed_values = ', '.join(
                f"'{value}'" for value in self.VALID_CLAIM_STATUSES
            )
            errors.append({
                "field": "claim_status",
                "detail": (
                    f"Invalid claim status(es) {invalid_statuses}, "
                    f"allowed values are {allowed_values}."
                )
            })

        return errors
