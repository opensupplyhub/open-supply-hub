from typing import Any, Dict, List, Optional

from app.utils.constants import ProcessingAction
from app.database.models.facility_list_item_temp import FacilityListItemTemp
from app.database.models.facility_match_temp import FacilityMatchTemp
from app.matching.DTOs.facility_match_dto import FacilityMatchDTO
from app.matching.DTOs.item_update_dto import ItemUpdateDTO
from app.matching.DTOs.results_dto import ResultsDTO
from app.database.sqlalchemy import get_session

facility_match_data = Dict[str, str or int or Any]


class BaseItemMatch:
    item: FacilityListItemTemp
    matches: Dict[str, Any]
    automatic_threshold: float
    started: str
    finished: str
    results: ResultsDTO
    pending_item_update: Optional[ItemUpdateDTO]

    def __init__(
        self,
        item_id,
        matches,
        started,
        finished,
        results,
        automatic_threshold
    ):
        with get_session() as session:
            self.item = session.query(FacilityListItemTemp).get(item_id)
        self.matches = matches
        self.started = started
        self.finished = finished
        self.results = results
        self.automatic_threshold= automatic_threshold
        self.pending_item_update = None

    def process(self) -> List[FacilityMatchDTO]:
        pass

    def make_match_object(
        self,
        facility_id: str,
        confidence: int = 1,
        status: str = FacilityMatchTemp.PENDING,
        **kwargs
    ):
        return {
            "facility_list_item_id": self.item.id,
            "facility_id": facility_id,
            "confidence": confidence,
            "status": status,
            "results": kwargs
        }
    
    def stage_item_update(self, **kwargs) -> None:
        """
        Record the item's final status and processing results without
        writing them. The Writer applies the staged update together with
        the item's match rows in one transaction: committing the status
        here, before the matches were written, let a caller polling on the
        status read a partial set of matches (OSDEV-3149).
        """
        json_data = {
            'action': ProcessingAction.MATCH,
            'error': False,
            'started_at': self.started,
            'finished_at': self.finished,
            **kwargs,
        }

        processing_results_data = list(self.item.processing_results or [])
        processing_results_data.append(json_data)

        self.pending_item_update = {
            'facility_list_item_id': self.item.id,
            'source_id': self.item.source_id,
            'status': self.item.status,
            'facility_id': self.item.facility_id,
            'processing_results': processing_results_data,
            'new_facility': None,
        }
