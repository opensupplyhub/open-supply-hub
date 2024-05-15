from typing import Any, Dict, List

from app.utils.constants import ProcessingAction
from app.database.models.facility_list_item import FacilityListItem
from app.database.models.facility_list_item_temp import FacilityListItemTemp
from app.database.models.source import Source
from app.database.models.facility_match_temp import FacilityMatchTemp
from app.matching.DTOs.facility_match_dto import FacilityMatchDTO
from app.matching.DTOs.results_dto import ResultsDTO
from app.database.sqlalchemy import get_session
from app.config import settings

facility_match_data = Dict[str, str or int or Any]


class BaseItemMatch:
    item: FacilityListItemTemp
    matches: Dict[str, Any]
    automatic_threshold: float
    started: str
    finished: str
    results: ResultsDTO

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

    def item_save(self, **kwargs):
        json_data = {
            'action': ProcessingAction.MATCH,
            'error': False,
            'started_at': self.started,
            'finished_at': self.finished,
            **kwargs,
        }

        processing_results_data = self.item.processing_results
        processing_results_data.append(json_data)
        with get_session() as session:
            facility_list_item = session.query(FacilityListItemTemp).filter(FacilityListItemTemp.id==self.item.id).one()
            facility_list_item.status = self.item.status
            # Update the JSON column data
            session.query(FacilityListItemTemp).\
                filter(FacilityListItemTemp.id == facility_list_item.id).update({"processing_results": processing_results_data})
            facility_list_item.facility_id = self.item.facility_id
            facility_list_item.version = settings.dedupe_hub_version
            session.commit()

        session.close()
        if session.query(Source.create).filter(Source.id==self.item.source_id).scalar():
            if settings.dedupe_hub_live:
                with get_session() as session_two:
                    origin_facility_list_item = session_two.query(FacilityListItem).filter(FacilityListItem.id==self.item.id).one()
                    origin_facility_list_item.status = self.item.status
                    # Update the JSON column data
                    session_two.query(FacilityListItem).\
                        filter(FacilityListItem.id == origin_facility_list_item.id).update({"processing_results": processing_results_data})
                    origin_facility_list_item.facility_id = self.item.facility_id
                    session_two.commit()

                session_two.close()
