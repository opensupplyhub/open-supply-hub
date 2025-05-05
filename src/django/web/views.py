import os

from django.conf import settings
from django.shortcuts import render

from api.models import Facility


def environment(request):
    """
    A JavaScript snippet that initializes the environment
    """
    # Capture all REACT_APP_ variables into a dictionary for context
    environment = {
        k: v
        for k, v in os.environ.items()
        if k.startswith('REACT_APP_')
    }

    # Add Environment variable, lowered for easier comparison
    # One of `development`, `test`, `preprod`, `rba`,
    # `local`, `staging`, `production`
    environment['ENVIRONMENT'] = settings.ENVIRONMENT.lower()

    environment['OAR_CLIENT_KEY'] = settings.OAR_CLIENT_KEY

    environment['TILE_CACHE_KEY'] = Facility.current_tile_cache_key()

    context = {'environment': environment}

    return render(request, 'web/environment.js', context,
                  content_type='application/javascript; charset=utf-8')
