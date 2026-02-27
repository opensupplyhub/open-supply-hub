"""
Viewset for partner field groups.
Allows listing of the partner field groups with pagination.
Available for all users.
"""

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import CursorPagination

from api.models.partner_field_group import PartnerFieldGroup
from api.serializers.partner_field_group.\
    partner_field_group_serializer import PartnerFieldGroupSerializer


class PartnerFieldGroupCursorPagination(CursorPagination):
    """
    Cursor based pagination for partner field groups.
    Allows the client to control the page size via the ?limit= parameter.
    And adds the default ordering by the `order` field.
    """

    page_size = 20
    ordering = "order"
    page_size_query_param = "limit"
    max_page_size = 100


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
