from django.apps import AppConfig
from django.db.models.options import Options


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        names = getattr(Options, 'DEFAULT_NAMES', None)
        if names is None:
            names = getattr(Options, 'default_names', ())
        if 'index_together' not in names:
            new_names = tuple(names) + ('index_together',)
            if hasattr(Options, 'DEFAULT_NAMES'):
                Options.DEFAULT_NAMES = new_names
            else:
                Options.default_names = new_names
        # Implicitly connect signal handlers decorated with @receiver.
        from api import signals  # noqa: F401
