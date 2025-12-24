from django.forms import Textarea


class CKEditorWidget(Textarea):
    """Minimal stub to satisfy any legacy imports."""

    def __init__(self, *args, **kwargs):
        # Ignore legacy config_name argument if provided.
        kwargs.pop("config_name", None)
        super().__init__(*args, **kwargs)
