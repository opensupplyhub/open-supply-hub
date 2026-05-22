"""
View for the partner group contributors endpoint.

Returns grouped Spotlight Data Partners options. Each returned group includes
its display label and a deduplicated list of contributors. Groups with no
available contributors are omitted from the response.

Uses the project's default API permissions
(`IsAuthenticatedOrWebClient`).
"""

from django.conf import settings
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListAPIView

from api.models.contributor.contributor import Contributor
from api.models.partner_field import PartnerField
from api.models.partner_field_group import PartnerFieldGroup
from api.pagination import PartnerFieldGroupCursorPagination
from api.serializers.partner_group_contributors\
    .partner_group_contributors_serializer import (
        PartnerGroupContributorsSerializer,
    )


@method_decorator(
    cache_page(
        settings.MEMCACHED_VIEW_CACHE_TIMEOUT_SECONDS,
        cache="view_cache",
    ),
    name="dispatch",
)
class PartnerGroupContributorsView(ListAPIView):
    """
    GET /api/partner-group-contributors/

    Returns Spotlight Data Partners grouped for filter display.
    Results are ordered by the configured group order (`order`) ascending,
    with `uuid` as the cursor-pagination tie-breaker.
    Contributor options are built from active partner fields only; groups that
    end up with no contributors after this filter are omitted.

    Each entry includes `uuid`, `label`, and deduplicated `contributors`.

    Response shape (paginated via cursor):
    {
      "next": "<cursor URL | null>",
      "previous": "<cursor URL | null>",
      "results": [
        {
          "uuid": "<group UUID>",
          "label": "<PartnerFieldGroup.name>",
          "contributors": [{"id": <int>, "name": "<str>"}, ...]
        },
        ...
      ]
    }
    """

    serializer_class = PartnerGroupContributorsSerializer
    pagination_class = PartnerFieldGroupCursorPagination

    def get_queryset(self):
        contributor_qs = Contributor.objects.only('id', 'name')

        active_fields_qs = PartnerField.objects.filter(
            active=True,
        ).prefetch_related(
            Prefetch('contributor_set', queryset=contributor_qs),
        )

        return PartnerFieldGroup.objects.filter(
            partner_fields__active=True,
            partner_fields__contributor__isnull=False,
        ).distinct().prefetch_related(
            Prefetch(
                'partner_fields',
                queryset=active_fields_qs,
                to_attr='active_fields',
            )
        )
