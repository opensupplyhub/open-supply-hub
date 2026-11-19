"""Fetch newly uploaded facility lists and enqueue them for processing.

Reads the resume cursor from DynamoDB, queries
``GET /api/admin-facility-lists/`` for ``PENDING`` lists with ``id__gt`` cursor
pagination, writes each new list as a PENDING row, and returns Map-state items
for Step Functions.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import unquote, urlparse

from lib.lists_repository import ListsRepository
from lib.os_hub_api import FacilityListStatus, OSHubAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# OSDEV-3398: a list stays out of ContriBot until its contributor's
# list-cleaning review window has closed. The window is
# LIST_CLEANING_REVIEW_MINUTES (60) from the end of the parse, so the
# wait is measured from the upload with a margin for the parse itself.
MIN_LIST_AGE_MINUTES_DEFAULT = 90


def min_list_age() -> timedelta:
    raw = os.environ.get("CONTRIBOT_MIN_LIST_AGE_MINUTES", "").strip()
    minutes = int(raw) if raw else MIN_LIST_AGE_MINUTES_DEFAULT
    return timedelta(minutes=max(minutes, 0))


def created_at(facility_list: dict) -> Optional[datetime]:
    """When the list was uploaded, or ``None`` when the API did not say."""
    raw = str(facility_list.get("created_at") or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def handler(event, context):
    """Lambda entry point: enqueue new facility lists and return Map items."""
    repository = ListsRepository()
    last_id = repository.get_last_list_id()
    logger.info("Resuming after list_id=%s", last_id)
    cutoff = datetime.now(timezone.utc) - min_list_age()

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
        uploaded = created_at(facility_list)
        if uploaded is not None and uploaded > cutoff:
            # Lists come in id order, so everything from here on is
            # younger too. Leave them, and the cursor, for a later run.
            logger.info(
                "Stopping before list_id=%s uploaded at %s: younger than %s",
                facility_list.get("id"),
                uploaded.isoformat(),
                min_list_age(),
            )
            break
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

    if max_fetched_id > last_id:
        repository.advance_cursor(max_fetched_id)

    return {"lists": lists}
