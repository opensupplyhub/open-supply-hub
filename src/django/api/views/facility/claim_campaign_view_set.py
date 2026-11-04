from django.db.models import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from waffle import flag_is_active, switch_is_active

from api.models.facility.claim_campaign import (
    ClaimCampaign,
    ClaimCampaignSupplier,
)
from api.permissions import IsRegisteredAndConfirmed
from api.serializers.facility.claim_campaign_serializer import (
    ClaimCampaignCreateSerializer,
    ClaimCampaignSerializer,
)
from api.services.claim_campaign_service import (
    SELF_SERVE_FLAG,
    create_campaign_with_suppliers,
    get_contributor_list_sources,
    get_list_facilities,
    serialize_suppliers,
)


class ClaimCampaignViewSet(ListModelMixin, GenericViewSet):
    """
    The requesting user's own claim campaigns with per-supplier claim
    statuses. Statuses expose only what is already public (unclaimed /
    pending / claimed).

    Brands enabled for self-serve (the `claim_campaign_self_serve`
    waffle flag) can also list their candidate suppliers and create a
    campaign from one of their own lists.
    """

    serializer_class = ClaimCampaignSerializer
    permission_classes = (IsRegisteredAndConfirmed,)
    pagination_class = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not switch_is_active('claim_campaigns'):
            raise NotFound()

    def get_contributor(self):
        return getattr(self.request.user, 'contributor', None)

    def require_self_serve(self):
        contributor = self.get_contributor()
        if contributor is None or not flag_is_active(
            self.request, SELF_SERVE_FLAG
        ):
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
                    queryset=ClaimCampaignSupplier.objects.select_related(
                        'facility'
                    ).order_by('id'),
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
            ClaimCampaignSerializer(campaign).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'])
    def candidates(self, request):
        """
        Without `list`, the brand's active lists to choose from. With
        `list={id}`, that list's matched suppliers and claim statuses.
        """
        contributor = self.require_self_serve()
        sources = get_contributor_list_sources(contributor)

        list_id = request.query_params.get('list')
        if list_id is None:
            return Response(
                [
                    {
                        'id': source.facility_list.id,
                        'name': source.facility_list.name,
                        'is_public': source.is_public,
                        'created_at': source.created_at,
                    }
                    for source in sources
                ]
            )

        source = (
            sources.filter(facility_list_id=list_id).first()
            if list_id.isdigit()
            else None
        )
        if source is None:
            raise NotFound()
        return Response(
            {
                'id': source.facility_list.id,
                'name': source.facility_list.name,
                'is_public': source.is_public,
                'suppliers': serialize_suppliers(get_list_facilities(source)),
            }
        )
