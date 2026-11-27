import json

from rest_framework import renderers


class MvtRenderer(renderers.BaseRenderer):
    media_type = 'application/vnd.mapbox-vector-tile'
    format = 'pbf'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class CSVRenderer(renderers.BaseRenderer):
    """Lets a view that builds its own CSV `HttpResponse` accept
    `Accept: text/csv` (OSDEV-3398: ContriBot asks for the post-review
    list that way). Content negotiation only needs the media type to
    match; the view's `HttpResponse` is returned as built. An error
    (`Response` with a dict) is rendered as JSON so the message stays
    readable to the client."""
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, media_type=None, renderer_context=None):
        if isinstance(data, (str, bytes)):
            return data
        return json.dumps(data)
