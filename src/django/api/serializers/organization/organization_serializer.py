from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
)

from api.models.organization.organization import Organization


class OrganizationSerializer(ModelSerializer):
    """
    An organization as one of its members sees it. Pass the requesting
    user's membership in the context as `membership`.
    """
    seats_used = SerializerMethodField()
    role = SerializerMethodField()
    membership_uuid = SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            'uuid',
            'name',
            'legal_name',
            'parent_entity_name',
            'seat_limit',
            'seats_used',
            'dashboard_enabled',
            'role',
            'membership_uuid',
        )

    def get_seats_used(self, organization):
        return organization.seats_used

    def get_role(self, _):
        membership = self.context.get('membership')
        return membership.role if membership else None

    def get_membership_uuid(self, _):
        membership = self.context.get('membership')
        return membership.uuid if membership else None
