from django.conf import settings
from django.db.models import Exists, OuterRef, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import CursorPagination

from ...models import Contributor, User
from ...models.extended_field import ExtendedField
from ...models.facility.facility_index import FacilityIndex
from ...models.partner_field import PartnerField
from ...models.wage_indicator_country_data import WageIndicatorCountryData
from ...partner_fields.india_labour_line_provider import (
    IndiaLabourLineProvider,
    get_covered_production_locations,
)
from ...partner_fields.zone_set_provider import (
    build_zone_sets_covered_q,
    get_active_zone_sets_for_fields,
)
from ...serializers.facility.facility_index_summary_serializer import (
    FacilityIndexSummarySerializer,
)
from ...serializers.user.user_profile_facilities_serializer import (
    UserProfileFacilitiesSerializer,
)


class FacilityIndexCursorPagination(CursorPagination):
    """Cursor-based pagination for facility index listings."""

    page_size = 10
    ordering = "-updated_at"
    page_size_query_param = "limit"
    max_page_size = 20


@method_decorator(
    cache_page(
        settings.MEMCACHED_VIEW_CACHE_TIMEOUT_SECONDS,
        cache="view_cache",
    ),
    name="dispatch",
)
class UserProfileFacilities(ListAPIView):
    """List facilities associated with a user's contributor profile."""

    serializer_class = FacilityIndexSummarySerializer
    pagination_class = FacilityIndexCursorPagination

    def __base_queryset(self):
        """The slim facility queryset every branch below filters."""
        return FacilityIndex.objects.only(
            "id",
            "name",
            "address",
            "country_code",
            "contributors_id",
            "updated_at",
        ).order_by("-updated_at")

    def get_queryset(self):
        """
        Return facility indexes where the user is a contributor.
        Has the ability to filter spotlight facilities by partner fields.
        """
        params = UserProfileFacilitiesSerializer(
            data=self.request.query_params,
        )

        if not params.is_valid():
            raise ValidationError(params.errors)

        try:
            user = User.objects.get(pk=self.kwargs["pk"])
            contributor = user.contributor
        except User.DoesNotExist as exc:
            raise NotFound() from exc
        except Contributor.DoesNotExist as exc:
            raise NotFound() from exc

        queryset = self.__base_queryset().filter(
            contributors_id__contains=[
                contributor.id,
            ],
        )

        if not params.validated_data["spotlight"]:
            return queryset

        partner_fields = list(
            PartnerField.objects.filter(
                contributor__id=contributor.id
            ).values_list("name", flat=True)
        )

        if not partner_fields:
            return self.__base_queryset().none()

        if "wage_indicator" in partner_fields:
            country_codes = list(
                WageIndicatorCountryData.objects.values_list(
                    "country_code", flat=True
                )
            )
            return self.__base_queryset().filter(
                country_code__in=country_codes,
            )

        if "mit_living_wage" in partner_fields:
            return self.__base_queryset().filter(
                country_code__in=["US"],
            )

        # The India Labour Line spotlight shows the locations the
        # helpline covers, applying the shared covered-locations rule
        # directly to this view's own queryset (one flat query) so
        # this page can never disagree with the search filter.
        if IndiaLabourLineProvider.FIELD_NAME in partner_fields:
            return get_covered_production_locations(
                self.__base_queryset()
            )

        # A zone-set field is served by polygons, so its spotlight is
        # every location a zone covers, whoever contributed it. The
        # shared helpers keep this the same condition the search
        # filter applies, and return no zone sets while the
        # `enable_zone_sets` switch is off (or the set is inactive),
        # in which case the field falls through to the contributed
        # branch below and matches nothing. A contributor holding
        # both a zone-set field and a contributed field gets the
        # union of the two, with the contributed half still scoped to
        # the contributor's own locations as it always was.
        zone_sets = get_active_zone_sets_for_fields(partner_fields)
        zone_set_field_names = {
            zone_set.partner_field.name for zone_set in zone_sets
        }
        contributed_fields = [
            field_name
            for field_name in partner_fields
            if field_name not in zone_set_field_names
        ]

        contributed_q = Exists(
            ExtendedField.objects.filter(
                facility_id=OuterRef("id"),
                contributor_id=contributor.id,
                field_name__in=contributed_fields,
            )
        )

        if not zone_sets:
            return queryset.filter(contributed_q)

        covered_q = build_zone_sets_covered_q(zone_sets)
        if contributed_fields:
            own_contributed_q = (
                Q(contributors_id__contains=[contributor.id]) & contributed_q
            )
            return self.__base_queryset().filter(
                covered_q | own_contributed_q
            )
        return self.__base_queryset().filter(covered_q)
