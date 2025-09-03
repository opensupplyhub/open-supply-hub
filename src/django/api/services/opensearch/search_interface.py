from abc import abstractmethod


class SearchInterface:
    '''
    Interface for search methods that will be used for the OpenSearch
    '''

    @abstractmethod
    def search_index(self, index_name, query_body, params=None):
        pass
