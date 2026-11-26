from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_list import FacilityList
from api.models.moderation_event import ModerationEvent
from api.models.source import Source
from api.pagination import PageAndSizePagination
from api.serializers.organization.organization_query_params_serializers \
    import OrganizationContributionsQueryParamsSerializer as QueryParams
from api.views.organization.base import OrganizationMemberAPIView


def submitted_by(contributor):
    """Who submitted a contribution, as the organization sees them."""
    if contributor is None:
        return None
    return {
        'contributor_id': contributor.id,
        'contributor_name': contributor.name,
        'email': contributor.admin.email,
    }


class OrganizationContributions(OrganizationMemberAPIView):
    """
    GET /api/organizations/{uuid}/contributions/
        ?type=lists|contributions|claims

    A read-only, newest-first list of what the organization's members
    submitted: uploaded lists, SLC and API contributions, or claims,
    each with who submitted it. Includes what former members submitted
    while they belonged. Optional `member` narrows to one contributor
    id. Any member.
    """
    pagination_class = PageAndSizePagination

    def get(self, request, organization_uuid):
        params = QueryParams(data=request.query_params)
        params.is_valid(raise_exception=True)
        contribution_type = params.validated_data['type']
        member = params.validated_data.get('member')

        if contribution_type == QueryParams.CONTRIBUTIONS:
            queryset, to_row = self._moderation_events(member)
        elif contribution_type == QueryParams.CLAIMS:
            queryset, to_row = self._claims(member)
        else:
            queryset, to_row = self._lists(member)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            [to_row(item) for item in page]
        )

    def _lists(self, member):
        queryset = (
            FacilityList.objects
            .filter(
                source__organization=self.organization,
                source__source_type=Source.LIST,
            )
            .select_related('source__contributor__admin')
            .order_by('-created_at')
        )
        if member:
            queryset = queryset.filter(source__contributor_id=member)

        def to_row(facility_list):
            return {
                'id': facility_list.id,
                'name': facility_list.name,
                'status': facility_list.status,
                'is_active': facility_list.source.is_active,
                'created_at': facility_list.created_at,
                'submitted_by': submitted_by(
                    facility_list.source.contributor
                ),
            }

        return queryset, to_row

    def _moderation_events(self, member):
        queryset = (
            ModerationEvent.objects
            .filter(organization=self.organization)
            .exclude(request_type=ModerationEvent.RequestType.CLAIM)
            .select_related('contributor__admin')
            .order_by('-created_at')
        )
        if member:
            queryset = queryset.filter(contributor_id=member)

        def to_row(event):
            cleaned_data = event.cleaned_data or {}
            return {
                'moderation_id': event.uuid,
                'request_type': event.request_type,
                'source': event.source,
                'status': event.status,
                'name': cleaned_data.get('name'),
                'country_code': cleaned_data.get('country_code'),
                'os_id': event.os_id,
                'created_at': event.created_at,
                'submitted_by': submitted_by(event.contributor),
            }

        return queryset, to_row

    def _claims(self, member):
        queryset = (
            FacilityClaim.objects
            .filter(organization=self.organization)
            .select_related('contributor__admin', 'facility')
            .order_by('-created_at')
        )
        if member:
            queryset = queryset.filter(contributor_id=member)

        def to_row(claim):
            return {
                'id': claim.id,
                'os_id': claim.facility_id,
                'facility_name': claim.facility.name,
                'status': claim.status,
                'created_at': claim.created_at,
                'submitted_by': submitted_by(claim.contributor),
            }

        return queryset, to_row
