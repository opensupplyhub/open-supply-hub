from typing import List, Dict
from datetime import datetime

from app.utils.os_id import make_os_id
from app.utils.constants import ProcessingAction
from app.database.sqlalchemy import get_session
from app.database.models.facility import Facility
from app.database.models.facility_list_item import FacilityListItem
from app.database.models.facility_list_item_temp import FacilityListItemTemp
from app.database.models.facility_match_temp import FacilityMatchTemp
from app.database.models.source import Source
from app.matching.DTOs.facility_list_item_dto import FacilityListItemDict
from app.matching.DTOs.facility_match_dto import FacilityMatchDTO
from app.matching.DTOs.match_dto import MatchDTO
from app.matching.matcher.base_matcher import BaseMatcher
from app.matching.matcher.exact.exact_matcher import ExactMatcher
from app.matching.matcher.gazeteer.gazetteer_matcher import GazetteerMatcher
from app.config import settings

class CumulativeMatcher(BaseMatcher):
    matchers = (ExactMatcher, GazetteerMatcher)

    def __init__(self) -> None:
        pass

    def process(self, messy: FacilityListItemDict) -> List[FacilityMatchDTO]:
        results: List[FacilityMatchDTO] = []
        originMessy = messy
        for matcher in self.matchers:
            if len(messy) == 0:
                break
            processed_matches = self.process_matches(matcher(), messy)
            results.extend(processed_matches)
            messy = self.clean_matched(messy, processed_matches)

        unmatched_processed = self.process_unmatched_items(originMessy, results)
        results.extend(unmatched_processed)
        if settings.dedupe_hub_live:
            self.update_extended_fields(originMessy)

        return results

    def clean_matched(self, messy, processed_matches):
        match_ids = [fm_dto.get('facility_list_item_id', '') for fm_dto in processed_matches]
        return {
            id: value
            for id, value in messy.items()
            if int(id) not in match_ids
        }

    def process_matches(
        self, matcher: BaseMatcher, messy: FacilityListItemDict
    ) -> List[FacilityMatchDTO]:
        """
        Returns array of all matches as:
        [
            {
                "facility_list_item_id": FacilityListItem.id,
                "facility_id": Facility.id,
                "confidence": float,
                "status": FacilityMatch.status,
                "results": match.results
            }
        ]
        """

        matched: Dict[str, List[MatchDTO]] = matcher.process(messy)

        if isinstance(matched, list) and len(matched) == 0:
            return []

        return [
            item
            for item_id, matches in matched.items()
            for item in matcher.item_match(
                item_id=item_id,
                matches=matches,
                started=matcher.get_started(),
                finished=matcher.get_finished(),
                results=matcher.get_results(),
                automatic_threshold=matcher.automatic_threshold
            ).process()
        ]

    def process_unmatched_items(self, messy, matched):
        results: List[FacilityMatchDTO] = []

        messy_ids = messy.keys()
        matched_ids = []

        if len(matched) > 0:
            matched_ids = [item.get('facility_list_item_id', '') for item in matched]

        with get_session() as session:
            unmatched_list_items = session.query(FacilityListItemTemp). \
                filter(
                    FacilityListItemTemp.id.in_(messy_ids),
                    FacilityListItemTemp.id.not_in(matched_ids)
                ). \
                all()
            
            for unmatched_list_item in unmatched_list_items:
                facility_id = None
                if session.query(Source.create).filter(Source.id==unmatched_list_item.source_id).scalar():
                    if settings.dedupe_hub_live:
                        facility = Facility()
                        facility.id = make_os_id(unmatched_list_item.country_code)
                        facility.name = unmatched_list_item.name
                        facility.address = unmatched_list_item.address
                        facility.country_code = unmatched_list_item.country_code
                        facility.location = unmatched_list_item.geocoded_point
                        facility.created_from_id = unmatched_list_item.id
                        facility.ppe_product_types = unmatched_list_item.ppe_product_types
                        facility.ppe_contact_email = unmatched_list_item.ppe_contact_email
                        facility.ppe_contact_phone = unmatched_list_item.ppe_contact_phone
                        facility.ppe_website = unmatched_list_item.ppe_website
                        facility.created_at = datetime.now()
                        facility.updated_at = datetime.now()

                        session.add(facility)
                        session.commit()

                        facility_id = facility.id
                    else:
                        facility_id = "AB_Test_" + make_os_id(unmatched_list_item.country_code)

                    json_data = {
                        'error': False,
                        'action': ProcessingAction.MATCH,
                        'started_at': str(datetime.now()),
                        'finished_at': str(datetime.now())
                    }
                    processing_results_data = unmatched_list_item.processing_results
                    processing_results_data.append(json_data)

                    # Update the JSON column data
                    session.query(FacilityListItemTemp).\
                        filter(FacilityListItemTemp.id == unmatched_list_item.id).update({"processing_results": processing_results_data})

                    unmatched_list_item.status = FacilityListItemTemp.MATCHED
                    unmatched_list_item.facility_id = facility_id
                    unmatched_list_item.version = settings.dedupe_hub_version

                    session.commit()

                    if settings.dedupe_hub_live:
                        origin_list_item = session.query(FacilityListItem). \
                            filter(
                                FacilityListItem.id == unmatched_list_item.id,
                            ). \
                            one()
                        
                        # Update the JSON column data
                        session.query(FacilityListItem).\
                            filter(FacilityListItem.id == unmatched_list_item.id).update({"processing_results": processing_results_data})
                        
                        origin_list_item.status = FacilityListItem.MATCHED
                        origin_list_item.facility_id = facility_id

                        session.commit()

                    results.append({
                        "facility_list_item_id": unmatched_list_item.id,
                        "facility_id": facility_id,
                        "status": FacilityMatchTemp.AUTOMATIC,
                        "results": {'match_type': 'no_gazetteer_match'},
                        "confidence": 1,
                    })

            session.close()

            return results


