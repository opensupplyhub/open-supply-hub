from rest_framework.exceptions import APIException


class BadRequestException(APIException):
    status_code = 400
    default_detail = 'Bad request'
    default_code = 'bad_request'


class ServiceUnavailableException(APIException):
    status_code = 503
    default_detail = 'Service is temporarily unavailable due to maintenance \
        work. Please try again later.'
    default_code = 'service_unavailable'
