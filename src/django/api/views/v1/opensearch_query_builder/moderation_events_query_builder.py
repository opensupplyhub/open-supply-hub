import copy
from api.views.v1.opensearch_query_builder. \
    opensearch_query_builder import OpenSearchQueryBuilder
from api.views.v1.parameters_list import V1_PARAMETERS_LIST


class ModerationEventsQueryBuilder(OpenSearchQueryBuilder):
    def __init__(self):
        self.default_query_body = {
            'track_total_hits': 'true',
            'query': {'bool': {'must': []}},
            'sort': []
        }
        self.query_body = copy.deepcopy(self.default_query_body)
        self.default_sort = 'created_at'
        self.default_sort_order = 'desc'
        self.build_options = {
            'country': self._build_country,
        }

    def _build_country(self, field):
        return f'cleaned_data.{field}.alpha_2'

    def _build_date_range(self, query_params):
        date_start = query_params.get('date_gte')
        date_end = query_params.get('date_lt')
        range_query = {}

        if date_start is not None:
            range_query['gte'] = date_start
        if date_end is not None:
            range_query['lte'] = date_end

        if range_query:
            existing_range = any(
                query.get('range', {}).get('created_at')
                for query in self.query_body['query']['bool']['must']
            )
            if not existing_range:
                self.query_body['query']['bool']['must'].append({
                    'range': {'created_at': range_query}
                })

    def _add_terms(self, field, values):
        if not values:
            return self.query_body

        if field == V1_PARAMETERS_LIST.OS_ID:
            self._build_os_id(values)
            return
        
        if field == V1_PARAMETERS_LIST.MODERATION_ID:
            self._build_moderation_id(values)
            return

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
            {field: {'order': order_by}}
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
                self.default_sort: {
                    'order': self.default_sort_order
                }
            }
            self.query_body['sort'].append(sort_criteria)

        self.query_body[V1_PARAMETERS_LIST.SEARCH_AFTER].append(search_after)
