from datetime import datetime
from typing import List
from sqlalchemy import text
from app.database.models.facility_match import FacilityMatch
from app.database.models.facility_match_temp import FacilityMatchTemp
from app.matching.DTOs.facility_match_dto import FacilityMatchDTO
from app.database.sqlalchemy import get_session
from app.config import settings


class Writer:
    def __init__(self):
        pass

    def write(
        self, processed_data: List[FacilityMatchDTO]
    ) -> List[FacilityMatchDTO]:
        with get_session() as session:
            matches = []
            for match in processed_data:
                facility_match = FacilityMatchTemp()
                facility_match.facility_id = match['facility_id']
                facility_match.confidence = float(match['confidence'])
                facility_match.facility_list_item_id = match['facility_list_item_id']
                facility_match.status = match['status']
                facility_match.results = match['results']
                facility_match.version = settings.dedupe_hub_version
                facility_match.created_at = datetime.now()
                facility_match.updated_at = datetime.now()

                session.add(facility_match)
                session.commit()

                if settings.dedupe_hub_live:
                    origin_facility_match = FacilityMatch()
                    origin_facility_match.facility_id = match['facility_id']
                    origin_facility_match.confidence = float(match['confidence'])
                    origin_facility_match.facility_list_item_id = match['facility_list_item_id']
                    origin_facility_match.status = match['status']
                    origin_facility_match.results = match['results']
                    origin_facility_match.created_at = datetime.now()
                    origin_facility_match.updated_at = datetime.now()

                    session.add(origin_facility_match)
                    session.commit()

                matches.append(facility_match)
            
            if len(matches) > 0 and settings.dedupe_hub_live:
                ids = [f_m.facility_id for f_m in matches]
                ids_set = { elem for elem in ids }
                params = {'data': list(ids_set)}
                sql = text('call index_facilities_by(:data);')
                session.execute(sql, params)
                session.commit()
            
            session.close()

            return processed_data
