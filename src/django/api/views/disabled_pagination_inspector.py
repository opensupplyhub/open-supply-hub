from drf_yasg.inspectors import PaginatorInspector


class DisabledPaginationInspector(PaginatorInspector):
    def get_paginator_parameters(self, _):
        return []

    def get_paginated_response(self, _, response_schema):
        return response_schema
