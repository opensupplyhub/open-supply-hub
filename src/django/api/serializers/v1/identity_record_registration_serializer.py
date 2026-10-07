from django.core.validators import URLValidator
from rest_framework import serializers


class IdentityRecordRegistrationSerializer(serializers.Serializer):
    """
    Request body for registering an external record against an OS ID.

    Shape is fixed by Section 3.2 of the OS Hub technical scope doc. The
    issuer and the registrant are building their FR-05 call against it, so
    do not change it without telling them.
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
    # The registrant's own handle for the location. Useful to them for
    # reconciliation and carried through unchanged, but Open Supply Hub
    # resolves on the OS ID alone, so it is not required.
    registrant_reference = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        default='',
    )

    def validate_resolver_uri(self, value):
        """
        Reject a Credential URL presented as a Resolver URI where we can
        tell the difference.

        Registering a Credential URL points at one specific version and
        silently breaks the always-current guarantee in Section 3.3, which
        is the whole premise of the pilot. Credential URLs in this pilot
        address a document directly, so a .json suffix catches the obvious
        mistake. This is a guard against the common error, not a
        general-purpose detector: a Credential URL served without that
        suffix would still pass.
        """
        if value.endswith('.json'):
            raise serializers.ValidationError(
                'This looks like a Credential URL rather than a Resolver '
                'URI. Register the resolver link, which stays current as '
                'new versions are issued, never a link to one version '
                '(FR-06, scope doc 3.3).'
            )
        return value
