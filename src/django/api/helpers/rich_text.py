import html

import bleach
from django.utils.html import strip_tags
from django_bleach.utils import get_bleach_default_options

# CKEditor serializes a visually empty document in several ways
# (`<p>&nbsp;</p>`, `<p><br></p>`, formatted but blank runs). Treat all of
# them as no content so an empty editor never renders an empty element.
NON_BREAKING_SPACE = '\xa0'
ZERO_WIDTH_SPACE = '\u200b'


def clean_rich_text(value):
    '''
    Sanitize admin-authored CKEditor HTML against the Bleach allowlist and
    collapse a visually empty document to an empty string.
    '''
    if not value:
        return ''

    cleaned = bleach.clean(value, **get_bleach_default_options()).strip()

    # Entities survive bleach.clean in encoded form, so decode before
    # deciding whether anything visible is left.
    visible_text = html.unescape(strip_tags(cleaned)).replace(
        NON_BREAKING_SPACE, ' '
    ).replace(ZERO_WIDTH_SPACE, '').strip()

    return cleaned if visible_text else ''
