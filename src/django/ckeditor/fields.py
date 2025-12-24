from django.db import models


class RichTextField(models.TextField):
    """Minimal stub to satisfy legacy migrations."""

    def __init__(self, *args, **kwargs):
        # Legacy migrations pass config_name; ignore it for compatibility.
        kwargs.pop("config_name", None)
        super().__init__(*args, **kwargs)

