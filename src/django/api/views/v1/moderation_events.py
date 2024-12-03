import logging

from django.http import QueryDict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from django.api.moderation_event_actions.approval.add_production_location \
    import AddProductionLocation
from api.moderation_event_actions.approval.event_approval_context \
    import EventApprovalContext
from api.permissions import IsRegisteredAndConfirmed
from api.serializers.v1.moderation_event_update_serializer \
    import ModerationEventUpdateSerializer
from api.serializers.v1.moderation_events_serializer \
    import ModerationEventsSerializer
from api.services.moderation_events_service import ModerationEventsService
from api.services.opensearch.search import OpenSearchService
from api.views.v1.index_names import OpenSearchIndexNames
from api.views.v1.opensearch_query_builder.moderation_events_query_builder \
    import ModerationEventsQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director import \
    OpenSearchQueryDirector
from api.views.v1.utils import (
    handle_errors_decorator,
    serialize_params
)

log = logging.getLogger(__name__)


class ModerationEvents(ViewSet):
    swagger_schema = None
    permission_classes = [IsRegisteredAndConfirmed]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opensearch_service = OpenSearchService()
        self.moderation_events_service = ModerationEventsService()
        self.moderation_events_query_builder = ModerationEventsQueryBuilder()
        self.opensearch_query_director = OpenSearchQueryDirector(
                self.moderation_events_query_builder
            )

    @handle_errors_decorator
    def list(self, request):
        _, error_response = serialize_params(
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

        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            query_body
        )
        return Response(response)

    @handle_errors_decorator
    def retrieve(self, _,  pk=None):
        self.moderation_events_service.validate_uuid(pk)

        query_params = QueryDict('', mutable=True)
        query_params.update({'moderation_id': pk})
        query_body = self.opensearch_query_director.build_query(
            query_params
        )
        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            query_body
        )
        return Response(response)

    @handle_errors_decorator
    def patch(self, request, pk=None):
        self.moderation_events_service.validate_user_permissions(request)

        self.moderation_events_service.validate_uuid(pk)

        event = self.moderation_events_service.fetch_moderation_event_by_uuid(
            pk
        )

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
                "detail": 'The request body contains '
                'invalid or missing fields.',
                "error": [serializer.errors]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @handle_errors_decorator
    def add_production_location(self, request, moderation_id=None):
        self.moderation_events_service.validate_user_permissions(request)

        self.moderation_events_service.validate_uuid(moderation_id)

        event = self.moderation_events_service.fetch_moderation_event_by_uuid(
            moderation_id
        )

        self.moderation_events_service.validate_moderation_status(event.status)

        add_production_location = EventApprovalContext(
            AddProductionLocation(event)
        )

        try:
            item = add_production_location.run_processing()
        except Exception as error:
            return self.moderation_events_service.handle_processing_error(
                error
            )

        return Response(
            {"os_id": item.facility_id}, status=status.HTTP_201_CREATED
        )
