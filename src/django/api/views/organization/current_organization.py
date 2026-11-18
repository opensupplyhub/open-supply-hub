from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from api.serializers.organization.organization_serializer import (
    OrganizationSerializer,
)
from api.services.organization_service import get_active_membership
from api.views.organization.base import OrganizationLevelAPIView


class CurrentOrganization(OrganizationLevelAPIView):
    """
    GET /api/organizations/current/: the organization the requesting
    user belongs to, with their role and its seat usage. 404 when they
    belong to none.
    """

    def get(self, request):
        membership = get_active_membership(request.user)
        if membership is None:
            raise NotFound('You do not belong to an organization.')

        serializer = OrganizationSerializer(
            membership.organization,
            context={'membership': membership},
        )
        return Response(serializer.data)
