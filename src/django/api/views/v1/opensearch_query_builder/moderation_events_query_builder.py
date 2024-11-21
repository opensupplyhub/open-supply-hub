import copy
from api.views.v1.opensearch_query_builder. \
    opensearch_query_builder import OpenSearchQueryBuilder
from api.views.v1.parameters_list import V1_PARAMETERS_LIST


class ModerationEventsQueryBuilder(OpenSearchQueryBuilder):
    def __init__(self):
        self.default_query_body = {
            'track_total_hits': True,
            'query': {'bool': {'must': []}},
            'sort': []
        }
        self.query_body = copy.deepcopy(self.default_query_body)
        self.default_sort = 'created_at'
        self.default_sort_order = 'desc'
        self.build_options = {
            'country': self.__build_country,
        }

    def __build_country(self, field):
        return f'cleaned_data.{field}.alpha_2'

    def add_terms(self, field, values):
        if not values:
            return self.query_body

        if field == V1_PARAMETERS_LIST.OS_ID:
            self._build_os_id(values)

        else:
            terms_field = self.build_options.get(
                field, lambda x: x
            )(field)

            self.query_body['query']['bool']['must'].append(
                {'terms': {terms_field: values}}
            )

    def add_sort(self, field, order_by=None):
        if order_by is None:
            order_by = self.default_sort_order
        if (
            field == V1_PARAMETERS_LIST.CLEANED_NAME
            or field == V1_PARAMETERS_LIST.CLEANED_ADDRESS
        ):
            self.query_body['sort'].append({
                'cleaned_data.' + field[len('cleaned_'):]: {'order': order_by}
            })
        elif field == V1_PARAMETERS_LIST.CLEANED_COUNTRY:
            self.query_body['sort'].append(
                {
                    'cleaned_data.' +
                    field[len('cleaned_'):] +
                    '.alpha_2': {'order': order_by}
                }
            )
        else:
            self.query_body['sort'].append(
                {
                    field: {
                        'order': order_by
                    }
                }
            )

    def add_search_after(self, search_after):
        # search_after can't be present as empty by default in query_body
        if V1_PARAMETERS_LIST.SEARCH_AFTER not in self.query_body:
            self.query_body[V1_PARAMETERS_LIST.SEARCH_AFTER] = []

        if not self.query_body.get('sort'):
            self.query_body['sort'] = [
                { self.default_sort: self.default_sort_order },
                { "moderation_id": self.default_sort_order }
            ]
        else:
            if not any("moderation_id" in criterion for criterion in self.query_body['sort']):
                self.query_body['sort'].append({ "moderation_id": self.default_sort_order })

        if isinstance(search_after, str) and ',' in search_after:
            search_after = search_after.split(',')

        self.query_body[V1_PARAMETERS_LIST.SEARCH_AFTER] = search_after

