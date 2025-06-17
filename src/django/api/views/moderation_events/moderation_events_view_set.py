from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import (
    PermissionDenied,
    NotFound,
    ValidationError)
from drf_yasg.utils import swagger_auto_schema
from waffle import flag_is_active

from api.permissions import IsRegisteredAndConfirmed
from api.constants import FeatureGroups
from api.serializers import MergeQueryParamsSerializer
from api.views.moderation_events.moderation_event_params import (
    merge_params
)
from api.views.moderation_events.merge_events import (
    build_query_string
)
from api.views.moderation_events.merge_events import (
    retrieve_merge_events,
    fetch_all
)


class ModerationEventsViewSet(ViewSet):
    """
    A view for the 'moderation-events' API endpoint that a user can call to
    retrieve information about moderation events applied to the facilities.
    """

    @swagger_auto_schema(responses={200: ''},
                         manual_parameters=merge_params)
    @action(detail=False, methods=['GET'],
            permission_classes=(IsRegisteredAndConfirmed,))
    def merge(self, request):
        """
        Returns an array of objects with the history of merge events applied
        to the facilities that have occurred for all contributors and that were
        involved in a merge moderation event within the given date range.
        The API user can also specify 'contributors' parameters to receive
        information about merges that have occurred for the contributors
        with the specified IDs.

        ### Sample Response
            [
                {
                    "current_id": "PL2023213ZGTRGT",
                    "original_id": "PL2023214F95KZS",
                    "created_at": "2023-08-02T08:55:10.046094Z",
                    "merge_date": "2023-08-02T09:10:00.340169Z",
                },
                {
                    "current_id": "PL2023213ZGTRGT",
                    "original_id": "PL2023213T2T6FM",
                    "created_at": "2023-08-01T11:35:31.595269Z",
                    "merge_date": "2023-08-01T11:45:53.306978Z",
                }
            ]
        """

        context = {'request': request}
        params = MergeQueryParamsSerializer(
            data=request.query_params,
            context=context)

        if not params.is_valid():
            raise ValidationError(params.errors)

        # Check if the API user has paid access to the API.
        if not flag_is_active(request._request,
                              FeatureGroups.CAN_GET_FACILITY_HISTORY):
            raise PermissionDenied()

        query = build_query_string(params)
        merge_history = retrieve_merge_events(query, fetch_all)

        if len(merge_history) == 0:
            raise NotFound()

        return Response(merge_history)
