import logging

from django.http import QueryDict

from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.moderation_event_actions.approval.add_production_location_strategy \
    import AddProductionLocationStrategy
from api.moderation_event_actions.approval.event_approval_context \
    import EventApprovalContext
from api.models.moderation_event import ModerationEvent
from api.permissions import IsRegisteredAndConfirmed
from api.serializers.v1.moderation_event_update_serializer \
    import ModerationEventUpdateSerializer
from api.serializers.v1.moderation_events_serializer \
    import ModerationEventsSerializer
from api.serializers.v1.opensearch_common_validators.moderation_id_validator \
    import ModerationIdValidator
from api.services.opensearch.search import OpenSearchService
from api.views.v1.index_names import OpenSearchIndexNames
from api.views.v1.opensearch_query_builder.moderation_events_query_builder \
    import ModerationEventsQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.views.v1.utils import (
    handle_errors_decorator,
    handle_path_error,
    serialize_params,
)

log = logging.getLogger(__name__)


class ModerationEvents(ViewSet):
    swagger_schema = None
    permission_classes = [IsRegisteredAndConfirmed]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opensearch_service = OpenSearchService()
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
        if not ModerationIdValidator.is_valid_uuid(pk):
            return handle_path_error(
                field="moderation_id",
                message="Invalid UUID format.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

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
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied(
                detail="Only the Moderator can perform this action."
            )

        if not ModerationIdValidator.is_valid_uuid(pk):
            return handle_path_error(
                field="moderation_id",
                message="Invalid UUID format.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = ModerationEvent.objects.get(uuid=pk)
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

        self.__validate_user_permissions(request)

        if not ModerationIdValidator.is_valid_uuid(moderation_id):
            return handle_path_error(
                field="moderation_id",
                message="Invalid UUID format.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            event = ModerationEvent.objects.get(uuid=moderation_id)
        except ModerationEvent.DoesNotExist:
            return handle_path_error(
                field="moderation_id",
                message="Moderation event not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if event.status != ModerationEvent.Status.PENDING:
            return handle_path_error(
                field="status",
                message="Moderation status must be PENDING.",
                status_code=status.HTTP_410_GONE,
            )

        add_production_location = EventApprovalContext(
            AddProductionLocationStrategy(event)
        )

        try:
            item = add_production_location.run_processing()
        except Exception as error:
            return self.__handle_processing_error(error)

        return Response(
            {"os_id": item.facility_id}, status=status.HTTP_201_CREATED
        )

    @staticmethod
    def __validate_user_permissions(request):
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied(
                detail="Only the Moderator can perform this action."
            )

    @staticmethod
    def __handle_processing_error(error_message):
        log.error(f'[Moderation Event] Error: {str(error_message)}')
        return Response(
            {
                "message": "An unexpected error occurred while "
                "processing the request."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
