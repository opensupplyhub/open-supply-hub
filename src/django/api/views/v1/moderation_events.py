import logging
# from django.http import QueryDict
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator,
    is_valid_uuid,
    handle_path_error
)
from api.services.search import OpenSearchService
from api.views.v1.opensearch_query_builder.opensearch_query_builder \
    import OpenSearchQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.serializers.v1.moderation_events_serializer \
    import ModerationEventsSerializer
from api.serializers.v1.moderation_event_update_serializer \
    import ModerationEventUpdateSerializer
from api.views.v1.index_names import OpenSearchIndexNames

from api.models.moderation_event \
    import ModerationEvent

logger = logging.getLogger(__name__)


class ModerationEvents(ViewSet):
    swagger_schema = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opensearch_service = OpenSearchService()
        self.opensearch_query_builder = OpenSearchQueryBuilder()
        self.opensearch_query_director = OpenSearchQueryDirector(
                self.opensearch_query_builder
            )

    @handle_errors_decorator
    def list(self, request):
        params, error_response = serialize_params(
            ModerationEventsSerializer,
            request.GET
        )
        if error_response:
            return Response(
                error_response,
                status=status.HTTP_400_BAD_REQUEST
            )

        query_body = self.opensearch_query_director.build_query(
            request.GET
        )

        logger.info(f'@@@ {query_body}')

        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            query_body
        )
        return Response(response)

    def patch(self, request, moderation_id=None):
        # Validate permission
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied()

        # Validate UUID.
        if not is_valid_uuid(moderation_id):
            return handle_path_error(
                field="moderation_id",
                message="Invalid UUID format.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the moderation event.
        try:
            event = ModerationEvent.objects.get(uuid=moderation_id)
        except ModerationEvent.DoesNotExist:
            return handle_path_error(
                field="moderation_id",
                message="Moderation event not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Serialize and validate data
        serializer = ModerationEventUpdateSerializer(
            event,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {
                "message": 'The request body contains '
                'invalid or missing fields.',
                "error": [serializer.errors]
            },
            status=status.HTTP_400_BAD_REQUEST
        )
