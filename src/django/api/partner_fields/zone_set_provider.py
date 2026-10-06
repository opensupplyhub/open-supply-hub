from typing import Any, Dict, Optional

from api.models.zone_set import Zone, ZoneSet
from api.partner_fields.base_provider import SystemPartnerFieldProvider


class ZoneSetProvider(SystemPartnerFieldProvider):
    """
    Serves one `ZoneSet` as a system partner field.

    Unlike the other providers, which are hard-wired to one dataset
    each, this class is instantiated once per active zone set by the
    registry at request time (see `SystemPartnerFieldRegistry`), so
    adding a polygon-based dataset needs no code: upload the zones,
    link a partner field, assign the field to a contributor.

    The field's name is the linked partner field's name. The value is
    the containing zone's label, emitted in the same `raw_value` shape
    contributed string partner fields use, so both the location page
    and the v1 production-locations endpoint render it unchanged. A
    location outside every zone gets nothing — "match nothing, never
    everything", as the India Labour Line provider puts it.
    """

    def __init__(self, zone_set: ZoneSet):
        self.zone_set = zone_set

    def _get_field_name(self) -> str:
        """Return the linked partner field's name."""
        return self.zone_set.partner_field.name

    def _fetch_raw_data(self, production_location) -> Optional[Zone]:
        """
        Find the zone containing the location, if any.

        Args:
            production_location: The Facility (v1 endpoint) or
                FacilityIndex (details page) being rendered; both
                carry `location`.

        Returns:
            The containing `Zone`, or None when the location has no
            coordinates or lies outside every zone of the set.
        """
        if not production_location.location:
            return None
        return self.zone_set.resolve_zone(production_location.location)

    def _format_data(
        self,
        raw_data: Zone,
        contributor_info: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Format the zone into the standard partner field structure.

        The displayed date is the zone's own timestamp — the time of
        the upload that created it — matching how the MIT Living Wage
        and India Labour Line fields date themselves by their
        boundary rows.
        """
        uploaded_at = raw_data.created_at.isoformat()
        return {
            'id': None,
            'value': {'raw_value': raw_data.label},
            'created_at': uploaded_at,
            'updated_at': uploaded_at,
            'field_name': self._get_field_name(),
            'contributor': contributor_info,
            'is_verified': False,
            'value_count': 1,
            # Random ID for being not from a claim.
            'facility_list_item_id': 1111,
            'should_display_association': True,
        }
