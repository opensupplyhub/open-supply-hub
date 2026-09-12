"""Fetch newly uploaded facility lists and enqueue them for processing.

Reads the resume cursor from DynamoDB, queries
``GET /api/admin-facility-lists/`` for ``PENDING`` lists with ``id__gt`` cursor
pagination, writes each new list as a PENDING row, and returns Map-state items
for Step Functions.
"""

from __future__ import annotations

import logging
from urllib.parse import unquote, urlparse

from lib.lists_repository import ListsRepository
from lib.os_hub_api import FacilityListStatus, OSHubAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """Lambda entry point: enqueue new facility lists and return Map items."""
    repository = ListsRepository()
    last_id = repository.get_last_list_id()
    logger.info("Resuming after list_id=%s", last_id)

    api = OSHubAPI()
    facility_lists = api.fetch_lists(
        params={
            "id__gt": last_id,
            "ordering": "id",
            "status": FacilityListStatus.PENDING.value,
        },
    )
    logger.info("Fetched %s list(s) after id__gt=%s", len(facility_lists), last_id)

    lists: list[dict[str, str]] = []
    max_fetched_id = last_id

    for facility_list in facility_lists:
        file_url = (facility_list.get("file") or "").strip()
        file_name = (
            unquote(urlparse(file_url).path.lstrip("/"))
            if file_url
            else ""
        )
        inserted = repository.put_list(
            facility_list["id"],
            list_name=facility_list.get("name") or "",
            contributor_id=facility_list.get("contributor_id"),
            contributor_name=facility_list.get("contributor_name") or "",
            contributor_email=facility_list.get("contributor_email") or "",
            file_name=file_name,
        )
        list_id = int(facility_list["id"])
        max_fetched_id = max(max_fetched_id, list_id)
        if inserted:
            lists.append({"list_id": str(list_id)})

    if facility_lists:
        repository.advance_cursor(max_fetched_id)

    return {"lists": lists}
