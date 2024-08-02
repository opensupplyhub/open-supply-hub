from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from api.services.search import OpenSearchService
from api.views.v1.opensearch_query_builder.opensearch_query_builder \
    import OpenSearchQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.serializers.v1.production_locations_serializer \
    import ProductionLocationsSerializer
import logging

logger = logging.getLogger(__name__)


class ProductionLocations(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opensearch_service = OpenSearchService()
        self.opensearch_query_builder = OpenSearchQueryBuilder()

    def list(self, request):
        opensearch_query_director = OpenSearchQueryDirector(
            self.opensearch_query_builder
        )
        query_params = request.GET

        '''
        There is no native support of OpenAPI deepObject parameters
        in Django serializers, so we need to parse them manually
        '''
        flattened_query_params = {
            key.replace(']', '').replace('[', '_'): value
            for key, value in query_params.items()
        }

        params = ProductionLocationsSerializer(data=flattened_query_params)

        try:
            if not params.is_valid():
                error_response = {
                    'message': None,
                    'errors': []
                }

                error_response['message'] = (
                    params.errors.get('message')[0].title()
                )

                for error_item in params.errors.get('errors', []):
                    field = str(error_item.get('field', '')).title()
                    message = str(error_item.get('message', '')).title()
                    error_response['errors'].append({
                        'field': field,
                        'message': message
                    })

                return Response(
                    error_response,
                    status=status.HTTP_400_BAD_REQUEST
                )

            query_body = opensearch_query_director.build_query(
                query_params
            )
            response = self.opensearch_service.search_production_locations(
                query_body
            )
            return Response(response)

        except ValueError as e:
            logger.error(f'Error processing request: {e}')
            return Response(
                {
                    "message": "The request query is invalid.",
                    "errors": [
                        {
                            "field": "general",
                            "message": (
                                "There was a problem processing your request. "
                                "Please check your input."
                            )
                        }
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
