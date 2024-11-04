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
from api.views.v1.opensearch_query_builder.moderation_events_query_builder \
    import ModerationEventsQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.serializers.v1.moderation_events_serializer \
    import ModerationEventsSerializer
from api.serializers.v1.moderation_event_update_serializer \
    import ModerationEventUpdateSerializer
from api.views.v1.index_names import OpenSearchIndexNames

from api.models.moderation_event \
    import ModerationEvent


class ModerationEvents(ViewSet):
    swagger_schema = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opensearch_service = OpenSearchService()
        self.moderation_events_query_builder = ModerationEventsQueryBuilder()
        self.opensearch_query_director = OpenSearchQueryDirector(
                self.moderation_events_query_builder
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

        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            query_body
        )
        return Response(response)

    @handle_errors_decorator
    def patch(self, request, moderation_id):
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied(
                detail="Only the Moderator can perform this action."
            )

        if not is_valid_uuid(moderation_id):
            return handle_path_error(
                field="moderation_id",
                message="Invalid UUID format.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = ModerationEvent.objects.get(uuid=moderation_id)
        except ModerationEvent.DoesNotExist:
            return handle_path_error(
                field="moderation_id",
                message="Moderation event not found.",
                status_code=status.HTTP_404_NOT_FOUND
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
                "message": 'The request body contains '
                'invalid or missing fields.',
                "error": [serializer.errors]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @handle_errors_decorator
    def add_production_location(self, request, moderation_id):
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied(
                detail="Only the Moderator can perform this action."
            )

        if not is_valid_uuid(moderation_id):
            return handle_path_error(
                field="moderation_id",
                message="Invalid UUID format.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = ModerationEvent.objects.get(uuid=moderation_id)
        except ModerationEvent.DoesNotExist:
            return handle_path_error(
                field="moderation_id",
                message="Moderation event not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if event.status != ModerationEvent.Status.PENDING:
            return Response(
                {
                    "message": "The request query is invalid.",
                    "errors": [
                        {
                            "field": "status",
                            "message": "Moderation status must be PENDING."
                        }
                    ]
                },
                status=status.HTTP_410_GONE
            )

        event.add_production_location(request.data)
        return Response(status=status.HTTP_200_OK)