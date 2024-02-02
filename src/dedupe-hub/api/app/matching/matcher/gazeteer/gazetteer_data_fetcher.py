from typing import Dict, List
from app.utils.clean import clean
from app.utils.helpers import transform_to_dict
from app.matching.matcher.gazeteer.gazetteer_helper import match_to_extended_facility_id
from app.database.sqlalchemy import get_session
from app.database.models.facility import Facility
from app.database.models.facility_match import FacilityMatch
from app.database.models.facility_list_item import FacilityListItem

def get_canonical_items():
    """
    Fetch all `Facility` items and create a dictionary suitable for use by a
    Dedupe model.

    Returns:
    A dictionary. The key is the `Facility` OS ID. The value is a dictionary
    of clean field values keyed by field name (country, name, address). A
    "clean" value is one which has been passed through the `clean` function.
    """
    with get_session() as session:
        facility_result = session.query(Facility.id, Facility.country_code, Facility.name, Facility.address).all()
        facility_dict_data = transform_to_dict(facility_result)

        items = {str(i['id']):
                {k: clean(i[k]) for k in i if k != 'id'}
                for i in facility_dict_data}
        
        confirmed_items = {match_to_extended_facility_id(m): {
            'country': clean(m.country_code),
            'name': clean(m.name),
            'address': clean(m.address),
                    
            } for m in session.query(FacilityMatch.id, 
                                     FacilityMatch.facility_id, 
                                     FacilityListItem.country_code, 
                                     FacilityListItem.name, 
                                     FacilityListItem.address). \
                join(
                    FacilityListItem,
                    FacilityListItem.id == FacilityMatch.facility_list_item_id
                ). \
                filter(
                    FacilityMatch.status == FacilityMatch.CONFIRMED,
                ).all()
        }

        items.update(confirmed_items)

        return items

def get_messy_items_for_training(mod_factor=5):
    """
    Fetch a subset of `FacilityListItem` objects that have been parsed and are
    not in an error state.

    Arguments:
    mod_factor -- Used to partition a subset of `FacilityListItem` records. The
                  larger the value, the fewer records will be contained in the
                  subset.

    Returns:
    A dictionary. The key is the `FacilityListItem` ID. The value is a
    dictionary of clean field values keyed by field name (country, name,
    address). A "clean" value is one which has been passed through the `clean`
    function.
    """
    with get_session() as session:
        facility_list_item_q = session.query(FacilityListItem.id, FacilityListItem.country_code, FacilityListItem.name, FacilityListItem.address). \
            filter(
                FacilityListItem.status != FacilityListItem.UPLOADED,
                FacilityListItem.status != FacilityListItem.ERROR,
                FacilityListItem.status != FacilityListItem.ERROR_PARSING,
                FacilityListItem.status != FacilityListItem.ERROR_GEOCODING,
                FacilityListItem.status != FacilityListItem.ERROR_MATCHING,
                FacilityListItem.facility_id != None
            ).all()
        facility_list_item_dict_data = transform_to_dict(facility_list_item_q)
        records = [record for (i, record) in enumerate(facility_list_item_dict_data)
                if i % mod_factor == 0]
        return {str(i['id']): {k: clean(i[k]) for k in i if k != 'id'}
                for i in records}