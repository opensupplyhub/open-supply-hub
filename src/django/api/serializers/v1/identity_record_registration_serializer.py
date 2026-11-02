from django.core.validators import URLValidator
from rest_framework import serializers

# The record types an issuer may register.
#
# A serializer allowlist rather than `choices` on the model field, which
# Django only applies in `full_clean()` and so would not enforce here.
ACCEPTED_RECORD_TYPES = (
    'untp:DigitalFacilityRecord',
)


class IdentityRecordRegistrationSerializer(serializers.Serializer):
    """
    Request body for registering an external record against an OS ID.

    The issuer and the registrant are building their call against this
    shape, so do not change it without telling them.
    """

    resolver_uri = serializers.CharField(
        required=True,
        validators=[URLValidator(schemes=['https'])],
        error_messages={
            'required': 'Field resolver_uri is required!',
        },
    )
    record_type = serializers.CharField(
        required=True,
        max_length=200,
        error_messages={
            'required': 'Field record_type is required!',
        },
    )
    issuer = serializers.CharField(
        required=True,
        max_length=500,
        error_messages={
            'required': 'Field issuer is required!',
        },
    )
    # The registrant's own handle for the location. Open Supply Hub
    # resolves on the OS ID alone, so it is not required, and can be used
    # by the registrant for reconciliation.
    registrant_reference = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        default='',
    )

    def validate_record_type(self, value):
        """
        Accept only a record type we recognize, because the resolver
        republishes this value and the association is shown on the Open
        Supply Hub site. It fails closed, so the error names what is
        accepted rather than only reporting that the value is wrong.
        """
        if value not in ACCEPTED_RECORD_TYPES:
            raise serializers.ValidationError(
                'Unsupported record_type. Accepted values: {}.'.format(
                    ', '.join(ACCEPTED_RECORD_TYPES)
                )
            )
        return value

    def validate_resolver_uri(self, value):
        """
        Reject a Credential URL presented as a Resolver URI. A guard
        against the common mistake rather than a detector: a Credential
        URL served without a .json suffix still passes.
        """
        if value.endswith('.json'):
            raise serializers.ValidationError(
                'This looks like a Credential URL rather than a Resolver '
                'URI. Register the resolver link, which stays current as '
                'new versions are issued, never a link to one version.'
            )
        return value
