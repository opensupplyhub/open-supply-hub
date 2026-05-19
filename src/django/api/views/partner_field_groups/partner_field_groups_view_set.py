"""
Viewset for partner field groups.
Allows listing of the partner field groups with pagination.
Available for all users.
"""

from rest_framework.viewsets import ReadOnlyModelViewSet

from api.models.partner_field_group import PartnerFieldGroup
from api.pagination import PartnerFieldGroupCursorPagination
from api.serializers.partner_field_group.\
    partner_field_group_serializer import PartnerFieldGroupSerializer


class PartnerFieldGroupsViewSet(ReadOnlyModelViewSet):
    """
    Allows listing of the partner field groups.
    Also, prefetches the related partner fields to avoid N+1 queries.
    Available for all users.
    """

    queryset = PartnerFieldGroup.objects.prefetch_related(
        "partner_fields"
    ).all()
    serializer_class = PartnerFieldGroupSerializer
    pagination_class = PartnerFieldGroupCursorPagination
