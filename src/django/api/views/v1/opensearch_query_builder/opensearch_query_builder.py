import copy
from api.views.v1.opensearch_query_builder. \
    opensearch_query_builder_interface import OpenSearchQueryBuilderInterface
from api.views.v1.parameters_list import V1_PARAMETERS_LIST


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
        self.default_sort = V1_PARAMETERS_LIST.NAME
        self.default_sort_order = 'asc'
        self.build_options = {
            'country': self.__build_country,
            'os_id': self.__build_os_id,
            'number_of_workers': self.__build_number_of_workers
        }

    def reset(self):
        self.query_body = copy.deepcopy(self.default_query_body)

    def __build_number_of_workers(self, field, range_query):
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
                                                'lte',
                                                float('inf')
                                            ),
                                            'gte': range_query.get(
                                                'gte',
                                                float('-inf')
                                            )
                                        }
                                    }
                                },
                                {
                                    'range': {
                                        f'{field}.max': {
                                            'gte': range_query.get(
                                                'gte',
                                                float('-inf')
                                            ),
                                            'lte': range_query.get(
                                                'lte',
                                                float('inf')
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

    def __build_os_id(self, field):
        return field

    def __build_country(self, field):
        return f'{field}.alpha_2'

    def add_size(self, size):
        self.query_body[V1_PARAMETERS_LIST.SIZE] = size

    def add_match(self, field, value, fuzziness=None):
        if fuzziness is None:
            fuzziness = self.default_fuzziness
        match_query = {
            'match': {field: {'query': value, 'fuzziness': fuzziness}}
        }
        self.query_body['query']['bool']['must'].append(match_query)

    def add_multi_match(self, query):
        self.query_body['query']['bool']['must'].append({
            'multi_match': {
                'query': query,
                'fields': [
                    f'{V1_PARAMETERS_LIST.NAME}^2',
                    V1_PARAMETERS_LIST.ADDRESS,
                    V1_PARAMETERS_LIST.DESCRIPTION,
                    V1_PARAMETERS_LIST.NAME_LOCAL
                ],
                'fuzziness': self.default_fuzziness
            }
        })

    def add_terms(self, field, values):
        if not values:
            return self.query_body

        terms_field = self.build_options \
            .get(field, lambda x: f'{x}.keyword')(field)

        existing_terms = next(
            (item['terms'] for item in self.query_body['query']['bool']['must']
             if 'terms' in item and terms_field in item['terms']), None)

        if existing_terms:
            existing_terms[terms_field].extend(values)
        else:
            self.query_body['query']['bool']['must'].append({
                'terms': {terms_field: values}
            })

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
            build_action = self.build_options.get(field)
            if build_action:
                build_action(field, range_query)
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

    def add_sort(self, field, order_by=None):
        if order_by is None:
            order_by = self.default_sort_order
        self.query_body['sort'] \
            .append({f'{field}.keyword': {'order': order_by}})

    def add_search_after(self, search_after):
        # search_after can't be present as empty by default in query_body
        if V1_PARAMETERS_LIST.SEARCH_AFTER not in self.query_body:
            self.query_body[V1_PARAMETERS_LIST.SEARCH_AFTER] = []
        '''
        There should always be sort if there is a search_after field.
        So if it is empty, sort by name by default
        '''
        if not self.query_body['sort']:
            sort_criteria = {
                f'{self.default_sort}.keyword': {
                    'order': self.default_sort_order
                }
            }
            self.query_body['sort'].append(sort_criteria)

        self.query_body[V1_PARAMETERS_LIST.SEARCH_AFTER] \
            .append(search_after)

    def get_final_query_body(self):
        return self.query_body
