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
        # Both default sorting and order are needed for add_search_after()
        # Default order is needed for add_sort() and add_search_after()
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
        # If there is sorting, then there should be an order.
        if order_by is None:
            order_by = self.default_sort_order
        if (
            field == V1_PARAMETERS_LIST.NAME
            or field == V1_PARAMETERS_LIST.ADDRESS
        ):
            self.query_body['sort'].append({
                'cleaned_data.' + field: {'order': order_by}
            })
        elif field == V1_PARAMETERS_LIST.COUNTRY:
            self.query_body['sort'].append(
                {
                    'cleaned_data.' +
                    field +
                    '.name': {'order': order_by}
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

    def add_search_after(
        self,
        search_after_value,
        search_after_id,
        id_type='moderation_id'
    ):
        super().add_search_after(search_after_value, search_after_id, id_type)

    def add_specific_queries(self, query_params):
        pass
