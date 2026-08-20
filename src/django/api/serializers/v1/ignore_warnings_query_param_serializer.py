from rest_framework.serializers import CharField, Serializer
from rest_framework.exceptions import ValidationError


class IgnoreWarningsQueryParamSerializer(Serializer):
    ignore_warnings = CharField(required=False, default='false')

    def validate_ignore_warnings(self, value: str) -> bool:
        '''
        Only the literal strings "true" and "false" are accepted, unlike
        DRF's BooleanField (which also treats "1", "yes", "on", etc. as
        true). Since bypassing the submission-quality check is a
        deliberate user action, a permissive parser risks an unintended
        value (e.g. a stray "1" or "false") silently bypassing it.
        '''
        if value not in ('true', 'false'):
            raise ValidationError(
                'The ignore_warnings query parameter must be '
                'exactly "true" or "false".'
            )

        return value == 'true'
