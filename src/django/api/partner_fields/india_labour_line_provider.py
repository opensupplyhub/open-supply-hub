import json
import logging
from typing import Any, Dict, List, Optional

from waffle import switch_is_active

from api.models.partner_field import PartnerField
from api.models.polygon import Polygon
from api.partner_fields.base_provider import SystemPartnerFieldProvider

logger = logging.getLogger(__name__)

# Waffle switch gating every India Labour Line behavior (this provider,
# the contributor-profile spotlight, and the search filter). Off by
# default; flip it in the Django admin (Waffle > Switches) to go live.
INDIA_LABOUR_LINE_SWITCH = 'india_labour_line_helpline'

# The Polygon rows (looked up by name) whose boundaries carry the
# India Labour Line helpline. This is deliberately a code-level list —
# the same pattern as MITLivingWageProvider hard-coding US counties —
# so changing coverage is a reviewed code change, while the boundary
# shapes themselves stay editable in the Django admin.
#
# The boundary is one (multi-part) Polygon covering every area the
# helpline serves; more names can be added here if coverage is ever
# split across multiple rows.
INDIA_LABOUR_LINE_POLYGON_NAMES = [
    'india_labour_line_helpline_areas',
]


def get_india_labour_line_polygons() -> List[Polygon]:
    """
    Return the Polygon rows backing the India Labour Line field.

    Looks up `INDIA_LABOUR_LINE_POLYGON_NAMES` in the database and logs
    a loud warning when any configured name is missing (the one
    fragility of referencing polygons by name: renaming a polygon in
    the admin would silently break the link, so we make it noisy).

    Returns:
        The Polygon rows that exist, possibly fewer than configured
        (or none at all) if names are missing.
    """
    polygons = list(
        Polygon.objects.filter(name__in=INDIA_LABOUR_LINE_POLYGON_NAMES)
    )
    missing = (
        set(INDIA_LABOUR_LINE_POLYGON_NAMES)
        - {polygon.name for polygon in polygons}
    )
    if missing:
        logger.warning(
            'India Labour Line polygons missing from the database: '
            f'{sorted(missing)}. The field will not appear for '
            'locations in those areas until Polygon rows with these '
            'exact names exist.'
        )
    return polygons


class IndiaLabourLineProvider(SystemPartnerFieldProvider):
    """
    Provides the India Labour Line helpline as a system partner field
    for production locations inside specific Indian state/region
    boundaries.

    Mirrors MITLivingWageProvider, with polygons instead of counties:
    the location's point is tested against the Polygon rows named in
    `INDIA_LABOUR_LINE_POLYGON_NAMES`, and the helpline phone number is
    read at request time from the partner field's JSON schema (the
    `default` of its `phone_number` property), so the number can be
    changed in the Django admin without a deploy.
    """

    FIELD_NAME = 'india_labour_line_helpline'

    # Declares the polygons this provider depends on, so the polygon
    # admin can warn staff before renaming or deleting one of them.
    POLYGON_NAMES = INDIA_LABOUR_LINE_POLYGON_NAMES

    def _get_field_name(self) -> str:
        """Return the partner field name for this provider."""
        return self.FIELD_NAME

    def _fetch_raw_data(self, production_location) -> Optional[Dict]:
        """
        Decide whether this location gets the helpline, and gather what
        the formatted field needs.

        Cheap checks run first (feature switch, country, has a
        location) so most locations never reach the PostGIS
        containment query.

        Args:
            production_location: The Facility being rendered.

        Returns:
            A dict with the matched `polygon` and the `phone_number`
            to display, or None when the location is outside every
            configured boundary (or the feature is off/misconfigured).
        """
        if not switch_is_active(INDIA_LABOUR_LINE_SWITCH):
            return None

        if production_location.country_code != 'IN':
            return None

        if not production_location.location:
            return None

        polygon = Polygon.objects.filter(
            name__in=INDIA_LABOUR_LINE_POLYGON_NAMES,
            geom__contains=production_location.location,
        ).first()

        if polygon is None:
            # Distinguish "outside the boundaries" (normal, quiet) from
            # "the configured polygons don't exist" (misconfiguration,
            # loud) — the helper logs the warning.
            get_india_labour_line_polygons()
            return None

        phone_number = self.__get_phone_number()
        if phone_number is None:
            return None

        return {'polygon': polygon, 'phone_number': phone_number}

    def _format_data(
        self,
        raw_data: Dict,
        contributor_info: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Format the helpline into the standard partner field structure.

        Args:
            raw_data: The dict returned by `_fetch_raw_data` (matched
                polygon plus phone number).
            contributor_info: The partner organization's details, as
                resolved by the base class (None on the download-only
                fast path).
        """
        polygon = raw_data['polygon']
        raw_values = {'phone_number': raw_data['phone_number']}

        return {
            'id': None,
            'value': {
                'raw_values': raw_values,
            },
            'created_at': polygon.created_at.isoformat(),
            'updated_at': polygon.updated_at.isoformat(),
            'field_name': self.FIELD_NAME,
            'contributor': contributor_info,
            'is_verified': False,
            'value_count': 1,
            # Random ID for being not from a claim.
            'facility_list_item_id': 1111,
            'should_display_association': True,
        }

    def __get_phone_number(self) -> Optional[str]:
        """
        Read the helpline number from the partner field's JSON schema.

        The number lives in the schema as the `default` of the
        `phone_number` property, so staff can update it in the Django
        admin with no deploy. Any missing piece (field row, schema,
        property, default) logs a warning and disables the field
        rather than crashing a page render.
        """
        partner_field = (
            PartnerField.objects.get_all_including_inactive()
            .filter(name=self.FIELD_NAME)
            .first()
        )
        if partner_field is None:
            logger.warning(
                f"Partner field '{self.FIELD_NAME}' not found; the "
                'India Labour Line helpline cannot be displayed.'
            )
            return None

        schema = partner_field.json_schema
        # The column usually deserializes to a dict, but tolerate a
        # JSON string too (other code parses it the same way).
        if isinstance(schema, str):
            try:
                schema = json.loads(schema)
            except ValueError:
                schema = None

        phone_number = None
        if isinstance(schema, dict):
            properties = schema.get('properties')
            if isinstance(properties, dict):
                phone_property = properties.get('phone_number')
                if isinstance(phone_property, dict):
                    phone_number = phone_property.get('default')

        if not isinstance(phone_number, str) or not phone_number:
            logger.warning(
                f"Partner field '{self.FIELD_NAME}' has no "
                "properties.phone_number.default in its JSON schema; "
                'the India Labour Line helpline cannot be displayed.'
            )
            return None

        return phone_number
