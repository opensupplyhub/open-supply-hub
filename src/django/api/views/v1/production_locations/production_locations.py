from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.services.search import OpenSearchService

# TODO: Remove loggers from here later
import logging
log = logging.getLogger(__name__)

@api_view(['GET'])
def production_locations(request,
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
    # TODO: abstract common query_body for all OpenSearch endpoints
    query_body = {
        'track_total_hits': 'true',
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
                'fields': ['name^2', 'address', 'description', 'name_local'],
                'fuzziness': '2'
            }
        })

    field_queries = {
        'name': 'match',
        'name_local': 'match',
        'description': 'match',
        'address': 'match',
        'sector': 'terms',
        'product_type': 'terms',
        'processing_type': 'terms',
        'location_type': 'terms',
        'number_of_workers': 'range',
        'coordinates': 'geo_distance',
        'minimum_order_quantity': 'terms',
        'average_lead_time': 'terms',
        'percent_female_workers': 'range',
        'affiliations': 'terms',
        'certifications_standards_regulations': 'terms',
        'country': 'terms',
    }

    for field, query_type in field_queries.items():

        logging.info(f"query_type is {query_type}")
        logging.info(f"field is {field}")
        logging.info(f"query_params are {request.query_params.dict()}")

        if query_type == 'terms':
            value = request.query_params.getlist(field)
        elif query_type == 'range' and field in ['number_of_workers']:
            min_value = request.query_params.get(f'{field}[min]', 0)
            max_value = request.query_params.get(f'{field}[max]')

            min_value = int(min_value) if min_value else None
            max_value = int(max_value) if max_value else None

            range_query = {}
            if min_value is not None:
                range_query['gte'] = min_value
            if max_value is not None:
                range_query['lte'] = max_value

            if range_query:
                query_body['query']['bool']['must'].append({
                    'bool': {
                        'should': [
                            {
                                'bool': {
                                    'must': [
                                        {
                                            'range': {
                                                f'{field}.min': {
                                                    'lte': range_query.get('lte', float('inf')),
                                                    'gte': range_query.get('gte', float('-inf'))
                                                }
                                            }
                                        },
                                        {
                                            'range': {
                                                f'{field}.max': {
                                                    'gte': range_query.get('gte', float('-inf')),
                                                    'lte': range_query.get('lte', float('inf'))
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                })
        else:
            value = request.query_params.get(field)

        logging.info(f"value is {value}")

        if value:
            if query_type == 'geo_distance':
                query_body['query']['bool']['must'].append({
                    query_type: {
                        'distance': '100km',
                        'location': value
                    }
                })
            elif query_type == 'terms' and field == 'country':
                query_body['query']['bool']['must'].append({
                    query_type: {
                        f"{field}.alpha_2.keyword": value
                    }
                })
            elif query_type == 'terms' and field in ['sector',
                'product_type', 
                'location_type',
                'processing_type',
                'certifications_standards_regulations',
                'average_lead_time',
                'minimum_order_quantity',
                'affiliations']:
                query_body['query']['bool']['must'].append({
                    query_type: {
                        f"{field}.keyword": value
                    }
                })
            # TODO: there is a problem with sorting that will sort by name by default
            # and not by the score in the output
            elif query_type == 'match' and field in ['address', 'name']:
                query_body['query']['bool']['must'].append({
                    'match': {
                        field: {
                            'query': value,
                            'fuzziness': '2'
                        }
                    }
                })
            else:
                query_body['query']['bool']['must'].append({
                    query_type: {
                        field: value
                    }
                })


    logging.info(f"query body is {query_body}")

    if start_after:
        query_body['search_after'] = [start_after]

    response = opensearch_service. \
        search_production_locations(query_body)

    return Response(response)