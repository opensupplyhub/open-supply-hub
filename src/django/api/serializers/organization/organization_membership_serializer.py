from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from api.models.organization.organization_membership import (
    OrganizationMembership,
)


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    email = serializers.SerializerMethodField()
    contributor_id = serializers.SerializerMethodField()
    contributor_name = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationMembership
        fields = (
            'uuid',
            'role',
            'status',
            'joined_at',
            'user_id',
            'email',
            'contributor_id',
            'contributor_name',
            'is_self',
        )

    @staticmethod
    def _contributor(membership):
        try:
            return membership.user.contributor
        except ObjectDoesNotExist:
            return None

    def get_email(self, membership):
        return membership.user.email

    def get_contributor_id(self, membership):
        contributor = self._contributor(membership)
        return contributor.id if contributor else None

    def get_contributor_name(self, membership):
        contributor = self._contributor(membership)
        return contributor.name if contributor else None

    def get_is_self(self, membership):
        request = self.context.get('request')
        return bool(request and request.user.id == membership.user_id)


class OrganizationMembershipUpdateSerializer(serializers.Serializer):
    """Body of PATCH .../members/{uuid}/: the member's new role."""
    role = serializers.ChoiceField(
        choices=OrganizationMembership.ROLE_CHOICES,
        required=True,
    )
