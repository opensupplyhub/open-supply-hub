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
        # Both default sorting and order are needed for add_search_after()
        # Default order is needed for add_sort() and add_search_after()
        self.default_sort = V1_PARAMETERS_LIST.NAME
        self.default_sort_order = 'asc'
        self.build_options = {
            'country': self.__build_country,
            'number_of_workers': self.__build_number_of_workers
        }
        self.date_field = 'claimed_at'

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

    def __init_filter(self):
        if "filter" not in self.query_body["query"]["bool"]:
            self.query_body["query"]["bool"]["filter"] = []

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
        # If there is sorting, then there should be an order.
        if order_by is None:
            order_by = self.default_sort_order

        if field == 'claimed_at':
            self.query_body['sort'].append(
                {f'{field}': {'order': order_by}}
            )
        else:
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

    def add_multi_match(self, query, slop=None):
        fields = [
            f'{V1_PARAMETERS_LIST.NAME}^2',
            V1_PARAMETERS_LIST.ADDRESS,
            V1_PARAMETERS_LIST.DESCRIPTION,
            V1_PARAMETERS_LIST.LOCAL_NAME
        ]

        if slop is not None:
            multi_match_query = {
                'multi_match': {
                    'query': query,
                    'fields': fields,
                    'type': 'phrase',
                    'slop': slop
                }
            }
        else:
            multi_match_query = {
                'multi_match': {
                    'query': query,
                    'fields': fields,
                    'fuzziness': self.default_fuzziness
                }
            }

        self.query_body['query']['bool']['must'].append(multi_match_query)

    def add_aggregations(self, aggregation, geohex_grid_precision=None):
        if aggregation == 'geohex_grid':
            aggregation_config = {
                'field': 'coordinates'
            }

            if geohex_grid_precision:
                aggregation_config['precision'] = geohex_grid_precision

            self.query_body['aggregations'] = {
                'grouped': {
                    'geohex_grid': aggregation_config
                }
            }

        return self.query_body

    def add_geo_bounding_box(self, top, left, bottom, right):
        self.__init_filter()

        self.query_body['query']['bool']['filter'].append({
            'geo_bounding_box': {
                'coordinates': {
                    'top': top,
                    'left': left,
                    'bottom': bottom,
                    'right': right,
                }
            }
        })

    def add_geo_polygon(self, values):
        self.__init_filter()

        geo_polygon = {
            "geo_polygon": {
                "coordinates": {
                    "points": [
                        {
                            "lat": float(lat), "lon": float(lon)
                        } for lat, lon
                        in (
                            point.split(",") for point in values
                        )
                    ]
                }
            }
        }

        self.query_body["query"]["bool"]["filter"].append(geo_polygon)
