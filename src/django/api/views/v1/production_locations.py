from django.http import QueryDict
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator
)
from api.services.opensearch.search import OpenSearchService
from api.views.v1.opensearch_query_builder.opensearch_query_builder \
    import OpenSearchQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.serializers.v1.production_locations_serializer \
    import ProductionLocationsSerializer
from api.views.v1.index_names import OpenSearchIndexNames


class ProductionLocations(ViewSet):
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
        location = response.get('data', []).pop()
        return Response(location)
