def is_health_check_request(request):
    """
    True for the app liveness path under /health-check/.

    Probes must not depend on middleware that talks to database or external
    services.
    """
    path = request.path
    return path == '/health-check/' or path.startswith('/health-check/')
