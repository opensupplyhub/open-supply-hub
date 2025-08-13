import hashlib, json
from typing import Optional
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
    if after_id:
        qs = qs.filter(id__gt=after_id)
    items = list(qs.order_by("id")[:page_size])
    last_id = items[-1].id if items else None
    return items, last_id

def advance_blocks_id(
    qs, page_size: int, start_after: Optional[int], steps: int, block: int = 10
) -> Optional[int]:
    after = start_after
    while steps > 0:
        take = min(steps, block)
        batch = list(
            (qs.filter(id__gt=after) if after else qs)
            .order_by("id")[:page_size * take]
        )
        if not batch:
            return None
        after = batch[-1].id
        steps -= take
    return after
