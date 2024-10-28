import logging
# from django.http import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator
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

    @handle_errors_decorator
    def patch(self, request, moderation_id=None):
        event = get_object_or_404(ModerationEvent, uuid=moderation_id)
        serializer = ModerationEventUpdateSerializer(event, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
