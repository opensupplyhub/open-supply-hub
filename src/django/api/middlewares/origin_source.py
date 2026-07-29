from django.conf import settings
from django.db import connection

from api.middlewares.utils import is_health_check_request


class OriginSourceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.default_origin_source = getattr(
            settings,
            'INSTANCE_SOURCE',
            'os_hub'
        )

    def __call__(self, request):
        # Skip the session-scoped SET so synthetic/ALB/ECS probes stay
        # independent of database availability.
        if not is_health_check_request(request):
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET app.origin_source TO %s",
                    [self.default_origin_source]
                )

        response = self.get_response(request)
        return response
