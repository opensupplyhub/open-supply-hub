from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.services.search import OpenSearchService

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
    # TODO: Refactor query_body creation for all OpenSearch endpoints using Builder pattern
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
        'minimum_order_quantity': 'terms',
        'average_lead_time': 'terms',
        'percent_female_workers': 'range',
        'affiliations': 'terms',
        'certifications_standards_regulations': 'terms',
        'country': 'terms',
        'coordinates': 'geo_distance',
    }

    for field, query_type in field_queries.items():
        if query_type == 'terms':
            value = request.query_params.getlist(field)

        elif query_type == 'range':
            min_value = request.query_params.get(f'{field}[min]')
            max_value = request.query_params.get(f'{field}[max]')
            
            min_value = int(min_value) if min_value is not None else None
            max_value = int(max_value) if max_value is not None else None

            range_query = {}
            if min_value is not None:
                range_query['gte'] = min_value
            if max_value is not None:
                range_query['lte'] = max_value

            if range_query:
                if field == 'number_of_workers':
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
                elif field == 'percent_female_workers':
                    query_body['query']['bool']['must'].append({
                        'range': {
                            field: range_query
                        }
                    })

        elif query_type == 'geo_distance' and field == 'coordinates':
            lat = request.query_params.get('coordinates[lat]')
            lon = request.query_params.get('coordinates[lon]')
            distance = "10km"

            if lat and lon:
                query_body['query']['bool']['must'].append({
                    'geo_distance': {
                        'distance': distance,
                        'coordinates': {
                            'lat': float(lat),
                            'lon': float(lon)
                        }
                    }
                })

        else:
            value = request.query_params.get(field)

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


    if start_after:
        query_body['search_after'] = [start_after]

    response = opensearch_service. \
        search_production_locations(query_body)

    return Response(response)
