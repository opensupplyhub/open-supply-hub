import copy
import uuid

from django.conf import settings
from django.test import override_settings


def isolated_download_session_cache():
    """
    Download sessions and their reuse index live in memcached, which
    outlives a test run. Give each test class its own key prefix so
    sessions left by earlier runs (where user ids repeat) can't be reused.
    """
    caches = copy.deepcopy(settings.CACHES)
    caches['facility_downloads']['KEY_PREFIX'] = (
        f'facility_downloads_test_{uuid.uuid4().hex}'
    )
    return override_settings(CACHES=caches)
