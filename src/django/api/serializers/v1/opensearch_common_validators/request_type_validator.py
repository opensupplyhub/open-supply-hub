from typing import List
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class RequestTypeValidator(OpenSearchValidationInterface):
    VALID_REQUEST_TYPES = {'CREATE', 'UPDATE', 'CLAIM'}

    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []
        request_type = data.get('request_type')

        if not request_type:
            return errors
        if not isinstance(request_type, list):
            errors.append({
                "field": "request_type",
                "detail": "Request type must be a list of values."
            })
        elif not all(
            item in self.VALID_REQUEST_TYPES
            for item in request_type
        ):
            invalid_request_types = [item for item in request_type if
                                     item not in self.VALID_REQUEST_TYPES]
            # Format allowed values in uppercase
            allowed_values = ', '.join(
                f"'{value}'" for value in self.VALID_REQUEST_TYPES
            )
            errors.append({
                "field": "request_type",
                "detail": (
                    f"Invalid request type(s) {invalid_request_types}. "
                    f"Allowed values are {allowed_values}."
                )
            })
        return errors
