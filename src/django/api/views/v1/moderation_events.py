from typing import Tuple

from django.http import QueryDict
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from api.constants import (
    APIV1CommonErrorMessages,
    APIV1ModerationEventErrorMessages
)
from api.moderation_event_actions.approval.add_production_location \
    import AddProductionLocation
from api.moderation_event_actions.approval.update_production_location \
    import UpdateProductionLocation
from api.permissions import IsRegisteredAndConfirmed, IsSuperuser
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
    serialize_params,
)
from api.mail import (
    send_slc_contribution_approval_email,
    send_slc_contribution_rejected_email
)


class ModerationEvents(ViewSet):
    swagger_schema = None
    permission_classes = [IsRegisteredAndConfirmed]

    def get_permissions(self):
        action_permissions = {
            'partial_update': [IsSuperuser],
            'add_production_location': [IsSuperuser],
            'update_production_location': [IsSuperuser],
        }

        permission_classes = action_permissions.get(
            self.action, self.permission_classes
        )
        return [permission() for permission in permission_classes]

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
            raise NotFound(
                detail=APIV1ModerationEventErrorMessages.EVENT_NOT_FOUND
            )

        return Response(events[0])

    def partial_update(self, request, pk=None):
        ModerationEventsService.validate_uuid(pk)

        event = ModerationEventsService.fetch_moderation_event_by_uuid(pk)

        serializer = ModerationEventUpdateSerializer(
            instance=event,
            data=request.data,
            user=request.user,
            partial=True
        )

        if not serializer.is_valid():
            raise ValidationError(
                {
                    "detail": APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                    "errors": [serializer.errors],
                }
            )

        serializer.save()        
        event.refresh_from_db()

        send_slc_contribution_rejected_email(request, event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST'],
        url_path='production-locations',
    )
    def add_production_location(self, request, pk=None):
        ModerationEventsService.validate_uuid(pk)

        event = ModerationEventsService.fetch_moderation_event_by_uuid(pk)
        ModerationEventsService.validate_moderation_status(event.status)

        add_production_location_processor = AddProductionLocation(
            event, request.user
        )

        try:
            item = add_production_location_processor.process_moderation_event()
        except Exception as error:
            return ModerationEventsService.handle_processing_error(error)

        return Response(
            {"os_id": item.facility_id}, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['PATCH'],
        url_path='production-locations/(?P<os_id>[^/.]+)',
    )
    def update_production_location(self, request, pk=None, os_id=None):
        ModerationEventsService.validate_uuid(pk)

        event = ModerationEventsService.fetch_moderation_event_by_uuid(pk)

        ModerationEventsService.validate_moderation_status(event.status)

        ModerationEventsService.validate_location_os_id(os_id)

        update_production_location_processor = UpdateProductionLocation(
            event, request.user, os_id
        )

        try:
            item = (
                update_production_location_processor.process_moderation_event()
            )
        except Exception as error:
            return ModerationEventsService.handle_processing_error(error)

        send_slc_contribution_approval_email(request, event, item)
        return Response({"os_id": item.facility_id}, status=status.HTTP_200_OK)
