import logging

from typing import Any, Dict, List

from app.database.models.facility_list_item import FacilityListItem
from app.matching.DTOs.match_dto import MatchDTO
from app.matching.DTOs.facility_list_item_dto import FacilityListItemDict
from app.matching.matcher.base_matcher import BaseMatcher
from app.matching.matcher.exact.exact_item_match import ExactItemMatch
from app.database.sqlalchemy import get_session

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


class ExactMatcher(BaseMatcher):
    automatic_threshold: float
    started: str
    finished: str
    item_match = ExactItemMatch

    def __init__(self) -> None:
        self.automatic_threshold = 1.0
        super().__init__()

    def process(
        self, messy: FacilityListItemDict
    ) -> Dict[str, List[MatchDTO]]:
        self.set_start()

        log.info('[Matching] Exact match processing started!')
        log.info(f'[Matching] Messy data: {messy}')

        matches = {
            messy_id: self.identify_exact_matches(item)
            for messy_id, item in messy.items()
        }
        self.set_finish()

        log.info('[Matching] Exact match processing finished!')
        log.info(f'[Matching] Exact matches result: {matches}')

        return matches

    def identify_exact_matches(
        self, facility_list_item
    ) -> List[MatchDTO or None]:

        exact_matches = self.get_exact_matches(facility_list_item)

        if len(exact_matches) > 0:
            return exact_matches

        return []

    def get_exact_matches(self, facility_list_item) -> List[MatchDTO]:
        result_list: List[MatchDTO] = []
        for item in self.get_matched_items(facility_list_item):
            exact_match_dto: MatchDTO = {
                'id': item.id,
                'facility_id': item.facility_id,
                'score': '1'
            }
            result_list.append(exact_match_dto)

        return result_list

    @staticmethod
    def get_matched_items(facility_list_item):
        with get_session() as session:
            return (session.query(FacilityListItem). \
                filter(
                    FacilityListItem.status.in_([FacilityListItem.MATCHED, FacilityListItem.CONFIRMED_MATCH]),
                    FacilityListItem.facility_id != None,
                    FacilityListItem.clean_name == facility_list_item.get('name', ''),
                    FacilityListItem.clean_address == facility_list_item.get('address', ''),
                    FacilityListItem.country_code == facility_list_item.get('country', '').upper()
                ). \
                all()
            )
        
    def get_started(self):
        return self.started
    
    def get_finished(self):
        return self.finished
    
    def get_results(self) -> Dict:
        return {}
