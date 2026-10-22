"""
Viewset for partner fields with cursor-based pagination.
"""

from rest_framework.viewsets import ReadOnlyModelViewSet
from api.models.partner_field import PartnerField
from api.permissions import IsSuperuser
from api.serializers.partner_field.partner_field_serializer import (
    PartnerFieldSerializer,
)
from rest_framework.pagination import CursorPagination


class PartnerFieldCursorPagination(CursorPagination):
    """
    Pagination class for partner fields with cursor-based pagination.
    """

    page_size = 20
    ordering = "created_at"
    page_size_query_param = "limit"
    max_page_size = 100


class PartnerFieldsViewSet(ReadOnlyModelViewSet):
    """
    Allows listing of the partner fields with pagination. Available
    for superusers only. Allows client to control page size via ?limit=.

    By default only active fields are returned. Pass ?include_inactive=true
    (exact lowercase value) to include inactive fields in the response.
    """

    queryset = PartnerField.objects.all()
    serializer_class = PartnerFieldSerializer
    permission_classes = [IsSuperuser]
    throttle_classes = []
    pagination_class = PartnerFieldCursorPagination

    def get_queryset(self):
        """Return active fields, or all fields when ?include_inactive=true."""
        if self.request.query_params.get('include_inactive') == 'true':
            return PartnerField.objects.get_all_including_inactive()
        return PartnerField.objects.all()
