import re
from api.serializers.v1.opensearch_validation_interface \
    import OpenSearchValidationInterface


class ModerationIdValidator(OpenSearchValidationInterface):
    UUID_REGEX = (
        r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
        r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )

    def validate_opensearch_params(self, data):
        errors = []
        moderation_id = data.get('moderation_id')

        if moderation_id is None:
            return errors

        if isinstance(moderation_id, list):
            invalid_ids = [
                mid for mid in moderation_id
                if not re.match(self.UUID_REGEX, mid)
            ]
            if invalid_ids:
                errors.append({
                    "field": "moderation_id",
                    "message": (
                        f"Invalid UUID(s): {invalid_ids}."
                        "Each ID must be a valid UUID."
                    )
                })
        elif isinstance(moderation_id, str):
            if not re.match(self.UUID_REGEX, moderation_id):
                errors.append({
                    "field": "moderation_id",
                    "message": "Must be a valid UUID."
                })
        else:
            errors.append({
                "field": "moderation_id",
                "message": "Must be a valid UUID or a list of UUIDs."
            })

        return errors
