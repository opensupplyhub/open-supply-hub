from typing import List
import uuid
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class ModerationIdValidator(OpenSearchValidationInterface):
    @staticmethod
    def is_valid_uuid(value):
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False

    def validate_opensearch_params(self, data) -> List[dict]:
        errors: List[dict] = []
        moderation_id = data.get('moderation_id')

        if moderation_id is None:
            return errors

        if isinstance(moderation_id, list):
            invalid_ids = [
                id_value for id_value in moderation_id
                if not self.is_valid_uuid(id_value)
            ]
            if invalid_ids:
                errors.append({
                    "field": "moderation_id",
                    "detail": f"Invalid uuid(s): {', '.join(invalid_ids)}.",
                })
        elif isinstance(moderation_id, str):
            if not self.is_valid_uuid(moderation_id):
                errors.append({
                    "field": "moderation_id",
                    "detail": f"Invalid uuid: {moderation_id}.",
                })
        else:
            errors.append({
                "field": "moderation_id",
                "detail": (
                    "moderation_id must be a valid uuid or a list of uuids."
                )
            })

        return errors
