from rest_framework.serializers import CharField, Serializer
from rest_framework.exceptions import ValidationError


class DuplicateOverrideQueryParamSerializer(Serializer):
    duplicate_override = CharField(required=False, default='false')

    def validate_duplicate_override(self, value: str) -> bool:
        '''
        Only the literal strings "true" and "false" are accepted, unlike
        DRF's BooleanField (which also treats "1", "yes", "on", etc. as
        true). Since bypassing the duplicate-submission check is a
        deliberate user action, a permissive parser risks an unintended
        value (e.g. a stray "1" or "false") silently bypassing it.
        '''
        if value not in ('true', 'false'):
            raise ValidationError(
                'The duplicate_override query parameter must be '
                'exactly "true" or "false".'
            )

        return value == 'true'
