from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from api.pagination import PageAndSizePagination
from api.serializers.organization.organization_query_params_serializers \
    import OrganizationDashboardQueryParamsSerializer
from api.services.organization_dashboard_service import (
    OrganizationDashboardService,
)
from api.services.organization_usage_service import OrganizationUsageService
from api.views.organization.base import OrganizationDashboardAPIView


def _dashboard_filters(request):
    params = OrganizationDashboardQueryParamsSerializer(
        data=request.query_params
    )
    params.is_valid(raise_exception=True)
    return params.validated_data


class OrganizationDashboardSummary(OrganizationDashboardAPIView):
    """
    GET /api/organizations/{uuid}/dashboard/summary/: how many production
    locations the organization's members submitted, broken down by
    member, country, month, sector and list versus single contribution,
    plus claimed versus unclaimed and what still waits for moderation.
    Filters: member, country, date_from, date_to, claimed.
    """

    def get(self, request, organization_uuid):
        service = OrganizationDashboardService(
            self.organization, _dashboard_filters(request)
        )
        return Response(service.summary())


class OrganizationDashboardFacilities(OrganizationDashboardAPIView):
    """
    GET /api/organizations/{uuid}/dashboard/facilities/: one row per
    production location and submission, newest first, with who
    submitted it, when, through which list, and whether it is claimed.
    Same filters as the summary; paginated with page and pageSize.
    """
    pagination_class = PageAndSizePagination

    def get(self, request, organization_uuid):
        service = OrganizationDashboardService(
            self.organization, _dashboard_filters(request)
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(
            service.facility_rows(), request, view=self
        )
        return paginator.get_paginated_response(
            [service.serialize_row(item) for item in page]
        )


class OrganizationDashboardFacilityDetail(OrganizationDashboardAPIView):
    """
    GET /api/organizations/{uuid}/dashboard/facilities/{os_id}/: one
    production location the organization submitted, with the
    organization's submissions of it and the claimed data its public
    profile shows.
    """

    def get(self, request, organization_uuid, os_id):
        service = OrganizationDashboardService(self.organization)
        detail = service.facility_detail(os_id)
        if detail is None:
            raise NotFound(
                'This organization has not submitted that production '
                'location.'
            )
        return Response(detail)


class OrganizationDashboardLists(OrganizationDashboardAPIView):
    """
    GET /api/organizations/{uuid}/dashboard/lists/: the match report.
    For each list the organization uploaded, newest first, how many
    rows matched a production location OS Hub already had, how many
    created a new one, and how many are unresolved, failed or removed.
    """

    def get(self, request, organization_uuid):
        service = OrganizationDashboardService(self.organization)
        return Response({'lists': service.list_match_report()})


class OrganizationDashboardUsage(OrganizationDashboardAPIView):
    """
    GET /api/organizations/{uuid}/dashboard/usage/: what the
    organization's current members downloaded and how much they called
    the API recently, per member and in total, with each member's
    remaining download allowance and API limit.
    """

    def get(self, request, organization_uuid):
        return Response(OrganizationUsageService(self.organization).usage())
