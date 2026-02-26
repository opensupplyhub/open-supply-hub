"""
Viewset for partner field groups.
"""

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import CursorPagination

from api.models.partner_field_group import PartnerFieldGroup
from api.serializers.partner_field_group.\
    partner_field_group_serializer import PartnerFieldGroupSerializer


class PartnerFieldGroupCursorPagination(CursorPagination):
    """
    Pagination class for partner field groups with cursor-based pagination.
    """

    page_size = 20
    ordering = "order"
    page_size_query_param = "limit"
    max_page_size = 100


class PartnerFieldGroupsViewSet(ReadOnlyModelViewSet):
    """
    Allows listing of the partner field groups.
    Available for all users.
    """

    queryset = PartnerFieldGroup.objects.prefetch_related(
        "partner_fields"
    ).all()
    serializer_class = PartnerFieldGroupSerializer
    pagination_class = PartnerFieldGroupCursorPagination
