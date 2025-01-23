import copy
from abc import ABC, abstractmethod
from api.views.v1.parameters_list import V1_PARAMETERS_LIST


class OpenSearchQueryBuilder(ABC):
    def reset(self):
        self.query_body = copy.deepcopy(self.default_query_body)

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
            self.__build_date_range(query_params)

    def __build_date_range(self, query_params):
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

    def add_geo_distance(self, field, lat, lng, distance):
        geo_distance_query = {
            'geo_distance': {
                'distance': distance,
                field: {'lat': lat, 'lon': lng}
            }
        }
        self.query_body['query']['bool']['must'].append(geo_distance_query)

    def __ensure_sort_criteria(self, id_type, current_sorting):
        '''
        Ensure proper sort criteria exists with id_type
        for consistent pagination.
        '''
        if not self.query_body.get('sort'):
            self.query_body['sort'] = [
                {self.default_sort: self.default_sort_order},
                {id_type: self.default_sort_order}
            ]
            return

        if not any(
            id_type in criterion for criterion in self.query_body['sort']
        ):
            self.query_body['sort'].append({id_type: current_sorting})

    def add_search_after(self, search_after_value, search_after_id, id_type):
        '''
        Add search_after pagination with proper sort criteria.

        Args:
            search_after_value: The value to search after
            for the primary sort field.
            search_after_id: The ID to search after for
            consistent pagination.
            id_type: The type of ID field to
            use in sort criteria.
        '''
        current_sorting = self.default_sort_order
        for sort_item in self.query_body.get('sort', []):
            for key, value in sort_item.items():
                if isinstance(value, dict) and 'order' in value:
                    current_sorting = value['order']
                    break
                elif key == 'order':
                    current_sorting = value
                    break

        # search_after can't be present as empty by default in query_body
        if 'search_after' not in self.query_body:
            self.query_body['search_after'] = []

        self.__ensure_sort_criteria(id_type, current_sorting)

        '''
        Order of search_after_value and
        search_after_id should be the same
        as for the sort field
        '''
        self.query_body[V1_PARAMETERS_LIST.SEARCH_AFTER] = [
            search_after_value,
            search_after_id
        ]

    def get_final_query_body(self):
        return self.query_body

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
    def add_sort(self, field, order_by=None):
        pass

    @abstractmethod
    def add_terms(self, field, values):
        pass

    @abstractmethod
    def add_specific_queries(self, query_params):
        pass
