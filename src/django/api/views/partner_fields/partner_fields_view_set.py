from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
    Allows client to control page size via ?limit=.
    """

    page_size = 20
    ordering = "created_at"
    page_size_query_param = "limit"
    max_page_size = 100


class PartnerFieldsViewSet(ReadOnlyModelViewSet):
    """
    Viewset for partner fields with cursor-based pagination.
    Allows client to control page size via ?limit=.
    """

    queryset = PartnerField.objects.all()
    serializer_class = PartnerFieldSerializer
    permission_classes = [IsSuperuser]
    throttle_classes = []
    pagination_class = PartnerFieldCursorPagination

    @swagger_auto_schema(
        operation_description="List partner fields with cursor-based pagination.",
        manual_parameters=[
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Number of results to return per page.",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "cursor",
                openapi.IN_QUERY,
                description="Cursor for paginating results.",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """
        List partner fields. Supports cursor-based pagination and limit parameter.
        """
        return super().list(request, *args, **kwargs)
