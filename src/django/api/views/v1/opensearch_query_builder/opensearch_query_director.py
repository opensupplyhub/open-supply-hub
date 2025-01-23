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
                field,
                float(lat),
                float(lng),
                distance
            )

    def build_query(self, query_params):
        self.__builder.reset()

        for field, query_type in self.__opensearch_template_fields.items():
            if query_type == "match":
                value = query_params.get(field)
                self.__add_match_query(field, value)
                continue

            if query_type == "terms":
                values = query_params.getlist(field)
                self.__add_terms_query(field, values)
                continue

            if query_type == "range":
                self.__add_range_query(field, query_params)
                continue

            if query_type == "geo_distance":
                lat = query_params.get(f"{field}[lat]")
                lng = query_params.get(f"{field}[lng]")
                distance = query_params.get("distance", "10km")
                self.__add_geo_distance_query(field, lat, lng,
                                              distance)

        sort_by = query_params.get(V1_PARAMETERS_LIST.SORT_BY)
        if sort_by:
            order_by = query_params.get(V1_PARAMETERS_LIST.ORDER_BY)
            self.__builder.add_sort(sort_by, order_by)

        search_after_id = query_params. \
            get(V1_PARAMETERS_LIST.SEARCH_AFTER + "[id]")
        search_after_value = query_params. \
            get(V1_PARAMETERS_LIST.SEARCH_AFTER + "[value]")
        if search_after_id and search_after_value:
            self.__builder.add_search_after(
                search_after_value,
                search_after_id
            )

        paginate_from = query_params.get(V1_PARAMETERS_LIST.FROM)
        if paginate_from:
            self.__builder.add_from(paginate_from)

        size = query_params.get(V1_PARAMETERS_LIST.SIZE)
        if size:
            self.__builder.add_size(size)

        self.__builder.add_specific_queries(query_params)

        return self.__builder.get_final_query_body()
