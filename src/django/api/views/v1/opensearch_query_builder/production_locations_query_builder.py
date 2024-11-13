import copy
from api.views.v1.opensearch_query_builder. \
    opensearch_query_builder import OpenSearchQueryBuilder
from api.views.v1.parameters_list import V1_PARAMETERS_LIST


class ProductionLocationsQueryBuilder(OpenSearchQueryBuilder):
    def __init__(self):
        self.default_query_body = {
            'track_total_hits': True,
            'query': {'bool': {'must': []}},
            'sort': []
        }
        self.query_body = copy.deepcopy(self.default_query_body)
        self.default_fuzziness = 2
        self.default_sort = V1_PARAMETERS_LIST.NAME
        self.default_sort_order = 'asc'
        self.build_options = {
            'country': self._build_country,
            'number_of_workers': self._build_number_of_workers
        }

    def _add_terms(self, field, values):
        if not values:
            return self.query_body

        if field == V1_PARAMETERS_LIST.OS_ID:
            self._build_os_id(values)

        else:
            terms_field = self.build_options.get(
                field, lambda x: f'{x}.keyword'
            )(field)

            self.query_body['query']['bool']['must'].append(
                {'terms': {terms_field: values}}
            )

    def _add_sort(self, field, order_by=None):
        if order_by is None:
            order_by = self.default_sort_order
        self.query_body['sort'].append(
            {f'{field}.keyword': {'order': order_by}}
        )

    def _add_search_after(self, search_after):
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

        self.query_body[V1_PARAMETERS_LIST.SEARCH_AFTER].append(search_after)
