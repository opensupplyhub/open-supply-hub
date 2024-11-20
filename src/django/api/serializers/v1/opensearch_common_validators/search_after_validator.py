from typing import List
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface

class SearchAfterValidator(OpenSearchValidationInterface):
    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []
        search_after = data.get('search_after')

        if search_after is None:
            return errors

        search_after_values = search_after.split(',')
        if len(search_after_values) != 2:
            errors.append({
                "field": "search_after",
                "message": (
                    "The search_after parameter must contain exactly two values."
                )
            })
            return errors

        return errors
