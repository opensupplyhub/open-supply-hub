# api/services/production_location_defaults.py
from typing import Dict
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem


def fetch_required_fields(os_id: str) -> Dict[str, str]:
    # 1) Try “promoted match” list item first
    promoted = (
        FacilityListItem.objects
        .filter(facility_id=os_id)
        .filter(
            processing_results__contains=[{'action': 'promote_match'}]
        )
        .order_by('-created_at')
        .first()
    )
    if promoted and promoted.name:
        return {
            'name': promoted.name,
            'address': promoted.address or '',
            'country': promoted.country_code or '',
        }

    # 2) Fallback to latest list item
    latest = (
        FacilityListItem.objects
        .filter(facility_id=os_id)
        .order_by('-created_at')
        .first()
    )
    if latest:
        return {
            'name': latest.name or '',
            'address': latest.address or '',
            'country': latest.country_code or '',
        }

    # 3) Fallback to Facility
    os = Facility.objects.get(id=os_id)
    return {
        'name': os.name,
        'address': os.address,
        'country': os.country_code,
    }
