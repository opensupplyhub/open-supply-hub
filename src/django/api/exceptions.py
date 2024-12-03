from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request'
    default_code = 'bad_request'


class GoneException(APIException):
    status_code = status.HTTP_410_GONE
    default_detail = "The resource is no longer available."
    default_code = "gone"


class InternalServerErrorException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = (
        "An unexpected error occurred while processing the request."
    )
    default_code = "internal_server_error"


class ServiceUnavailableException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = ('Service is temporarily unavailable due to maintenance'
                      'work. Please try again later.')
    default_code = 'service_unavailable'
