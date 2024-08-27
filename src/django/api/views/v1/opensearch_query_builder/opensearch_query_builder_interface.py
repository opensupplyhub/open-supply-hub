from abc import abstractmethod


class OpenSearchQueryBuilderInterface:
    '''
    Interface for query build methods that will be
    used for the OpenSearchQueryBuilder
    '''

    @abstractmethod
    def add_size(self, size):
        pass

    @abstractmethod
    def add_match(self, field, value, fuzziness):
        pass

    @abstractmethod
    def add_multi_match(self, query):
        pass

    @abstractmethod
    def add_terms(self, field, values):
        pass

    @abstractmethod
    def add_range(self, field, min_value, max_value):
        pass

    @abstractmethod
    def add_geo_distance(self, field, lat, lng, distance):
        pass

    @abstractmethod
    def add_sort(self, field, order):
        pass

    @abstractmethod
    def add_search_after(self, search_after):
        pass
