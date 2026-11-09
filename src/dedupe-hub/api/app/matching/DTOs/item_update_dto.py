from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class NewFacilityDTO(TypedDict):
    id: str
    name: str
    address: str
    country_code: str
    location: Any
    created_from_id: int


class ItemUpdateDTO(TypedDict):
    """
    The final state of a list item after matching. The matchers only stage
    it; the Writer applies it in the same transaction as the item's match
    rows, so the status a caller polls on never becomes final before the
    matches it describes exist (OSDEV-3149).
    """
    facility_list_item_id: int
    source_id: int
    status: str
    facility_id: Optional[str]
    processing_results: List[Dict[str, Any]]
    # Set only for an unmatched item of a `create` source while dedupe-hub
    # is live: the Facility the Writer creates for it.
    new_facility: Optional[NewFacilityDTO]
