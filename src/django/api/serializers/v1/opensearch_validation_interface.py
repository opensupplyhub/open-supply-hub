from abc import ABC, abstractmethod


class OpenSearchValidationInterface(ABC):
    '''
    Interface for validation methods that will be
    used for requests to the OpenSearch
    '''

    def validate(self, data):
        return self.validate_opensearch_params(data)

    @abstractmethod
    def validate_opensearch_params(self, data):
        pass
