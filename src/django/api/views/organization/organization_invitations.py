from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from api.mail import (
    send_organization_invitation_email,
    send_organization_invitation_response_email,
)
from api.models.organization.organization_invitation import (
    OrganizationInvitation,
)
from api.permissions import IsOrganizationAdmin
from api.serializers.organization.organization_invitation_serializer \
    import (
        OrganizationInvitationCreateSerializer,
        OrganizationInvitationSerializer,
    )
from api.services.organization_service import (
    accept_invitation,
    create_invitation,
    decline_invitation,
    expire_stale_invitations,
    revoke_invitation,
)
from api.throttles import OrganizationInviteThrottle
from api.views.organization.base import (
    OrganizationLevelAPIView,
    OrganizationMemberAPIView,
)


class OrganizationInvitations(OrganizationMemberAPIView):
    """
    GET  /api/organizations/{uuid}/invitations/
        The invitations still waiting for an answer.
    POST /api/organizations/{uuid}/invitations/
        Invite the existing OS Hub account behind an email address.
        Refused with 400 and a reason the Admin can act on when the
        email has no confirmed account, the person already belongs to an
        organization or has an invitation waiting, or no seat is free.
    Admin only.
    """
    permission_classes = (IsOrganizationAdmin,)

    def get_throttles(self):
        if self.request.method == 'POST':
            return [OrganizationInviteThrottle()]
        return super().get_throttles()

    def get(self, request, organization_uuid):
        expire_stale_invitations(self.organization)
        invitations = (
            self.organization.invitations
            .filter(status=OrganizationInvitation.PENDING)
            .select_related('organization', 'invited_by')
        )
        return Response(
            OrganizationInvitationSerializer(invitations, many=True).data
        )

    def post(self, request, organization_uuid):
        serializer = OrganizationInvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation = create_invitation(
            organization=self.organization,
            invited_by=request.user,
            email=serializer.validated_data['email'],
            role=serializer.validated_data['role'],
        )
        send_organization_invitation_email(request, invitation)
        OrganizationInviteThrottle().record_invite(request, self)

        return Response(
            OrganizationInvitationSerializer(invitation).data,
            status=status.HTTP_201_CREATED,
        )


class OrganizationInvitationDetail(OrganizationMemberAPIView):
    """
    DELETE /api/organizations/{uuid}/invitations/{invitation_uuid}/:
    revoke an invitation that is still waiting. Admin only.
    """
    permission_classes = (IsOrganizationAdmin,)

    def delete(self, request, organization_uuid, invitation_uuid):
        try:
            invitation = OrganizationInvitation.objects.get(
                uuid=invitation_uuid,
                organization=self.organization,
            )
        except OrganizationInvitation.DoesNotExist as exc:
            raise NotFound('Invitation not found.') from exc

        revoke_invitation(invitation)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyOrganizationInvitations(OrganizationLevelAPIView):
    """
    GET /api/organization-invitations/: the invitations waiting for the
    requesting user's answer.
    """

    def get(self, request):
        invitations = [
            invitation for invitation in
            OrganizationInvitation.objects
            .filter(
                invited_user=request.user,
                status=OrganizationInvitation.PENDING,
                organization__is_active=True,
            )
            .select_related('organization', 'invited_by')
            if invitation.is_open
        ]
        return Response(
            OrganizationInvitationSerializer(invitations, many=True).data
        )


class OrganizationInvitationResponse(OrganizationLevelAPIView):
    """
    POST /api/organization-invitations/{invitation_uuid}/accept/
    POST /api/organization-invitations/{invitation_uuid}/decline/
    Only the invited user can answer. Accepting creates the membership
    and attributes the user's earlier contributions to the organization.
    """
    accept = True

    def post(self, request, invitation_uuid):
        try:
            invitation = OrganizationInvitation.objects.select_related(
                'organization', 'invited_by', 'invited_user'
            ).get(uuid=invitation_uuid, invited_user=request.user)
        except OrganizationInvitation.DoesNotExist as exc:
            raise NotFound('Invitation not found.') from exc

        if self.accept:
            accept_invitation(invitation, request.user)
        else:
            decline_invitation(invitation, request.user)

        invitation.refresh_from_db()
        send_organization_invitation_response_email(
            request, invitation, accepted=self.accept
        )

        return Response(OrganizationInvitationSerializer(invitation).data)
