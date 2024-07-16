from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.services.opensearch import search_production_locations

@api_view(['GET'])
def production_locations_view(request):
    size = request.query_params.get('size', 10)
    start_after = request.query_params.get('start_after', None)
    query = request.query_params.get('query', None)
    name = request.query_params.get('name', None)
    name_local = request.query_params.get('name_local', None)
    description = request.query_params.get('description', None)
    address = request.query_params.get('address', None)
    sector = request.query_params.getlist('sector', None)
    product_type = request.query_params.getlist('product_type', None)
    location_type = request.query_params.getlist('location_type', None)
    number_of_workers = request.query_params.get('number_of_workers', None)
    coordinates = request.query_params.get('coordinates', None)
    minimum_order_quantity = request.query_params.get('minimum_order_quantity', None)
    average_lead_time = request.query_params.get('average_lead_time', None)
    percent_female_workers = request.query_params.get('percent_female_workers', None)
    affiliations = request.query_params.get('affiliations', None)
    certifications = request.query_params.getlist('certifications_standards_regulations', None)
    country = request.query_params.get('country', None)
    sort_by = request.query_params.get('sort_by', 'name')
    order_by = request.query_params.get('order_by', 'asc')

    query_body = {
        'size': size,
        'query': {
            'bool': {
                'must': []
            }
        },
        'sort': [
            {sort_by: {'order': order_by}}
        ]
    }

    if query:
        query_body['query']['bool']['must'].append({
            'multi_match': {
                'query': query,
                'fields': ['name^2', 'address', 'description', 'name_local']
            }
        })
    if name:
        query_body['query']['bool']['must'].append({'match': {'name': name}})
    if name_local:
        query_body['query']['bool']['must'].append({'match': {'name_local': name_local}})
    if description:
        query_body['query']['bool']['must'].append({'match': {'description': description}})
    if address:
        query_body['query']['bool']['must'].append({'match': {'address': address}})
    if sector:
        query_body['query']['bool']['must'].append({'terms': {'sector': sector}})
    if product_type:
        query_body['query']['bool']['must'].append({'terms': {'product_type': product_type}})
    if location_type:
        query_body['query']['bool']['must'].append({'terms': {'location_type': location_type}})
    if number_of_workers:
        query_body['query']['bool']['must'].append({'range': {'number_of_workers': number_of_workers}})
    if coordinates:
        query_body['query']['bool']['must'].append({'geo_distance': {'distance': '100km', 'location': coordinates}})
    if minimum_order_quantity:
        query_body['query']['bool']['must'].append({'match': {'minimum_order_quantity': minimum_order_quantity}})
    if average_lead_time:
        query_body['query']['bool']['must'].append({'match': {'average_lead_time': average_lead_time}})
    if percent_female_workers:
        query_body['query']['bool']['must'].append({'match': {'percent_female_workers': percent_female_workers}})
    if affiliations:
        query_body['query']['bool']['must'].append({'match': {'affiliations': affiliations}})
    if certifications:
        query_body['query']['bool']['must'].append({'terms': {'certifications_standards_regulations': certifications}})
    if country:
        query_body['query']['bool']['must'].append({'match': {'country': country}})

    if start_after:
        query_body['search_after'] = [start_after]

    response = search_production_locations(query_body)
    return Response(response)
