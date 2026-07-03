"""Shared helpers for facility index backfill workers."""

from typing import Optional


def format_worker_number(
    worker_id: int,
    workers: Optional[int] = None,
) -> str:
    """Return a 1-based worker label for logs."""
    number = worker_id + 1
    if workers is not None:
        return f'{number}/{workers}'
    return str(number)
