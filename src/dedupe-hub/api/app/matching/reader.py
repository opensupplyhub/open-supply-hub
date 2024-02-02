from typing import Dict, List

from app.utils.clean import clean
from app.utils.helpers import transform_to_dict
from app.database.models.facility_list_item import FacilityListItem
from app.database.models.facility_list_item_temp import FacilityListItemTemp
from app.database.sqlalchemy import get_session
from app.matching.DTOs.facility_list_item_dto import FacilityListItemDict


class Reader:
    def __init__(self, source_id):
        self.source_id = source_id

    def read(self) -> FacilityListItemDict:
        with get_session() as session:
            result = session.query(FacilityListItemTemp.id, FacilityListItemTemp.country_code, FacilityListItemTemp.name, FacilityListItemTemp.address). \
                filter(
                    FacilityListItemTemp.source_id == self.source_id,
                    FacilityListItemTemp.status == FacilityListItemTemp.GEOCODED
                ). \
                all()

            facility_list_items_data = transform_to_dict(result)

            return self.process_to_dict_by_id(facility_list_items_data)

    @staticmethod
    def process_to_dict_by_id(
        data: List[Dict[str, str]]
    ) -> FacilityListItemDict:

        return {
            item['id']: {
                key: clean(value)
                for key, value in item.items()
                if key != 'id'
            }
            for item in data
        }
