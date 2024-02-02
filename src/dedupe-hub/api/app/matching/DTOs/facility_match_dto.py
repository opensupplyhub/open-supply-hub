from typing import Any, Dict
from typing_extensions import TypedDict


class FacilityMatchDTO(TypedDict):
    facility_id: str
    confidence: int
    facility_list_item_id: str
    status: str
    results: Dict[str, Any]
