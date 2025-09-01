import hashlib
import json
from typing import Optional, Callable
from math import ceil
from django.core.cache import cache
from api.constants import PaginationConfig


def create_query_hash(request, page_size: int) -> str:
    parts = {
        "qp": sorted(request.query_params.items()),
        "uid": getattr(request.user, "id", None),
        "ps": page_size,
    }
    return hashlib.sha1(json.dumps(parts, sort_keys=True).encode()).hexdigest()


def _get_bookmark_key(hash: str, page: int) -> str:
    return f"dl:{hash}:p:{page}"


def get_page_bookmark(hash: str, page: int) -> Optional[int]:
    return cache.get(_get_bookmark_key(hash, page))


def set_page_bookmark(
    hash: str,
    page: int,
    last_id: Optional[int],
    ttl: int = PaginationConfig.CACHE_TTL_SECONDS
) -> None:
    if last_id is not None:
        cache.set(_get_bookmark_key(hash, page), last_id, ttl)


def get_paginated_items_after_id(
    qs,
    page_size: int,
    after_id: Optional[int]
):
    query = qs.filter(id__gt=after_id) if after_id else qs
    batch = list(query.order_by("id")[: page_size + 1])

    items = batch[:page_size]
    last_id = items[-1].id if items else None

    has_next = len(batch) > page_size
    is_last_page = not has_next

    return items, last_id, is_last_page


def move_to_next_block_id(
    qs,
    page_size: int,
    start_after: Optional[int],
    steps: int,
    block: int,
    densify: Optional[Callable[[int, int], None]] = None,
    start_from_page: Optional[int] = None,
) -> Optional[int]:

    after = start_after
    current_page = start_from_page or 0

    while steps > 0:
        take = min(steps, block)
        ids = list(
            (qs.filter(id__gt=after) if after else qs)
            .order_by("id")
            .values_list("id", flat=True)[: page_size * take]
        )
        if not ids:
            return None

        pages_in_batch = ceil(len(ids) / page_size)

        if densify is not None and start_from_page is not None:
            for i in range(pages_in_batch):
                idx = min((i + 1) * page_size - 1, len(ids) - 1)
                current_page += 1
                densify(current_page, ids[idx])

        after = ids[-1]
        steps -= pages_in_batch

    return after
