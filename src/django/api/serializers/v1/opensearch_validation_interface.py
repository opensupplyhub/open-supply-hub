from abc import ABC, abstractmethod
from rest_framework import serializers


class OpenSearchValidationInterface(ABC):
    '''
    Interface for validation methods that will be
    used for requests to the OpenSearch
    '''

    def validate(self, data):
        errors = self.validate_opensearch_params(data)
        if errors:
            raise serializers.ValidationError({
                "message": "The request query is invalid.",
                "errors": errors
            })

    @abstractmethod
    def validate_opensearch_params(self, data):
        pass
