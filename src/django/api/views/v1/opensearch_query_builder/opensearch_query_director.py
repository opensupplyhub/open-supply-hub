class OpenSearchQueryDirector:
    def __init__(self, builder):
        self.builder = builder
        self._opensearch_template_fields = {
            'name': 'match',
            'name_local': 'match',
            'description': 'match',
            'address': 'match',
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
            'country': 'terms',
            'coordinates': 'geo_distance',
        }

    def build_query(self, query_params):
        for field, query_type in self._opensearch_template_fields.items():
            if query_type == 'match':
                value = query_params.get(field)
                fuzziness = '2' if field in ['address', 'name'] else None
                if value:
                    self.builder.add_match(field, value, fuzziness=fuzziness)
            elif query_type == 'terms':
                value = query_params.getlist(field)
                if value:
                    self.builder.add_terms(field, value)
            elif query_type == 'range':
                self.builder.add_range(field, query_params)
            elif query_type == 'geo_distance':
                lat = query_params.get(f'{field}[lat]')
                lon = query_params.get(f'{field}[lon]')
                distance = query_params.get('distance', '10km')
                if lat and lon:
                    self.builder.add_geo_distance(field,
                                                  float(lat),
                                                  float(lon),
                                                  distance)

        start_after = query_params.get('start_after')
        if start_after:
            self.builder.add_start_after(start_after.split(','))

        size = query_params.get('size')
        if size:
            self.builder.add_size(size)

        return self.builder.get_query_body()
