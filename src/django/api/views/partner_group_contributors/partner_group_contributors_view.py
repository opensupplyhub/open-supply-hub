"""
View for the partner group contributors endpoint.

Returns, for each partner field group, the list of contributors who
contribute data through that group's active partner fields. System
partner fields belong to groups just like regular fields and are
included via those groups — no separate handling needed.

Available to all users without authentication.
"""

from django.db.models import Prefetch
from rest_framework.generics import ListAPIView

from api.models.contributor.contributor import Contributor
from api.models.partner_field import PartnerField
from api.models.partner_field_group import PartnerFieldGroup
from api.pagination import PartnerFieldGroupCursorPagination
from api.serializers.partner_group_contributors\
    .partner_group_contributors_serializer import (
        PartnerGroupContributorsSerializer,
    )


class PartnerGroupContributorsView(ListAPIView):
    """
    GET /api/partner-group-contributors/

    Returns one entry per PartnerFieldGroup, ordered by
    PartnerFieldGroup.order.
    Each entry carries the group's display label and the deduplicated list of
    contributors who are linked — via Contributor.partner_fields — to at least
    one active PartnerField in that group. System fields belong to groups and
    are included through the same path.

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

        return PartnerFieldGroup.objects.prefetch_related(
            Prefetch(
                'partner_fields',
                queryset=active_fields_qs,
                to_attr='active_fields',
            )
        )
