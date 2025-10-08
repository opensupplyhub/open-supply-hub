from typing import Dict, List
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


def has_coordinates(data: Dict) -> bool:
    return bool(data.get('coordinates'))


def get_missing_required_fields(data: Dict) -> List[str]:
    required_fields = ('name', 'address', 'country')
    return [field for field in required_fields if not data.get(field)]


def has_all_required_fields(data: Dict) -> bool:
    return len(get_missing_required_fields(data)) == 0


def has_some_required_fields(data: Dict) -> bool:
    missing_count = len(get_missing_required_fields(data))
    return 0 < missing_count < 3


def is_coordinates_without_all_required_fields(data: Dict) -> bool:
    return has_coordinates(data) and not has_all_required_fields(data)
