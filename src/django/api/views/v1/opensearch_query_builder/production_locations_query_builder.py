import copy
from api.views.v1.opensearch_query_builder. \
    opensearch_query_builder_interface import OpenSearchQueryBuilderInterface
from api.views.v1.parameters_list import V1_PARAMETERS_LIST

# TODO: Inherit OpenSearchQueryBuilder
class ProductionLocationsQueryBuilder(OpenSearchQueryBuilderInterface):
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

    def get_final_query_body(self):
        return self.query_body
