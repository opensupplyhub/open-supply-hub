class OpenSearchQueryDirector:
    def __init__(self, builder):
        self.__builder = builder
        self.__opensearch_template_fields = {
            'description': 'match',
            'address': 'match',
            'name': 'terms',
            'name_local': 'terms',
            'country': 'terms',
            'sector': 'terms',
            'product_type': 'terms',
            'processing_type': 'terms',
            'location_type': 'terms',
            'number_of_workers': 'range',
            'minimum_order_quantity': 'terms',
            'average_lead_time': 'terms',
            'percent_female_workers': 'range',
            'affiliations': 'terms',
            'certifications_standards_regulations': 'terms',
            'coordinates': 'geo_distance',
        }

    def __add_match_query(self, field, value):
        if value:
            self.__builder.add_match(field, value, fuzziness='2')

    def __add_terms_query(self, field, values):
        self.__builder.add_terms(field, values)

    def __add_range_query(self, field, query_params):
        self.__builder.add_range(field, query_params)

    def __add_geo_distance_query(self, field, lat, lon, distance):
        if lat and lon:
            self.__builder.add_geo_distance(
                field,
                float(lat),
                float(lon),
                distance
            )

    def build_query(self, query_params):
        self.__builder.reset()

        for field, query_type in self.__opensearch_template_fields.items():
            if query_type == 'match':
                value = query_params.get(field)
                self.__add_match_query(field, value)
            elif query_type == 'terms':
                values = query_params.getlist(field)
                self.__add_terms_query(field, values)
            elif query_type == 'range':
                self.__add_range_query(field, query_params)
            elif query_type == 'geo_distance':
                lat = query_params.get(f'{field}[lat]')
                lon = query_params.get(f'{field}[lon]')
                distance = query_params.get('distance', '10km')
                self.__add_geo_distance_query(field, lat, lon, distance)

        sort_by = query_params.get('sort_by')
        if sort_by:
            order_by = query_params.get('order_by')
            self.__builder.add_sort(sort_by, order_by)

        search_after = query_params.get('search_after')
        if search_after:
            self.__builder.add_search_after(search_after)

        size = query_params.get('size')
        if size:
            self.__builder.add_size(size)

        multi_match_query = query_params.get('query')
        if multi_match_query:
            self.__builder.add_multi_match(multi_match_query)

        return self.__builder.get_final_query_body()
