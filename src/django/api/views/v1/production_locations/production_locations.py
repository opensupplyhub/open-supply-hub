from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from api.services.search import OpenSearchService
from api.views.v1.opensearch_query_builder \
    import OpenSearchQueryDirector, OpenSearchQueryBuilder


class ProductionLocations(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opensearch_service = OpenSearchService()
        self.opensearch_query_builder = OpenSearchQueryBuilder()

    def list(self, request):
        opensearch_query_director = \
            OpenSearchQueryDirector(self.opensearch_query_builder)
        query_params = request.GET
        query_body = opensearch_query_director.build_query(query_params)
        response = self.opensearch_service. \
            search_production_locations(query_body)
        return Response(response)
