from django.http import QueryDict
from django.db import transaction
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator
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
        if self.action == 'create':
            permission_classes = [IsRegisteredAndConfirmed]

        # Combine custom permissions with global application-level permissions
        # set via the DEFAULT_PERMISSION_CLASSES setting.
        combined_permission_classes = \
            permission_classes + self.permission_classes

        return [permission() for permission in combined_permission_classes]

    @handle_errors_decorator
    def list(self, request):
        _, error_response = serialize_params(
            ProductionLocationsSerializer,
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
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body
        )
        return Response(response)

    @handle_errors_decorator
    def retrieve(self, request,  pk=None):
        query_params = QueryDict('', mutable=True)
        query_params.update({'os_id': pk})
        query_body = self.opensearch_query_director.build_query(
            query_params
        )
        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body
        )
        return Response(response)

    @transaction.atomic
    def create(self, request):
        location_contribution_strategy = LocationContribution()
        moderation_event_creator = ModerationEventCreator(
            location_contribution_strategy
        )
        result = moderation_event_creator.perform_event_creation(
            request.data
        )

        if result.errors:
            return Response(result.errors)
        return Response(result.raw_data)
