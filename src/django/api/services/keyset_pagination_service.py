from api.pagination_keyset_helpers import (
    create_query_hash,
    get_page_bookmark,
    set_page_bookmark,
    get_paginated_items_after_id,
    move_to_next_block_id
)


class KeysetPaginationService:

    def __init__(self, base_qs, block: int):
        self.base_qs = base_qs
        self.block = block

    def get_page_cursor(
        self,
        request,
        page: int,
        page_size: int,
    ):
        if page == 1:
            return None

        qh = create_query_hash(request, page_size)
        prev_last_id = get_page_bookmark(qh, page - 1)
        if prev_last_id is not None:
            return prev_last_id

        start_after, steps, nearest = self.find_nearest_cached_page(
            qh,
            page - 1,
            page_size
        )

        if steps > 0 and start_after is not None:
            start_after = move_to_next_block_id(
                self.base_qs,
                page_size,
                start_after,
                steps,
                block=self.block,
                densify=lambda p, lid: set_page_bookmark(qh, p, lid),
                start_from_page=nearest,
            )

        return start_after

    def find_nearest_cached_page(
        self,
        query_hash: str,
        target_page: int,
        page_size: int,
    ):
        nearest = target_page
        while nearest > 1 and get_page_bookmark(query_hash, nearest) is None:
            nearest -= 1

        start_after = get_page_bookmark(query_hash, nearest) if nearest > 1 else None
        steps = target_page - (nearest if nearest > 1 else 0)

        if start_after is None and nearest == 1:
            _, first_last, _ = get_paginated_items_after_id(
                self.base_qs,
                page_size, None
            )
            set_page_bookmark(query_hash, 1, first_last)
            start_after, steps = first_last, steps - 1
            nearest = 1
        
        return start_after, steps, nearest
