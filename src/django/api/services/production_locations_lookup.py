from typing import Dict
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem


def fetch_required_fields(os_id: str) -> Dict[str, str]:
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

    os = Facility.objects.get(id=os_id)
    return {
        'name': os.name,
        'address': os.address,
        'country': os.country_code,
    }


def is_only_coordinates_present(data: Dict) -> bool:
    return (data.get('coordinates') and not all(
        data.get(field)
        for field in ('name', 'address', 'country')
    ))


def is_required_field_missing(data: Dict) -> bool:
    return all(
        not data.get(field)
        for field in ('name', 'address', 'country')
    )
