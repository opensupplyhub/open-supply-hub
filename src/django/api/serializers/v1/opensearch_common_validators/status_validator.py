from typing import List
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface
from api.constants import FacilityClaimStatuses

class StatusValidator(OpenSearchValidationInterface):
    VALID_CLAIM_STATUSES = {
        FacilityClaimStatuses.PENDING,
        FacilityClaimStatuses.APPROVED,
        FacilityClaimStatuses.DENIED,
        FacilityClaimStatuses.REVOKED,
    }

    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []
        status = data.get('status')

        if not status:
            return errors

        if not isinstance(status, list):
            errors.append({
                "field": "status",
                "detail": "Claim status must be a list of values."
            })

        elif not all(item in self.VALID_CLAIM_STATUSES for item in status):
            invalid_statuses = [item for item in status if item not in self.VALID_CLAIM_STATUSES]
            allowed_values = ', '.join(f"'{value}'" for value in self.VALID_CLAIM_STATUSES)
            errors.append({
                "field": "status",
                "detail": (
                    f"Invalid claim status(es) {invalid_statuses}. "
                    f"Allowed values are {allowed_values}."
                )
            })

        return errors
