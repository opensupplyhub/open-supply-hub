from abc import abstractmethod


class SearchInterface:
    '''
    Interface for search methods that will be used for the OpenSearch
    '''

    @abstractmethod
    def search_production_locations(self, query_body):
        pass
