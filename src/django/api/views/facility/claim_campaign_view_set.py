from django.db.models import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from waffle import switch_is_active

from api.models.facility.claim_campaign import (
    ClaimCampaign,
    ClaimCampaignSupplier,
)
from api.permissions import IsRegisteredAndConfirmed
from api.serializers.facility.claim_campaign_serializer import (
    ClaimCampaignCreateSerializer,
    ClaimCampaignSerializer,
)
from api.serializers import FacilityQueryParamsSerializer
from api.services.claim_campaign_service import (
    API_SOURCE_ID,
    API_SOURCE_NAME,
    MAX_SEARCH_RESULTS,
    SUPPLIER_FACILITY_FIELDS,
    campaign_permissions,
    close_campaign,
    count_list_facilities,
    create_campaign_with_suppliers,
    describe_api_source,
    describe_list_source,
    get_api_facilities,
    get_contributor_list_sources,
    get_list_facilities,
    has_search_filter,
    is_active_campaign_code,
    is_too_large,
    normalize_campaign_code,
    search_campaign_candidates,
    serialize_suppliers,
    too_large_message,
)


class ClaimCampaignViewSet(ListModelMixin, GenericViewSet):
    """
    The requesting user's own claim campaigns with per-supplier claim
    statuses. Statuses expose only what is already public (unclaimed /
    pending / claimed).

    Brands enabled for self-serve (the `claim_campaign_self_serve`
    waffle flag) can also list their candidate suppliers and create a
    campaign from one of their own lists.

    `lookup` is the exception: any registered user (a supplier opening a
    campaign claim link) may ask whether a code is an active campaign.
    """

    NO_CONTRIBUTOR_MESSAGE = (
        'The current user does not have an associated contributor.'
    )

    serializer_class = ClaimCampaignSerializer
    permission_classes = (IsRegisteredAndConfirmed,)
    pagination_class = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        # Premium: off unless the switch is on and this user has been
        # given campaign access (claim_campaign_access flag).
        if not switch_is_active('claim_campaigns'):
            raise NotFound()
        if self.action == 'lookup':
            # Claimants, not campaign owners: no access flag or
            # contributor needed beyond the registered-user permission.
            return
        if request.user.is_authenticated and not campaign_permissions(
            request.user
        )['access']:
            raise NotFound()
        # Campaigns belong to a contributor; a user without one has
        # nothing to list, create or close here.
        if self.get_contributor() is None:
            raise PermissionDenied(self.NO_CONTRIBUTOR_MESSAGE)

    def get_contributor(self):
        return getattr(self.request.user, 'contributor', None)

    def require_self_serve(self):
        contributor = self.get_contributor()
        if contributor is None:
            raise PermissionDenied(self.NO_CONTRIBUTOR_MESSAGE)
        if not campaign_permissions(self.request.user)['self_serve']:
            raise NotFound()
        return contributor

    def get_queryset(self):
        contributor = self.get_contributor()
        if contributor is None:
            return ClaimCampaign.objects.none()

        return (
            ClaimCampaign.objects.filter(contributor=contributor)
            .prefetch_related(
                Prefetch(
                    'suppliers',
                    # Only the fields a supplier row needs: a roster can
                    # hold thousands of production locations.
                    queryset=ClaimCampaignSupplier.objects.select_related(
                        'facility'
                    )
                    .only(
                        'campaign',
                        'facility',
                        *(
                            f'facility__{field}'
                            for field in SUPPLIER_FACILITY_FIELDS
                        ),
                    )
                    .order_by('id'),
                )
            )
            .order_by('-created_at')
        )

    def create(self, request):
        contributor = self.require_self_serve()
        serializer = ClaimCampaignCreateSerializer(
            data=request.data,
            context={'contributor': contributor},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        campaign = create_campaign_with_suppliers(
            contributor, data['name'], data['os_ids']
        )
        campaign = self.get_queryset().get(pk=campaign.pk)
        return Response(
            {
                **ClaimCampaignSerializer(campaign).data,
                # Chosen suppliers left out because they were closed or
                # claimed by the time the campaign was created.
                'skipped': data['skipped'],
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'])
    def candidates(self, request):
        """
        Without `list`, the brand's active lists to choose from (each
        with its matched supplier count and whether it is still pending
        moderation or processing), plus one entry with id `api` for the
        locations it added through the API, if any. With `list={id}`
        (or `list=api`), those suppliers and their claim statuses. A
        list over MAX_LIST_FACILITIES is marked `too_large` and can't be
        opened (400).
        """
        contributor = self.require_self_serve()
        sources = get_contributor_list_sources(contributor)

        list_id = request.query_params.get('list')
        if list_id is None:
            entries = [describe_list_source(source) for source in sources]
            api_entry = describe_api_source(contributor)
            if api_entry is not None:
                entries.append(api_entry)
            return Response(entries)

        if list_id == API_SOURCE_ID:
            api_entry = describe_api_source(contributor)
            if api_entry is None:
                raise NotFound()
            if api_entry['too_large']:
                raise ValidationError(
                    {'detail': too_large_message(api_entry['supplier_count'])}
                )
            return Response(
                {
                    'id': API_SOURCE_ID,
                    'name': API_SOURCE_NAME,
                    'is_public': api_entry['is_public'],
                    'suppliers': serialize_suppliers(
                        get_api_facilities(contributor)
                    ),
                }
            )

        source = (
            sources.filter(facility_list_id=list_id).first()
            if list_id.isdigit()
            else None
        )
        if source is None:
            raise NotFound()
        # Checked before loading the suppliers: counting is cheap, loading
        # a very large list is not.
        supplier_count = count_list_facilities(source)
        if is_too_large(supplier_count):
            raise ValidationError(
                {'detail': too_large_message(supplier_count)}
            )
        return Response(
            {
                'id': source.facility_list.id,
                'name': source.facility_list.name,
                'is_public': source.is_public,
                'suppliers': serialize_suppliers(get_list_facilities(source)),
            }
        )

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close one of the requester's own campaigns. Any campaign owner
        can close, including campaigns OS Hub staff set up for them, so
        this doesn't need the self-serve flag. Another brand's campaign
        is a 404.
        """
        campaign = close_campaign(self.get_object())
        campaign = self.get_queryset().get(pk=campaign.pk)
        return Response(ClaimCampaignSerializer(campaign).data)

    @action(detail=False, methods=['get'], url_path='candidates/search')
    def search_candidates(self, request):
        """
        Facilities matching the same filters as the public OS Hub search
        (q, countries, sectors, facility_type, number_of_workers, ...),
        with claim statuses, so a brand can add suppliers it didn't
        contribute. Closed facilities are excluded. At most
        MAX_SEARCH_RESULTS are returned, sorted by name; `count` is the
        full number of matches.
        """
        self.require_self_serve()

        params = FacilityQueryParamsSerializer(data=request.query_params)
        if not params.is_valid():
            raise ValidationError(params.errors)
        if not has_search_filter(request.query_params):
            raise ValidationError(
                {'detail': 'Add at least one search filter.'}
            )

        count, facilities = search_campaign_candidates(request.query_params)
        return Response(
            {
                'count': count,
                'limit': MAX_SEARCH_RESULTS,
                'suppliers': serialize_suppliers(facilities),
            }
        )

    @action(detail=False, methods=['get'])
    def lookup(self, request):
        """
        Whether `code` is an ACTIVE campaign, for the claim form's
        campaign banner: `{"code": <normalized code>, "active": bool}`.
        Says nothing else about the campaign (not its name or brand),
        so a link can't reveal who invited the supplier. A code that
        can't be a campaign code is simply not active.
        """
        raw_code = request.query_params.get('code', '')
        if not raw_code.strip():
            raise ValidationError({'code': 'This parameter is required.'})
        code = normalize_campaign_code(raw_code)
        return Response(
            {
                'code': code,
                'active': is_active_campaign_code(code),
            }
        )
