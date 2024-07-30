import copy
from .opensearch_query_builder_interface import OpenSearchQueryBuilderInterface


class OpenSearchQueryBuilder(OpenSearchQueryBuilderInterface):
    def __init__(self):
        self.default_query_body = {
            'track_total_hits': 'true',
            'size': 10,
            'query': {'bool': {'must': []}},
            'sort': []
        }
        self.query_body = copy.deepcopy(self.default_query_body)
        self.default_fuzziness = 2
        self.default_sort = 'name'
        self.default_sort_order = 'asc'

    def reset(self):
        self.query_body = copy.deepcopy(self.default_query_body)

    def add_size(self, size):
        self.query_body['size'] = size

    def add_match(self, field, value, fuzziness=None):
        match_query = {'match': {field: {'query': value}}}
        if fuzziness:
            match_query['match'][field]['fuzziness'] = fuzziness
        self.query_body['query']['bool']['must'].append(match_query)

    def add_multi_match(self, query):
        self.query_body['query']['bool']['must'].append({
            'multi_match': {
                'query': query,
                'fields': ['name^2', 'address', 'description', 'name_local'],
                'fuzziness': self.default_fuzziness
            }
        })

    def add_terms(self, field, values):
        if field == 'country':
            terms_query = {'terms': {f'{field}.alpha_2': values}}
        else:
            terms_query = {'terms': {f'{field}.keyword': values}}
        self.query_body['query']['bool']['must'].append(terms_query)

    def add_range(self, field, query_params):
        min_value = query_params.get(f'{field}[min]')
        max_value = query_params.get(f'{field}[max]')
        min_value = int(min_value) if min_value else None
        max_value = int(max_value) if max_value else None

        range_query = {}
        if min_value is not None:
            range_query['gte'] = min_value
        if max_value is not None:
            range_query['lte'] = max_value

        if range_query:
            if field == 'number_of_workers':
                self.query_body['query']['bool']['must'].append({
                    'bool': {
                        'should': [
                            {
                                'bool': {
                                    'must': [
                                        {
                                            'range': {
                                                f'{field}.min': {
                                                    'lte': range_query.get(
                                                        'lte', float('inf')
                                                    ),
                                                    'gte': range_query.get(
                                                        'gte', float('-inf')
                                                    )
                                                }
                                            }
                                        },
                                        {
                                            'range': {
                                                f'{field}.max': {
                                                    'gte': range_query.get(
                                                        'gte', float('-inf')
                                                    ),
                                                    'lte': range_query.get(
                                                        'lte', float('inf')
                                                    )
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
                self.query_body['query']['bool']['must'].append({
                    'range': {field: range_query}
                })

    def add_geo_distance(self, field, lat, lon, distance):
        geo_distance_query = {
            'geo_distance': {
                'distance': distance,
                field: {'lat': lat, 'lon': lon}
            }
        }
        self.query_body['query']['bool']['must'].append(geo_distance_query)

    def add_sort(self, field, order='asc'):
        self.query_body['sort'].append({f'{field}.keyword': {'order': order}})

    def add_start_after(self, search_after):
        # search_after can't be present as empty by default in query_body
        if 'search_after' not in self.query_body:
            self.query_body['search_after'] = []
        '''
        There should be always sort if there is a search_after field.
        So if it is empty, sort by name by default
        '''
        if not self.query_body['sort']:
            sort_criteria = {
                f'{self.default_sort}.keyword': {
                    'order': self.default_sort_order
                }
            }
            self.query_body['sort'].append(sort_criteria)

        self.query_body['search_after'].append(search_after)

    def get_final_query_body(self):
        return self.query_body
