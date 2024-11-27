from django.http import QueryDict
from django.db import transaction
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator,
)
from api.services.opensearch.search import OpenSearchService
from api.views.v1.opensearch_query_builder.production_locations_query_builder \
    import ProductionLocationsQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.serializers.v1.production_locations_serializer \
    import ProductionLocationsSerializer
from api.views.v1.index_names import OpenSearchIndexNames
from api.permissions import IsRegisteredAndConfirmed
from api.moderation_event_actions.creation.moderation_event_creator \
    import ModerationEventCreator
from api.moderation_event_actions.creation.location_contribution \
    .location_contribution import LocationContribution
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.models.moderation_event import ModerationEvent
from api.throttles import DataUploadThrottle
from api.constants import (
    APIV1CommonErrorMessages,
    NON_FIELD_ERRORS_KEY,
    APIV1LocationContributionErrorMessages
)


class ProductionLocations(ViewSet):
    swagger_schema = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opensearch_service = OpenSearchService()
        self.opensearch_query_builder = ProductionLocationsQueryBuilder()
        self.opensearch_query_director = OpenSearchQueryDirector(
            self.opensearch_query_builder
        )

    def get_permissions(self):
        '''
        Redefines the parent method and returns the list of permissions for
        the ViewSet action methods.
        '''
        permission_classes = []
        if self.action == 'create':
            permission_classes.append(
                IsRegisteredAndConfirmed
            )

        # Combine custom permissions with global application-level permissions
        # set via the DEFAULT_PERMISSION_CLASSES setting.
        combined_permission_classes = \
            permission_classes + self.permission_classes

        return [permission() for permission in combined_permission_classes]

    def get_throttles(self):
        if self.action == 'create':
            return [DataUploadThrottle()]

        # Call the parent method to use the default throttling setup in the
        # settings.py file.
        return super().get_throttles()

    def get_parsers(self):
        '''
        Override the default parser classes for specific actions.
        '''
        if self.request.method == 'POST':
            # Use JSONParser for the 'create' action to restrict all media
            # types except 'application/json'.
            return [JSONParser()]

        # Call the parent method to use the default parsers setup in the
        # settings.py file.
        return super().get_parsers()

    @handle_errors_decorator
    def list(self, request):
        _, error_response = serialize_params(
            ProductionLocationsSerializer,
            request.GET,
        )

        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        query_body = self.opensearch_query_director.build_query(
            request.GET,
        )
        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body,
        )
        return Response(response)

    @handle_errors_decorator
    def retrieve(self, _, pk=None):
        query_params = QueryDict("", mutable=True)
        query_params.update({"os_id": pk})
        query_body = self.opensearch_query_director.build_query(query_params)
        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body,
        )
        locations = response.get("data", [])

        if len(locations) == 0:
            return Response(
                data={
                    "detail": "The location with the given id was not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(locations[0])

    @transaction.atomic
    def create(self, request):
        if not isinstance(request.data, dict):
            data_type = type(request.data).__name__
            specific_error = APIV1LocationContributionErrorMessages \
                .invalid_data_type_error(data_type)
            return Response(
                {
                    'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                    'errors': [{
                        'field': NON_FIELD_ERRORS_KEY,
                        'detail': specific_error
                    }]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        location_contribution_strategy = LocationContribution()
        moderation_event_creator = ModerationEventCreator(
            location_contribution_strategy
        )
        event_dto = CreateModerationEventDTO(
            contributor_id=request.user.contributor,
            raw_data=request.data,
            request_type=ModerationEvent.RequestType.CREATE
        )
        result = moderation_event_creator.perform_event_creation(event_dto)

        if result.errors:
            return Response(
                result.errors,
                status=result.status_code)

        return Response(
            {
                'moderation_id': result.moderation_event.uuid,
                'moderation_status': result.moderation_event.status,
                'created_at': result.moderation_event.created_at
            },
            status=result.status_code
        )
