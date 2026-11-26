from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response

from api.models.organization.organization_membership import (
    OrganizationMembership,
)
from api.permissions import IsOrganizationAdmin
from api.serializers.organization.organization_membership_serializer \
    import (
        OrganizationMembershipSerializer,
        OrganizationMembershipUpdateSerializer,
    )
from api.services.organization_service import (
    change_member_role,
    remove_member,
)
from api.views.organization.base import OrganizationMemberAPIView


class OrganizationMembers(OrganizationMemberAPIView):
    """
    GET /api/organizations/{uuid}/members/: the organization's active
    members and its seat usage. Any member.
    """

    def get(self, request, organization_uuid):
        memberships = (
            self.organization.active_memberships()
            .select_related('user', 'user__contributor')
            .order_by('joined_at')
        )
        serializer = OrganizationMembershipSerializer(
            memberships, many=True, context={'request': request}
        )
        return Response({
            'members': serializer.data,
            'seat_limit': self.organization.seat_limit,
            'seats_used': self.organization.seats_used,
        })


class OrganizationMemberDetail(OrganizationMemberAPIView):
    """
    PATCH  /api/organizations/{uuid}/members/{membership_uuid}/
        Change a member's role. Admin only.
    DELETE /api/organizations/{uuid}/members/{membership_uuid}/
        Remove a member (Admin), or leave (the member themselves).
    """

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsOrganizationAdmin()]
        return super().get_permissions()

    def _get_target(self, membership_uuid):
        try:
            return OrganizationMembership.objects.select_related(
                'user', 'user__contributor'
            ).get(
                uuid=membership_uuid,
                organization=self.organization,
                status=OrganizationMembership.ACTIVE,
            )
        except OrganizationMembership.DoesNotExist as exc:
            raise NotFound('Member not found.') from exc

    def patch(self, request, organization_uuid, membership_uuid):
        target = self._get_target(membership_uuid)
        serializer = OrganizationMembershipUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target = change_member_role(
            target, serializer.validated_data['role']
        )
        target = self._get_target(target.uuid)
        return Response(
            OrganizationMembershipSerializer(
                target, context={'request': request}
            ).data
        )

    def delete(self, request, organization_uuid, membership_uuid):
        target = self._get_target(membership_uuid)

        is_self = target.user_id == request.user.id
        if not is_self and not self.membership.is_admin:
            raise PermissionDenied(
                'Only an Admin of this organization can remove a member.'
            )

        remove_member(target, removed_by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
