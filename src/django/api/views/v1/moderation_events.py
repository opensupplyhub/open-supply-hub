from typing import Tuple

from django.http import QueryDict
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from api.moderation_event_actions.approval.add_production_location \
    import AddProductionLocation
from api.moderation_event_actions.approval.update_production_location \
    import UpdateProductionLocation
from api.moderation_event_actions.approval.event_approval_context \
    import EventApprovalContext
from api.permissions import IsRegisteredAndConfirmed
from api.serializers.v1.moderation_event_update_serializer \
    import ModerationEventUpdateSerializer
from api.serializers.v1.moderation_events_serializer \
    import ModerationEventsSerializer
from api.serializers.v1.update_production_location_serializer \
    import UpdateProductionLocationSerializer
from api.services.moderation_events_service import ModerationEventsService
from api.services.opensearch.search import OpenSearchService
from api.views.v1.index_names import OpenSearchIndexNames
from api.views.v1.opensearch_query_builder.moderation_events_query_builder \
    import ModerationEventsQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director import \
    OpenSearchQueryDirector
from api.views.v1.utils import (
    handle_errors_decorator,
    serialize_params,
)


class ModerationEvents(ViewSet):
    swagger_schema = None
    permission_classes = [IsRegisteredAndConfirmed]

    @staticmethod
    def __init_opensearch() -> Tuple[OpenSearchService,
                                     OpenSearchQueryDirector]:
        opensearch_service = OpenSearchService()
        moderation_events_query_builder = ModerationEventsQueryBuilder()
        opensearch_query_director = OpenSearchQueryDirector(
            moderation_events_query_builder
        )

        return (opensearch_service, opensearch_query_director)

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

        opensearch_service, opensearch_query_director = \
            self.__init_opensearch()
        query_body = opensearch_query_director.build_query(
            request.GET
        )

        response = opensearch_service.search_index(
            OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            query_body
        )
        return Response(response)

    @handle_errors_decorator
    def retrieve(self, _,  pk=None):
        ModerationEventsService.validate_uuid(pk)

        opensearch_service, opensearch_query_director = \
            self.__init_opensearch()
        query_params = QueryDict('', mutable=True)
        query_params.update({'moderation_id': pk})
        query_body = opensearch_query_director.build_query(
            query_params
        )
        response = opensearch_service.search_index(
            OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            query_body
        )

        events = response.get("data", [])

        if len(events) == 0:
            return Response(
                data={
                    "detail": 'The moderation event with the '
                    'given uuid was not found.',
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(events[0])

    @handle_errors_decorator
    def partial_update(self, request, pk=None):
        ModerationEventsService.validate_user_permissions(request)

        ModerationEventsService.validate_uuid(pk)

        event = ModerationEventsService.fetch_moderation_event_by_uuid(
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
    @action(
        detail=True, methods=['POST', 'PATCH'], url_path='production-locations'
    )
    def manage_production_location(self, request, pk=None):
        ModerationEventsService.validate_user_permissions(request)

        ModerationEventsService.validate_uuid(pk)

        event = ModerationEventsService.fetch_moderation_event_by_uuid(pk)
        ModerationEventsService.validate_moderation_status(event.status)

        if request.method == 'POST':
            manage_production_location_context = EventApprovalContext(
                AddProductionLocation(event)
            )
            status_code = status.HTTP_201_CREATED

        else:
            serializer = UpdateProductionLocationSerializer(data=request.data)

            if not serializer.is_valid():
                errors = [
                    {"field": field, "detail": detail}
                    for field, details in serializer.errors.items()
                    for detail in details
                ]

                raise ValidationError({
                    "detail": 'The request body contains '
                    'invalid or missing fields.',
                    "errors": errors
                })

            os_id = serializer.validated_data.get('os_id')

            manage_production_location_context = EventApprovalContext(
                UpdateProductionLocation(event, os_id)
            )

            status_code = status.HTTP_200_OK

        try:
            item = manage_production_location_context.run_processing()
        except Exception as error:
            return ModerationEventsService.handle_processing_error(error)

        return Response(
            {"os_id": item.facility_id},
            status=status_code
        )
