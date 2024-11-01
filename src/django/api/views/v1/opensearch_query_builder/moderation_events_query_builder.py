import copy
from api.views.v1.opensearch_query_builder. \
    opensearch_query_builder import OpenSearchQueryBuilder


class ModerationEventsQueryBuilder(OpenSearchQueryBuilder):
    def __init__(self):
        self.default_query_body = {
            'track_total_hits': 'true',
            'size': 10,
            'query': {'bool': {'must': []}},
            'sort': []
        }
        self.query_body = copy.deepcopy(self.default_query_body)
        self.default_sort = ''
        self.default_sort_order = 'asc'
        self.build_options = {
            'country': self._build_country,
        }

    def _build_country(self, field):
        return f'{field}.cleaned_data.country.alpha_2'
