from .opensearch_query_builder_interface import OpenSearchQueryBuilderInterface

class OpenSearchQueryBuilder:
    def __init__(self):
        # TODO: some of these fields might be also constructed
        self.query_body = {
            "track_total_hits": "true",
            "size": 10,
            "query": {
                "bool": {
                    "must": []
                }
            },
        }

    def add_terms(self, field, values):
        if values:
            self.query_body["query"]["bool"]["must"].append({
                "terms": {field: values}
            })
        return self

    def add_range(self, field, min_value=None, max_value=None):
        min_value = int(min_value) if min_value else None
        max_value = int(max_value) if max_value else None

        range_query = {}
        if min_value is not None:
            range_query["gte"] = min_value
        if max_value is not None:
            range_query["lte"] = max_value

        if range_query:
            self.query_body["query"]["bool"]["must"].append({
                "range": {field: range_query}
            })
        return self

    def add_geo_distance(self, field, lat, lon, distance="10km"):
        if lat is not None and lon is not None:
            self.query_body["query"]["bool"]["must"].append({
                "geo_distance": {
                    "distance": distance,
                    field: {
                        "lat": float(lat),
                        "lon": float(lon)
                    }
                }
            })
        return self

    def add_match(self, field, value):
        if value:
            self.query_body["query"]["bool"]["must"].append({
                "match": {field: value}
            })
        return self

    def add_sort(self, field, order="asc"):
        self.query_body["sort"].append({
            field: {"order": order}
        })
        return self

    def add_start_after(self, start_after):
        if start_after:
            self.query_body['search_after'] = start_after

    def build(self):
        return self.query_body

# TODO: field options will be the same for all views, make them private static props

'''
Client code example

builder = QueryBuilder()

for field, query_type in field_queries.items():
    if query_type == 'terms':
        value = request_query_params.getlist(field)
        builder.add_terms(field, value)
    elif query_type == 'range' and field in ['number_of_workers', 'percent_female_workers']:
        min_value = request_query_params.get(f'{field}[min]')
        max_value = request_query_params.get(f'{field}[max]')
        builder.add_range(field, min_value, max_value)
    elif query_type == 'geo_distance' and field == 'coordinates':
        lat = request_query_params.get('coordinates[lat]')
        lon = request_query_params.get('coordinates[lon]')
        builder.add_geo_distance(field, lat, lon)
        
query_body = builder.build()
print(query_body)
'''
