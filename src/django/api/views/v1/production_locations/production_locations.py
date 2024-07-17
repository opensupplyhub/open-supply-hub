from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.services.search import OpenSearchService


@api_view(['GET'])
def production_locations_view(request,
                              opensearch_service=OpenSearchService()):

    size = request.query_params.get('size', 10)
    start_after = request.query_params.get('start_after', None)
    query = request.query_params.get('query', None)
    sort_by = request.query_params.get('sort_by', 'name')
    order_by = request.query_params.get('order_by', 'asc')

    '''
    TODO: using sorting for keyword search will increase response time,
    see https://forum.opensearch.org/t/issue-with-message-field-data/13420
    '''
    query_body = {
        'size': size,
        'query': {
            'bool': {
                'must': []
            }
        },
        'sort': [
            {f"{sort_by}.keyword": {'order': order_by}}
        ]
    }

    if query:
        query_body['query']['bool']['must'].append({
            'multi_match': {
                'query': query,
                'fields': ['name^2', 'address', 'description', 'name_local']
            }
        })

    field_queries = {
        'name': 'match',
        'name_local': 'match',
        'description': 'match',
        'address': 'match',
        'sector': 'terms',
        'product_type': 'terms',
        'location_type': 'terms',
        'number_of_workers': 'range',
        'coordinates': 'geo_distance',
        'minimum_order_quantity': 'match',
        'average_lead_time': 'match',
        'percent_female_workers': 'match',
        'affiliations': 'match',
        'certifications_standards_regulations': 'terms',
        'country': 'match',
    }

    for field, query_type in field_queries.items():

        value = (
            request.query_params.getlist(field)
            if query_type == 'terms'
            else request.query_params.get(field)
        )

        if value:
            if query_type == 'geo_distance':
                query_body['query']['bool']['must'] \
                    .append({query_type: {
                                'distance': '100km',
                                'location': value
                            }})
            else:
                query_body['query']['bool']['must'] \
                    .append({query_type: {field: value}})

    if start_after:
        query_body['search_after'] = [start_after]

    response = opensearch_service. \
        search_production_locations(query_body)

    return Response(response)
