from drf_yasg.openapi import Schema, TYPE_OBJECT
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ...models.facility.facility_activity_report import FacilityActivityReport
from ...serializers.facility.facility_activity_report_serializer import (
    FacilityActivityReportSerializer
)
from ..is_list_and_admin_or_not_list import IsListAndAdminOrNotList
from .update_facility_activity_report_status import (
    update_facility_activity_report_status
)

facility_activity_report_schema = Schema(
    'data',
    type=TYPE_OBJECT,
    description=('The reason for the report status change.'),
)


class FacilityActivityReportViewSet(GenericViewSet):
    """
    Manage FacilityActivityReports.
    """
    queryset = FacilityActivityReport.objects.all()
    serializer_class = FacilityActivityReportSerializer
    permission_classes = (IsListAndAdminOrNotList,)

    @swagger_auto_schema(request_body=facility_activity_report_schema,
                         responses={200: FacilityActivityReportSerializer})
    @action(detail=True, methods=['POST'],
            permission_classes=(IsAdminUser,),
            url_path='approve')
    def approve(self, request, pk=None):
        """
        Approve a facility report.

        ## Sample Request Body

            {
                "status_change_reason": "The facility report was confirmed."
            }
        """
        try:
            facility_activity_report = self.queryset.get(id=pk)
        except FacilityActivityReport.DoesNotExist as exc:
            raise NotFound() from exc

        facility_activity_report = update_facility_activity_report_status(
            facility_activity_report, request,
            'CONFIRMED')

        facility = facility_activity_report.facility
        if facility_activity_report.closure_state == 'CLOSED':
            facility.is_closed = True
        else:
            facility.is_closed = False
        facility.save()

        response_data = FacilityActivityReportSerializer(
            facility_activity_report).data

        return Response(response_data)

    @swagger_auto_schema(request_body=facility_activity_report_schema,
                         responses={200: FacilityActivityReportSerializer})
    @action(detail=True, methods=['POST'],
            permission_classes=(IsAdminUser,),
            url_path='reject')
    def reject(self, request, pk=None):
        """
        Reject a facility report.

        ## Sample Request Body

            {
                "status_change_reason": "The facility report is incorrect."
            }
        """
        try:
            facility_activity_report = self.queryset.get(id=pk)
        except FacilityActivityReport.DoesNotExist as exc:
            raise NotFound() from exc

        facility_activity_report = update_facility_activity_report_status(
            facility_activity_report, request,
            'REJECTED')

        response_data = FacilityActivityReportSerializer(
            facility_activity_report).data

        return Response(response_data)

    def list(self, _):
        response_data = FacilityActivityReportSerializer(
            FacilityActivityReport.objects.all(), many=True).data

        return Response(response_data)
