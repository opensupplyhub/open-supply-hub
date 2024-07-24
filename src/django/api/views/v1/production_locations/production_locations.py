from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.services.search import OpenSearchService
from api.views.v1.opensearch_query_builder import \
    OpenSearchQueryDirector, OpenSearchQueryBuilder


@api_view(['GET'])
def production_locations(
        request,
        opensearch_service=OpenSearchService(),
        opensearch_query_builder=OpenSearchQueryBuilder()):

    opensearch_query_director = \
        OpenSearchQueryDirector(opensearch_query_builder)

    query_params = request.GET
    query_body = opensearch_query_director.build_query(query_params)

    response = opensearch_service. \
        search_production_locations(query_body)

    return Response(response)
