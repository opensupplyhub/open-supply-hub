from typing import List, Dict
from datetime import datetime

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
