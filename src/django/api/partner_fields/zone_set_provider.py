from typing import Any, Dict, List, Optional

from django.db.models import Q
from waffle import switch_is_active

from api.models.zone_set import Zone, ZoneSet
from api.partner_fields.base_provider import SystemPartnerFieldProvider

# Gates every zone-set surface: the providers in the registry, the
# Spotlight Partners search filter and the contributor-profile
# spotlight. Created inactive by migration 0247 so no surface queries
# `api_zoneset` on an image that is live before `migrate` has run in
# post-deploy, and so every zone-set-backed field can be pulled from
# all surfaces at once without a deploy. The hard-wired providers do
# not depend on it.
ZONE_SETS_SWITCH = 'enable_zone_sets'


def get_active_zone_sets_for_fields(field_names) -> List[ZoneSet]:
    """
    Return the active zone sets whose partner field is one of the names.

    This is how the search filter and the contributor-profile
    spotlight tell a zone-set field apart from a contributed one: a
    name that comes back here is served by polygons, not by
    `ExtendedField` rows, and must be matched by location instead.

    Returns an empty list — so the caller treats every name as
    contributed and finds nothing for the zone-set ones — when the
    `enable_zone_sets` switch is off, when no name is linked to a zone
    set, or when the linked set is inactive. The `api_zoneset` table
    is not queried at all while the switch is off, matching the
    registry.
    """
    if not field_names or not switch_is_active(ZONE_SETS_SWITCH):
        return []
    return list(
        ZoneSet.objects.filter(
            active=True,
            partner_field__name__in=field_names,
        ).select_related('partner_field')
    )


def build_zone_sets_covered_q(zone_sets):
    """
    Build the query condition "a zone of one of these sets covers the
    location", for a `FacilityIndex` queryset.

    This is the one shared definition of "inside the dataset" for the
    Spotlight Partners search filter and the contributor-profile
    spotlight, mirroring `build_covered_locations_q` for the India
    Labour Line, so the two surfaces cannot drift apart.

    The condition reads the materialised `zone_set_ids` column with an
    array overlap (`&&`), answered from the GIN index on it, so the
    whole-result count and map extent of a zone-set search cost what
    any broad search costs (OSDEV-3743). The column holds the sets
    whose zones cover the row's location by the same `ST_Covers` test
    `ZoneSet.resolve_zone` runs for the location page, refreshed by
    `index_facilities_by` on every facility save and by the
    `zone_set_ids` backfill after a set's zones are replaced (see
    `api.facility_index_backfill.zone_set_ids_recompute`). It lists
    inactive sets too: the switch-off and inactive-set behaviour comes
    from which ids the caller passes, not from the column.

    Args:
        zone_sets: The `ZoneSet` rows to test against. Pass only active
            sets; this helper does not re-check `active` or the switch
            (see `get_active_zone_sets_for_fields`).

    Returns:
        A `Q` against a queryset whose model carries `zone_set_ids`.
    """
    return Q(zone_set_ids__overlap=[zone_set.id for zone_set in zone_sets])


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

    # "Outside every zone" is the normal case for a dataset that covers
    # only part of the globe, so a miss is not worth a warning per
    # location per zone set on the details endpoint.
    log_missing_raw_data = False

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
            # `raw_value` (singular) is what keeps this field out of
            # the facility downloads: `fetch_only_raw_values` on the
            # base class returns None unless the value carries a
            # `raw_values` dict. That is deliberate for now (downloads
            # are a separate ticket), so a zone-set field missing from
            # a download is this line, not the download serializer.
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
