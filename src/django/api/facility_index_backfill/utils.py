"""Shared helpers for facility index backfill workers."""

from typing import Optional

from django.conf import settings

# Each worker is a subprocess (~150-200 MB RSS), so size parallelism to the
# CLI task memory when wiring a temporary backfill into post_deployment.
BACKFILL_PARALLEL_BY_ENVIRONMENT = {
    'Local': 2,
    'Development': 1,
    'Test': 10,
    'Staging': 10,
    'Preprod': 10,
    'Production': 10,
    'Rba': 10,
}

# Fallback when settings.ENVIRONMENT is not in the map
# (e.g. a new deploy target).
BACKFILL_PARALLEL_DEFAULT = 2


def backfill_parallel_worker_count() -> int:
    """Return post-deploy backfill parallelism for the current environment."""
    return BACKFILL_PARALLEL_BY_ENVIRONMENT.get(
        settings.ENVIRONMENT,
        BACKFILL_PARALLEL_DEFAULT,
    )


def format_worker_number(
    worker_id: int,
    workers: Optional[int] = None,
) -> str:
    """Return a 1-based worker label for logs."""
    number = worker_id + 1
    if workers is not None:
        return f'{number}/{workers}'
    return str(number)
