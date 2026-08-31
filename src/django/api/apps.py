# OSDEV-2644 path-filter smoke test. Do not merge.
from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from api import signals  # noqa: F401
