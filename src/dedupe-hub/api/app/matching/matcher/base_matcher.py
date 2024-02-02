from typing import List, Dict
from datetime import datetime

from app.database.modifier.extended_fields import update_extendedfields_for_list_item
from app.database.sqlalchemy import get_session
from app.database.models.facility_list_item import FacilityListItem
from app.matching.DTOs.facility_list_item_dto import FacilityListItemDict
from app.matching.DTOs.match_dto import MatchDTO
from app.matching.matcher.base_item_match import BaseItemMatch


class BaseMatcher:
    automatic_threshold: float
    started: str
    finished: str

    item_match = BaseItemMatch

    def __init__(self) -> None:
        pass

    def process(self, messy: FacilityListItemDict) -> Dict[str, List[MatchDTO]]:
        pass

    def update_extended_fields(self, messy) -> None:
        with get_session() as session:
            items = session.query(FacilityListItem).filter(
                FacilityListItem.id.in_(list(messy.keys())),
                FacilityListItem.facility_id != None
            )
            for item in items:
                update_extendedfields_for_list_item(item)

    def set_start(self):
        self.started = str(datetime.now())

    def set_finish(self):
        self.finished = str(datetime.now())

    def get_started(self):
        pass
    
    def get_finished(self):
        pass

    def get_results(self) -> Dict:
        pass
