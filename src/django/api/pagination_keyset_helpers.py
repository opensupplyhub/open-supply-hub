import hashlib, json
from typing import Optional, Callable
from math import ceil
from django.core.cache import cache

def qhash(request, page_size: int) -> str:
    parts = {
        "qp": sorted(request.query_params.items()),
        "uid": getattr(request.user, "id", None),
        "ps": page_size,
    }
    return hashlib.sha1(json.dumps(parts, sort_keys=True).encode()).hexdigest()

def _bm_key(h: str, page: int) -> str:
    return f"dl:{h}:p:{page}"

def get_bm(h: str, page: int) -> Optional[int]:
    return cache.get(_bm_key(h, page))

def set_bm(h: str, page: int, last_id: Optional[int], ttl: int = 1800) -> None:
    if last_id is not None:
        cache.set(_bm_key(h, page), last_id, ttl)

def keyset_page_id(qs, page_size: int, after_id: Optional[int]):
    q = qs.filter(id__gt=after_id) if after_id else qs
    batch = list(q.order_by("id")[: page_size + 1])

    items = batch[:page_size]
    last_id = items[-1].id if items else None

    has_next = len(batch) > page_size
    is_last_page = not has_next

    return items, last_id, is_last_page

def advance_blocks_id(
    qs,
    page_size: int,
    start_after: Optional[int],
    steps: int,
    block: int = 10,
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
