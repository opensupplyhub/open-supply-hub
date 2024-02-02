from typing import Any, Dict, List

from app.utils.clean import clean
from app.database.sqlalchemy import get_session
from app.database.models.facility import Facility
from app.database.models.facility_list_item import FacilityListItem
from app.database.models.facility_list_item_temp import FacilityListItemTemp
from app.database.models.facility_match import FacilityMatch
from app.database.models.facility_match_temp import FacilityMatchTemp
from app.database.models.source import Source
from app.matching.DTOs.results_dto import ResultsDTO
from app.matching.DTOs.facility_match_dto import FacilityMatchDTO
from app.matching.matcher.base_item_match import BaseItemMatch
from app.matching.matcher.gazeteer.gazetteer_helper import normalize_extended_facility_id
from app.config import settings


class GazetteerItemMatch(BaseItemMatch):
    item: FacilityListItemTemp
    matches: Dict[str, Any]
    automatic_threshold: float
    started: str
    finished: str
    results: ResultsDTO

    def __init__(
        self,
        item_id: int,
        matches: Dict[str, Any],
        started: str,
        finished: str,
        results: ResultsDTO,
        automatic_threshold: float,
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
        self.item.status = FacilityListItemTemp.POTENTIAL_MATCH
        self.matches = self.reduce_matches(self.matches)

        if len(self.matches) == 0:
            return []

        automatic_match = None
        if len(self.matches) == 1:
            if self.matches[0]["confidence"] >= self.automatic_threshold:
                automatic_match = self.process_match(
                    self.matches[0],
                    "single_gazetteer_match"
                )
        else:
            quality_matches = list(filter(self.good_confidence, self.matches))

            if len(quality_matches) == 1:
                automatic_match = self.process_match(
                    quality_matches[0],
                    "one_gazetteer_match_greater_than_threshold"
                )

            elif len(quality_matches) > 1:
                exact_matches = list(filter(self.string_matched, self.matches))

                # We check == 1 because multiple exact matches should not
                # happen. They are an indication of duplicate facility data
                # that should be merged through moderation tools. Showing the
                # multiple potential matches to the contributor increases the
                # visibility of the issue.
                if len(exact_matches) == 1:
                    automatic_match = self.process_match(
                        exact_matches[0],
                        (
                            "multiple_gazetteer_matches_"
                            "with_one_exact_string_match"
                        )
                    )

        self.create_pending_matches()

        if automatic_match:
            self.matches.append(automatic_match)

        self.item_save()

        with get_session() as session:
            if session.query(Source.create).filter(Source.id==self.item.source_id).scalar():
                self.create_sources()
                return self.matches

        return []

    def reduce_matches(self, matches) -> List[Dict[str, str or int]]:
        """
        Process a list of facility match scores to remove duplicate facilities,
        choosing the highest match score in the case of a duplicate.

        Arguments:
        matches -- A list of tuples of the format (extended_facility_id, score)

        Returns:
        A list of tuples in the format (facility_id, score). Extended facility

        Example:
            Input:
                [
                    (US2020052GKF19F, 75),
                    (US2020052GKF19F_MATCH-23, 88),
                    (US2020052YDVKBQ, 45)
                ]
            Output:
                [
                    (US2020052GKF19F, 88),
                    (US2020052YDVKBQ, 45)
                ]
        """
        match_dict = {}

        for match in matches:
            facility_id = normalize_extended_facility_id(match['facility_id'])

            no_facility = facility_id not in match_dict
            if not no_facility:
                less_score = match_dict[facility_id] < match['score']

            if no_facility or less_score:
                match_dict[facility_id] = match['score']

        return [
            {
                "facility_id": facility_id,
                "confidence": confidence,
            }
            for facility_id, confidence in match_dict.items()
        ]

    def make_match_object(
        self, match, status=FacilityMatchTemp.PENDING, **kwargs
    ):
        return {
            **match,
            "facility_list_item_id": self.item.id,
            "status": status,
            "results": {**self.results, **kwargs}
        }

    def process_match(self, match: Dict[str, str or int], match_type: str):
        self.item.status = FacilityListItemTemp.MATCHED
        self.item.facility_id = self.get_facility(match["facility_id"]).id
        self.delete_match_by_facility_id(match["facility_id"])

        return self.make_match_object(
            match,
            status=FacilityMatchTemp.AUTOMATIC,
            match_type=match_type
        )

    def create_pending_matches(self):
        self.matches = [
            self.make_match_object(match)
            for match in self.matches
        ]

    def create_sources(self):
        for match in self.matches:
            if match["status"] != FacilityMatchTemp.AUTOMATIC:
                continue

            self.create_source(match)

    def create_source(self, match):
        facility = self.get_facility(match["facility_id"])

        should_update_ppe_product_types = (
            self.item.ppe_product_types is not None and self.item.ppe_product_types != []
            and (facility.ppe_product_types is None or facility.ppe_product_types == []))

        should_update_ppe_contact_phone = (
            self.item.ppe_contact_phone is not None and self.item.ppe_contact_phone != ''
            and (facility.ppe_contact_phone is None or facility.ppe_contact_phone == ''))

        should_update_ppe_contact_email = (
            self.item.ppe_contact_email is not None and self.item.ppe_contact_email != ''
            and (facility.ppe_contact_email is None or facility.ppe_contact_email == ''))
        
        should_update_ppe_website = (
            self.item.ppe_website is not None and self.item.ppe_website != ''
            and (facility.ppe_website is None or facility.ppe_website == ''))

        should_save_facility = (
            should_update_ppe_product_types
            or should_update_ppe_contact_phone
            or should_update_ppe_contact_email
            or should_update_ppe_website)

        if should_save_facility and settings.dedupe_hub_live:
            with get_session() as session:
                facility_to_update = session.query(Facility).filter(Facility.id==facility.id).one()
                facility_to_update.ppe_product_types = self.item.ppe_product_types
                facility_to_update.ppe_contact_phone = self.item.ppe_contact_phone
                facility_to_update.ppe_contact_email = self.item.ppe_contact_email
                facility_to_update.ppe_website = self.item.ppe_website
                session.commit()
                session.close()

    def good_confidence(self, match: FacilityMatchDTO) -> bool:
        return match['confidence'] > self.automatic_threshold

    def string_matched(self, match: FacilityMatchDTO) -> bool:
        with get_session() as session:
            facility = session.query(Facility).filter(Facility.id==match['facility_id']).one()
            return (
                self.item.country_code == facility.country_code and
                self.clean_match(self.item.name, facility.name) and
                self.clean_match(self.item.address, facility.address)
            )

    def delete_match_by_facility_id(self, facility_id):
        self.matches = [
            match
            for match in self.matches
            if match["facility_id"] != facility_id
        ]

    @staticmethod
    def clean_match(sting_one: str, string_two: str) -> bool:
        clean(sting_one) == clean(string_two)

    @staticmethod
    def get_facility(facility_id):
        with get_session() as session:
            return session.query(Facility).filter(Facility.id==facility_id).one()
