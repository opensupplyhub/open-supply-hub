from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.pagination import CursorPagination

from ...models import Contributor, FacilityList, User
from ...serializers.facility.facility_list_summary_serializer import (
    FacilityListSummarySerializer,
)


class FacilityListCursorPagination(CursorPagination):
    """Newest-first cursor pagination for facility lists."""

    page_size = 10
    ordering = "-created_at"
    page_size_query_param = "limit"
    max_page_size = 100


class UserProfileFacilityLists(ListAPIView):
    """List a user's approved, public facility lists."""

    serializer_class = FacilityListSummarySerializer
    pagination_class = FacilityListCursorPagination

    def get_queryset(self):
        """Return approved facility lists for the user given by URL pk."""
        try:
            user = User.objects.get(pk=self.kwargs["pk"])
            contributor = user.contributor
        except User.DoesNotExist as exc:
            raise NotFound() from exc
        except Contributor.DoesNotExist as exc:
            raise NotFound() from exc

        return FacilityList.objects.filter(
            source__contributor=contributor,
            source__is_active=True,
            source__is_public=True,
            status=FacilityList.APPROVED,
        ).order_by("-created_at")
