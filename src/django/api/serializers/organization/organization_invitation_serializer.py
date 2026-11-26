from rest_framework import serializers

from api.models.organization.organization_invitation import (
    OrganizationInvitation,
)
from api.models.organization.organization_membership import (
    OrganizationMembership,
)


class OrganizationInvitationSerializer(serializers.ModelSerializer):
    organization_uuid = serializers.UUIDField(
        source='organization.uuid', read_only=True
    )
    organization_name = serializers.CharField(
        source='organization.name', read_only=True
    )
    invited_by_email = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationInvitation
        fields = (
            'uuid',
            'email',
            'role',
            'status',
            'expires_at',
            'responded_at',
            'created_at',
            'organization_uuid',
            'organization_name',
            'invited_by_email',
        )

    def get_invited_by_email(self, invitation):
        return invitation.invited_by.email if invitation.invited_by else None

    def get_status(self, invitation):
        # A pending invitation past its time reads as expired even
        # before the lazy clean-up has rewritten the row.
        if (
            invitation.status == OrganizationInvitation.PENDING
            and invitation.is_expired
        ):
            return OrganizationInvitation.EXPIRED
        return invitation.status


class OrganizationInvitationCreateSerializer(serializers.Serializer):
    """
    Body of POST .../invitations/: the email of an existing OS Hub
    account and the role it gets on accepting.
    """
    email = serializers.EmailField(required=True, allow_blank=False)
    role = serializers.ChoiceField(
        choices=OrganizationMembership.ROLE_CHOICES,
        required=False,
        default=OrganizationMembership.MEMBER,
    )

    def validate_email(self, value):
        return value.strip().lower()
