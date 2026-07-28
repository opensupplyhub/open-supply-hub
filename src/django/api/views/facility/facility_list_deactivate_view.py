from django.db import transaction

from drf_yasg.openapi import (
    Schema,
    TYPE_BOOLEAN,
    TYPE_INTEGER,
    TYPE_OBJECT,
)
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.constants import APIErrorMessages
from api.models.facility.facility_list import FacilityList
from api.permissions import IsRegisteredAndConfirmed
from api.services.facility_list_deactivation_service import (
    deactivate_contributor_source,
)


deactivate_response_schema = Schema(
    type=TYPE_OBJECT,
    properties={
        'list_id': Schema(type=TYPE_INTEGER),
        'deactivated': Schema(type=TYPE_BOOLEAN),
    },
    required=['list_id', 'deactivated'],
)


class FacilityListDeactivateView(APIView):
    permission_classes = (IsRegisteredAndConfirmed,)

    @swagger_auto_schema(
        request_body=no_body,
        responses={
            200: deactivate_response_schema,
            400: APIErrorMessages.LIST_NOT_APPROVED,
            404: APIErrorMessages.FACILITY_LIST_NOT_FOUND,
        },
    )
    @transaction.atomic
    def post(self, request, pk=None):
        """
        Deactivate an approved Facility List uploaded by the authenticated
        contributor.

        The list and its facilities are not deleted. The list is marked as
        rejected and its source is deactivated, replacing the contributor
        name with the contributor type on every affected facility profile.

        A contributor can deactivate only their own approved, active lists.
        Missing lists and lists owned by another contributor both return 404.

        ### Sample Response

            {
                "list_id": 16,
                "deactivated": true
            }
        """
        if pk is None or not str(pk).isdecimal():
            return Response(
                {'detail': APIErrorMessages.FACILITY_LIST_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )

        facility_list = (
            FacilityList.objects
            .filter(id=pk)
            .select_related('source', 'source__contributor')
            .first()
        )
        source = (
            getattr(facility_list, 'source', None)
            if facility_list is not None else None
        )

        contributor_id = (
            request.user.contributor.id
            if request.user.has_contributor else None
        )

        if (facility_list is None
                or source is None
                or source.contributor_id != contributor_id):
            return Response(
                {'detail': APIErrorMessages.FACILITY_LIST_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )

        if not source.is_active:
            return Response(
                {'detail': APIErrorMessages.LIST_ALREADY_INACTIVE},
                status=status.HTTP_404_NOT_FOUND
            )

        if facility_list.status not in (
                FacilityList.APPROVED,
                FacilityList.MATCHED):
            return Response(
                {'detail': APIErrorMessages.LIST_NOT_APPROVED},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not deactivate_contributor_source(facility_list, request.user):
            return Response(
                {'detail': APIErrorMessages.LIST_ALREADY_INACTIVE},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                'list_id': facility_list.id,
                'deactivated': True,
            },
            status=status.HTTP_200_OK
        )
