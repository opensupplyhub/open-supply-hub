import copy
from abc import abstractmethod
from api.views.v1.opensearch_query_builder. \
    opensearch_query_builder_interface import OpenSearchQueryBuilderInterface
from api.views.v1.parameters_list import V1_PARAMETERS_LIST


class OpenSearchQueryBuilder(OpenSearchQueryBuilderInterface):
    def reset(self):
        self.query_body = copy.deepcopy(self.default_query_body)

    def _build_number_of_workers(self, field, range_query):
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

    def _build_country(self, field):
        return f'{field}.alpha_2'

    def add_from(self, paginate_from):
        self.query_body['from'] = paginate_from

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
                    V1_PARAMETERS_LIST.LOCAL_NAME
                ],
                'fuzziness': self.default_fuzziness
            }
        })

    @abstractmethod
    def _add_terms(self, field, values):
        pass

    def _build_os_id(self, values):
        # Build a query to search in both os_id and historical_os_id.keyword
        self.query_body['query']['bool']['must'].append(
            {
                'bool': {
                    'should': [
                        {'terms': {'os_id': values}},
                        {'terms': {'historical_os_id.keyword': values}},
                    ]
                }
            }
        )

    @abstractmethod
    def _build_date_range(self, query_params):
        pass

    def add_range(self, field, query_params):
        if field in {
                V1_PARAMETERS_LIST.NUMBER_OF_WORKERS,
                V1_PARAMETERS_LIST.PERCENT_FEMALE_WORKERS
        }:
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

        elif field in {
            V1_PARAMETERS_LIST.DATE_GTE,
            V1_PARAMETERS_LIST.DATE_LT
        }:
            self._build_date_range(query_params)

    def add_geo_distance(self, field, lat, lng, distance):
        geo_distance_query = {
            'geo_distance': {
                'distance': distance,
                field: {'lat': lat, 'lon': lng}
            }
        }
        self.query_body['query']['bool']['must'].append(geo_distance_query)

    @abstractmethod
    def _add_sort(self, field, order_by=None):
        pass

    @abstractmethod
    def _add_search_after(self, search_after):
        pass

    def get_final_query_body(self):
        return self.query_body
