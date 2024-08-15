from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from api.views.v1.utils import (
    serialize_params,
    handle_value_error,
    handle_opensearch_exception
)
from api.services.search import OpenSearchService, OpenSearchServiceException
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

    def list(self, request):
        opensearch_query_director = OpenSearchQueryDirector(
            self.opensearch_query_builder
        )
        try:
            params, error_response = serialize_params(
                ProductionLocationsSerializer,
                request.GET
            )
            if error_response:
                return Response(
                    error_response,
                    status=status.HTTP_400_BAD_REQUEST
                )

            query_body = opensearch_query_director.build_query(
                request.GET
            )
            response = self.opensearch_service.search_index(
                OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
                query_body
            )
            return Response(response)

        except ValueError as e:
            return handle_value_error(e)

        except OpenSearchServiceException as e:
            return handle_opensearch_exception(e)
