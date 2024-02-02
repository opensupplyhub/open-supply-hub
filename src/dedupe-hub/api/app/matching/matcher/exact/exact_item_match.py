from typing import Any, Dict

from app.database.models.facility_list_item import FacilityListItem
from app.database.models.facility_list_item_temp import FacilityListItemTemp
from app.database.models.facility_match import FacilityMatch
from app.database.models.facility_match_temp import FacilityMatchTemp
from app.database.models.source import Source
from app.matching.DTOs.results_dto import ResultsDTO
from app.matching.matcher.base_item_match import BaseItemMatch
from app.database.sqlalchemy import get_session

facility_match_data = Dict[str, str or int or Any]


class ExactItemMatch(BaseItemMatch):
    item: FacilityListItemTemp
    matches: Dict[str, Any]
    automatic_threshold: float
    started: str
    finished: str

    def __init__(
        self,
        item_id: int,
        matches: Dict[str, Any],
        started: str,
        finished: str,
        results: ResultsDTO,
        automatic_threshold: float
    ):
        super().__init__(
            item_id=item_id,
            matches=matches,
            started=started,
            finished=finished,
            results=results,
            automatic_threshold=automatic_threshold
        )

    def process(self):
        matches = [self.make_match_object(match["facility_id"])
            for match in self.matches]
        
        if len(matches) == 0:
            return []
        
        matches[0]["status"] = FacilityMatchTemp.AUTOMATIC
        self.item.status = FacilityListItemTemp.MATCHED
        self.item.facility_id = matches[0]["facility_id"]

        if len(matches) == 1:
            matches[0]["results"]["match_type"] = "single_exact_match"
        else:
            matches[0]["results"]["match_type"] = "multiple_exact_matches"

        self.item_save(exact_match=True)
        with get_session() as session:
            if session.query(Source.create).filter(Source.id==self.item.source_id).scalar():
                return matches
            # for match in matches:
            #   m.save()
            #   TODO: handle PPE if needed

        return []

    def make_match_object(
        self, facility_id, status=FacilityMatchTemp.PENDING, **kwargs
    ):
        return {
            "facility_list_item_id": self.item.id,
            "facility_id": facility_id,
            "status": status,
            "results": {},
            "confidence": 1,
        }
