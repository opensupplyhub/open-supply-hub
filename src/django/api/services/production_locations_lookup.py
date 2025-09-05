import logging

from typing import Dict
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem

log = logging.getLogger(__name__)


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
        log.info(f"[Production locations lookup] Found promoted match for {os_id}: {promoted.name}")
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
        log.info(f"[Production locations lookup] Found latest list item for {os_id}: {latest.name}")
        return {
            'name': latest.name or '',
            'address': latest.address or '',
            'country': latest.country_code or '',
        }

    os = Facility.objects.get(id=os_id)
    log.info(f"[Production locations lookup] Found facility for {os_id}: {os.name}")
    return {
        'name': os.name,
        'address': os.address,
        'country': os.country_code,
    }
