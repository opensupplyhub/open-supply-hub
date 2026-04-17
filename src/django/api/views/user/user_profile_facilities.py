from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.pagination import CursorPagination

from ...models import Contributor, User
from ...models.facility.facility_index import FacilityIndex
from ...serializers.facility.facility_index_summary_serializer import (
    FacilityIndexSummarySerializer,
)


class FacilityIndexCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-updated_at"
    page_size_query_param = "limit"
    max_page_size = 20


class UserProfileFacilities(ListAPIView):
    serializer_class = FacilityIndexSummarySerializer
    pagination_class = FacilityIndexCursorPagination

    def get_queryset(self):
        try:
            user = User.objects.get(pk=self.kwargs["pk"])
            contributor = user.contributor
        except User.DoesNotExist as exc:
            raise NotFound() from exc
        except Contributor.DoesNotExist as exc:
            raise NotFound() from exc

        return FacilityIndex.objects.filter(
            contributors_id__contains=[contributor.id],
        ).order_by("-updated_at")
