from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.views import APIView

from api.permissions import IsOrganizationMember, IsRegisteredAndConfirmed
from api.services.organization_service import is_organization_level_active


class OrganizationLevelAPIView(APIView):
    """
    Base for every organization endpoint. They are internal, serve the
    React app only, and answer 404 while the organization_level switch
    is off, as if they did not exist.
    """
    permission_classes = (IsRegisteredAndConfirmed,)

    def initial(self, request, *args, **kwargs):
        if not is_organization_level_active():
            raise NotFound()
        super().initial(request, *args, **kwargs)


class OrganizationMemberAPIView(OrganizationLevelAPIView):
    """
    Base for endpoints scoped to one organization
    (/api/organizations/{organization_uuid}/...). The permission class
    resolves the requesting user's membership and leaves it on the
    request.
    """
    permission_classes = (IsOrganizationMember,)

    @property
    def membership(self):
        return self.request.organization_membership

    @property
    def organization(self):
        return self.membership.organization


class OrganizationDashboardAPIView(OrganizationMemberAPIView):
    """
    Base for the paid dashboard endpoints: any member of an organization
    whose dashboard OS Hub staff have switched on.
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not self.organization.dashboard_enabled:
            raise PermissionDenied(
                'The dashboard is not enabled for this organization.'
            )
