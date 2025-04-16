import logging

from typing import List, Tuple, Dict
from typing_extensions import DefaultDict

from dedupe import core, Gazetteer, StaticGazetteer
from app.config import settings

from sqlalchemy import *
from sqlalchemy.orm import *

from app.exceptions import NoCanonicalRecordsError
from app.database.models.facility import Facility
from app.matching.DTOs.match_dto import MatchDTO
from app.matching.DTOs.facility_match_dto import FacilityMatchDTO
from app.matching.DTOs.facility_list_item_dto import FacilityListItemDict
from app.matching.DTOs.results_dto import ResultsDTO
from app.matching.matcher.base_matcher import BaseMatcher
from app.matching.matcher.gazeteer.gazetteer_cache import GazetteerCache
from app.matching.matcher.gazeteer.gazetteer_item_match import GazetteerItemMatch
from app.matching.matcher.gazeteer.gazetteer_match_defaults import GazetteerMatchDefaults
from app.matching.matcher.gazeteer.gazetteer_helper import normalize_extended_facility_id
from app.database.sqlalchemy import get_session

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


class GazetteerMatcher(BaseMatcher):
    automatic_threshold: float
    gazetteer_threshold: float
    recall_weight: float
    no_gazetteer_matches: bool
    no_geocoded_items: bool
    started: str
    finished: str

    item_match = GazetteerItemMatch

    def __init__(
        self,
        automatic_threshold=GazetteerMatchDefaults.AUTOMATIC_THRESHOLD,
        gazetteer_threshold=GazetteerMatchDefaults.GAZETTEER_THRESHOLD,
        recall_weight=GazetteerMatchDefaults.RECALL_WEIGHT
    ):
        self.automatic_threshold = automatic_threshold
        self.gazetteer_threshold = gazetteer_threshold
        self.recall_weight = recall_weight

        super().__init__()

    def process(self, messy: FacilityListItemDict) -> Dict[str, List[MatchDTO]]:
        self.set_start()

        log.info('[Matching] Gazetteer match processing started!')
        log.info(f'[Matching] Messy data: {messy}')

        gazetter_matches = self.gazetter_match(messy)
        if isinstance(gazetter_matches, list) and len(gazetter_matches) == 0:
            return gazetter_matches

        self.set_finish()

        return self.filter_matches(gazetter_matches)

    def gazetter_match(self, messy):
        if len(messy.keys()) == 0:
            with get_session() as session:
                self.no_gazetteer_matches = session.query(Facility).count() == 0
                self.no_geocoded_items = len(messy.keys()) == 0
                return []

        self.no_geocoded_items = False
        try:
            self.no_gazetteer_matches = False
            gazetteer = self.get_gazetteer(messy)
            return gazetteer.match(
                messy,
                threshold=self.gazetteer_threshold,
                n_matches=None,
                generator=True
            )
        except NoCanonicalRecordsError:
            log.error('[Matching] Error: No canonical records')
            self.no_gazetteer_matches = True
            return []
        except core.BlockingError as error:
            log.error(f'[Matching] Blocking Error: {error}')
            self.no_gazetteer_matches = True
            return []

    def filter_matches(
        self, results: List[Tuple[Tuple[str, str], float]]
    ) -> DefaultDict[str, List[MatchDTO]]:
        """
        The gazetteer matcher obtained from the GazetteerCache may
        have encountered an exception raised by Dedupe while
        unindexing records and could therefore return matches
        for facility IDs that no longer exist due to merging or
        deleting.
        """
        item_matches = DefaultDict(list)

        for matches in results:
            for (messy_id, canon_id), score in matches:
                if self.facility_exists(canon_id):
                    item_matches[messy_id].append({
                        'id': messy_id,
                        'facility_id': canon_id, 
                        'score': float(score)
                        })

        log.info('[Matching] Gazetteer match processing finished!')
        log.info(f'[Matching] Gazetteer matches result: {item_matches}')

        return item_matches

    def get_gazetteer(self, messy) -> Gazetteer or StaticGazetteer:
        gazetteer = GazetteerCache.get_latest()
        gazetteer.threshold(messy, recall_weight=self.recall_weight)

        return gazetteer

    def facility_exists(self, canon_id: str) -> bool:
        with get_session() as session:
            return session.query(exists().where(Facility.id==normalize_extended_facility_id(canon_id))).scalar()

    def get_results(self) -> ResultsDTO:
        return {
            'no_gazetteer_matches': self.no_gazetteer_matches,
            'no_geocoded_items': self.no_geocoded_items,
            'gazetteer_threshold': self.gazetteer_threshold,
            'automatic_threshold': self.automatic_threshold,
            'recall_weight': self.recall_weight,
            'code_version': settings.git_commit.lower().capitalize()
        }
    
    def get_started(self):
        return self.started
    
    def get_finished(self):
        return self.finished
