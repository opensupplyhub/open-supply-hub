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
            'country': self.__build_country,
            'number_of_workers': self.__build_number_of_workers
        }

    def __build_country(self, field):
        return f'{field}.alpha_2'

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

    def add_terms(self, field, values):
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

    def add_sort(self, field, order_by=None):
        if order_by is None:
            order_by = self.default_sort_order
        self.query_body['sort'].append(
            {f'{field}.keyword': {'order': order_by}}
        )

    def add_search_after(
        self,
        search_after_value,
        search_after_id,
        id_type='os_id'
    ):
        super().add_search_after(search_after_value, search_after_id, id_type)
