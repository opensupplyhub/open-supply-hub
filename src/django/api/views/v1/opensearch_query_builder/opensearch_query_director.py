from api.views.v1.parameters_list import V1_PARAMETERS_LIST


class OpenSearchQueryDirector:
    def __init__(self, builder):
        self.__builder = builder
        self.__opensearch_template_fields = {
            V1_PARAMETERS_LIST.DESCRIPTION: 'match',
            V1_PARAMETERS_LIST.ADDRESS: 'match',
            V1_PARAMETERS_LIST.NAME: 'match',
            V1_PARAMETERS_LIST.OS_ID: 'terms',
            V1_PARAMETERS_LIST.LOCAL_NAME: 'match',
            V1_PARAMETERS_LIST.COUNTRY: 'terms',
            V1_PARAMETERS_LIST.SECTOR: 'terms',
            V1_PARAMETERS_LIST.PRODUCT_TYPE: 'terms',
            V1_PARAMETERS_LIST.PROCESSING_TYPE: 'terms',
            V1_PARAMETERS_LIST.LOCATION_TYPE: 'terms',
            V1_PARAMETERS_LIST.NUMBER_OF_WORKERS: 'range',
            V1_PARAMETERS_LIST.MINIMUM_ORDER_QUANTITY: 'terms',
            V1_PARAMETERS_LIST.AVERAGE_LEAD_TIME: 'terms',
            V1_PARAMETERS_LIST.PERCENT_FEMALE_WORKERS: 'range',
            V1_PARAMETERS_LIST.AFFILIATIONS: 'terms',
            V1_PARAMETERS_LIST.CERTIFICATIONS_STANDARDS_REGULATIONS: 'terms',
            V1_PARAMETERS_LIST.COORDINATES: 'geo_distance',
            V1_PARAMETERS_LIST.CONTRIBUTOR_ID: 'terms',
            V1_PARAMETERS_LIST.REQUEST_TYPE: 'terms',
            V1_PARAMETERS_LIST.SOURCE: 'terms',
            V1_PARAMETERS_LIST.STATUS: 'terms',
            V1_PARAMETERS_LIST.MODERATION_ID: 'terms',
            V1_PARAMETERS_LIST.DATE_GTE: 'range',
            V1_PARAMETERS_LIST.DATE_LT: 'range',
        }

    def build_query(self, query_params):
        self.__builder.reset()

        self.__process_template_fields(query_params)
        self.__process_sorting(query_params)
        self.__process_search_after(query_params)
        self.__process_pagination(query_params)
        self.__process_size(query_params)
        self.__process_multi_match(query_params)
        self.__process_aggregation(query_params)
        self.__process_filter(query_params)

        return self.__builder.get_final_query_body()

    def __process_template_fields(self, query_params):
        for field, query_type in self.__opensearch_template_fields.items():
            self.__process_query_field(field, query_type, query_params)

    def __process_query_field(self, field, query_type, query_params):
        if query_type == "match":
            value = query_params.get(field)
            self.__add_match_query(field, value)
            return

        if query_type == "terms":
            values = query_params.getlist(field)
            self.__add_terms_query(field, values)
            return

        if query_type == "range":
            self.__add_range_query(field, query_params)
            return

        if query_type == "geo_distance":
            lat = query_params.get(f"{field}[lat]")
            lng = query_params.get(f"{field}[lng]")
            distance = query_params.get("distance", "10km")
            self.__add_geo_distance_query(field, lat, lng, distance)

    def __add_match_query(self, field, value):
        if value:
            self.__builder.add_match(field, value, fuzziness='2')

    def __add_terms_query(self, field, values):
        self.__builder.add_terms(field, values)

    def __add_range_query(self, field, query_params):
        self.__builder.add_range(field, query_params)

    def __add_geo_distance_query(self, field, lat, lng, distance):
        if lat and lng:
            self.__builder.add_geo_distance(
                field, float(lat), float(lng), distance
            )

    def __process_sorting(self, query_params):
        sort_by = query_params.get(V1_PARAMETERS_LIST.SORT_BY)

        if sort_by:
            order_by = query_params.get(V1_PARAMETERS_LIST.ORDER_BY)
            self.__builder.add_sort(sort_by, order_by)

    def __process_search_after(self, query_params):
        search_after_id = query_params.get(
            V1_PARAMETERS_LIST.SEARCH_AFTER + "[id]"
        )
        search_after_value = query_params.get(
            V1_PARAMETERS_LIST.SEARCH_AFTER + "[value]"
        )

        if search_after_id and search_after_value:
            self.__builder.add_search_after(
                search_after_value, search_after_id
            )

    def __process_pagination(self, query_params):
        paginate_from = query_params.get(V1_PARAMETERS_LIST.FROM)

        if paginate_from:
            self.__builder.add_from(paginate_from)

    def __process_size(self, query_params):
        size = query_params.get(V1_PARAMETERS_LIST.SIZE)

        if size:
            self.__builder.add_size(size)

    def __process_multi_match(self, query_params):
        multi_match_query = query_params.get(V1_PARAMETERS_LIST.QUERY)

        if multi_match_query and hasattr(self.__builder, 'add_multi_match'):
            self.__builder.add_multi_match(multi_match_query)

    def __process_aggregation(self, query_params):
        aggregation = query_params.get(V1_PARAMETERS_LIST.AGGREGATION)
        geohex_grid_precision = query_params.get(
            V1_PARAMETERS_LIST.GEOHEX_GRID_PRECISION
        )

        if aggregation and hasattr(self.__builder, 'add_aggregations'):
            self.__builder.add_aggregations(aggregation, geohex_grid_precision)

    def __process_filter(self, query_params):
        top = query_params.get(
            V1_PARAMETERS_LIST.GEO_BOUNDING_BOX + '[top]'
        )
        left = query_params.get(
            V1_PARAMETERS_LIST.GEO_BOUNDING_BOX + '[left]'
        )
        bottom = query_params.get(
            V1_PARAMETERS_LIST.GEO_BOUNDING_BOX + '[bottom]'
        )
        right = query_params.get(
            V1_PARAMETERS_LIST.GEO_BOUNDING_BOX + '[right]'
        )

        if top and left and bottom and right and hasattr(
            self.__builder, 'add_geo_bounding_box'
        ):
            self.__builder.add_geo_bounding_box(
                float(top), float(left), float(bottom), float(right)
            )
