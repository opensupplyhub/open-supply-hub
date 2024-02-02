from app.utils.clean import clean

def facility_values_to_dedupe_record(facility_dict):
    """
    Convert a dictionary with id, country, name, and address keys into a
    dictionary suitable for training and indexing a Dedupe model.

    Arguments:
    facility_dict -- A dict with id, country, name, and address key created
                     from a `Facility` values query.

    Returns:
    A dictionary with the id as the key and a dictionary of fields
    as the value.
    """
    return {
        str(facility_dict['id']): {
            "country": clean(facility_dict['country']),
            "name": clean(facility_dict['name']),
            "address": clean(facility_dict['address']),
        }
    }

def match_detail_to_extended_facility_id(facility_id, match_id):
    return '{}_MATCH-{}'.format(facility_id, match_id)

def match_to_extended_facility_id(match):
    """
    We want manually confirmed matches to influence the matching process.
    We were not successful when adding them as training data so we add them
    to our list of canonical items with a synthetic ID. When post
    processing the matches we will drop the extension using the
    `normalize_extended_facility_id` function.
    """
    return match_detail_to_extended_facility_id(
        str(match.facility_id), str(match.id))

def normalize_extended_facility_id(facility_id: str) -> str:
    """
    Manually confirmed matches are added to the list of canonical
    facilities with a synthetic ID. This function converts one of these
    extended IDs back to a plain Facility ID. A plain Facility ID will pass
    through this function unchanged.
    """
    return facility_id.split('_')[0]