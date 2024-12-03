from typing import List
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class RequestTypeValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []
        request_type = data.get('request_type')

        if not request_type:
            return errors

        valid_request_types = {'CREATE', 'UPDATE', 'CLAIM'}

        if request_type not in valid_request_types:
            errors.append({
                "field": "request_type",
                "detail": f"'{request_type}' is not a valid request_type. \
                    Allowed values are 'CREATE', 'UPDATE' or 'CLAIM'."
            })

        return errors
