from django.db.models import Exists, OuterRef
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import CursorPagination

from ...models import Contributor, User
from ...models.extended_field import ExtendedField
from ...models.facility.facility_index import FacilityIndex
from ...models.partner_field import PartnerField
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


@method_decorator(cache_page(60 * 5, cache="view_cache"), name="dispatch")
class UserProfileFacilities(ListAPIView):
    """List facilities associated with a user's contributor profile."""

    serializer_class = FacilityIndexSummarySerializer
    pagination_class = FacilityIndexCursorPagination

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

        queryset = (
            FacilityIndex.objects.only(
                "id",
                "name",
                "address",
                "country_code",
                "contributors_id",
                "updated_at",
            )
            .filter(
                contributors_id__contains=[contributor.id],
            )
            .order_by("-updated_at")
        )

        if not params.validated_data["spotlight"]:
            return queryset

        partner_fields = list(
            PartnerField.objects.filter(
                contributor__id=contributor.id
            ).values_list("name", flat=True)
        )

        if not partner_fields:
            return queryset

        queryset = queryset.filter(
            Exists(
                ExtendedField.objects.filter(
                    facility_id=OuterRef("id"),
                    contributor_id=contributor.id,
                    field_name__in=partner_fields,
                )
            )
        )

        return queryset
