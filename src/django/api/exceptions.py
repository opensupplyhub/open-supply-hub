from rest_framework.exceptions import APIException
from rest_framework import status
from api.constants import ErrorMessages


class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request'
    default_code = 'bad_request'


class ServiceUnavailableException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = ErrorMessages.MAINTENANCE_MODE
    default_code = 'service_unavailable'
