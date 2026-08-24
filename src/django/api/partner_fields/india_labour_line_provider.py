import logging
from typing import Any, Dict, Optional

from django.db.models import Q

from api.models.partner_field import PartnerField
from api.partner_fields.base_provider import SystemPartnerFieldProvider

logger = logging.getLogger(__name__)

# The sectors the helpline covers (the request behind this feature was
# a textile facility list). A location must have at least one of these
# sectors, in addition to being inside the boundary, to get the field.
# Matching is exact-text against the production sector taxonomy, so
# these must be spelled exactly as they appear in the sector dropdown.
INDIA_LABOUR_LINE_SECTORS = [
    'Apparel',
    'Apparel Accessories',
    'Footwear',
    'Home Textiles',
    'Leather',
    'Textiles',
]


def get_india_labour_line_polygon():
    """
    Return the boundary polygon the helpline field points at.

    The partner field row holds a database link (a ForeignKey) to its
    coverage polygon, set in the Django admin. The link is rename-proof,
    and the database refuses to delete a polygon a field still points
    at. A loud warning is logged when the field or its link is missing,
    since the feature stays dormant until both exist.

    Returns:
        The linked Polygon, or None when the field doesn't exist or no
        polygon has been linked yet.
    """
    field = (
        PartnerField.objects.get_all_including_inactive()
        .filter(name=IndiaLabourLineProvider.FIELD_NAME)
        .select_related('polygon')
        .first()
    )
    if field is None:
        logger.warning(
            f"Partner field '{IndiaLabourLineProvider.FIELD_NAME}' not "
            'found; the India Labour Line helpline is dormant.'
        )
        return None
    if field.polygon is None:
        logger.warning(
            f"Partner field '{IndiaLabourLineProvider.FIELD_NAME}' has "
            'no coverage polygon linked; the India Labour Line '
            'helpline is dormant until one is set in the admin.'
        )
        return None
    return field.polygon


def build_covered_locations_q():
    """
    Build the query condition for "the helpline covers this location".

    "Covered" means: inside the linked boundary polygon AND working in
    at least one covered sector. This is the one shared definition of
    that rule — the contributor-profile spotlight and the search
    filter both use it, so the two can never drift apart.

    Returns:
        A Q object expressing the rule, or None when no coverage
        polygon is linked (the lookup helper logs a warning in that
        case). Callers must treat None as "match nothing", never as
        "match everything".
    """
    polygon = get_india_labour_line_polygon()
    if polygon is None:
        return None
    return (
        Q(location__within=polygon.geom)
        & Q(sector__overlap=INDIA_LABOUR_LINE_SECTORS)
    )


def get_covered_production_locations(base_queryset=None):
    """
    Return the production locations the helpline covers.

    Applies the shared covered-locations rule (see
    build_covered_locations_q) directly to the given queryset, so the
    database runs one flat query with no id sub-lookup.

    Args:
        base_queryset: Optional FacilityIndex queryset to narrow (for
            example, a view's own queryset with its ordering and field
            selection). Defaults to all production locations.

    Returns:
        The covered locations; an empty queryset — never "everything" —
        when no coverage polygon is linked.
    """
    from api.models.facility.facility_index import FacilityIndex

    if base_queryset is None:
        base_queryset = FacilityIndex.objects.all()
    covered_q = build_covered_locations_q()
    if covered_q is None:
        return base_queryset.none()
    return base_queryset.filter(covered_q)


class IndiaLabourLineProvider(SystemPartnerFieldProvider):
    """
    Provides the India Labour Line helpline as a system partner field
    for production locations inside the linked coverage boundary.

    Mirrors MITLivingWageProvider, with a polygon instead of counties:
    the location's point is tested against the boundary polygon the
    partner field links to, and the helpline phone number is read at
    request time from the partner field's display_text, so the number
    can be changed in the Django admin without a deploy (display_text
    stays editable even on protected system fields).
    """

    FIELD_NAME = 'india_labour_line_helpline'

    def _get_field_name(self) -> str:
        """Return the partner field name for this provider."""
        return self.FIELD_NAME

    def _fetch_raw_data(self, production_location) -> Optional[Dict]:
        """
        Decide whether this location gets the helpline, and gather what
        the formatted field needs.

        Cheap checks run first (country, has a location, sector)
        so most locations never reach the geometry containment check.
        This runs on every page render, so it keeps its own lean
        one-location path rather than going through
        get_covered_production_locations() — but it applies the same
        boundary and sector rules, and the test suite holds the two
        paths to the same answers.

        Args:
            production_location: The Facility being rendered.

        Returns:
            A dict with the coverage `polygon` and the `phone_number`
            to display, or None when the location is outside the
            boundary (or the feature is unconfigured).
        """
        if production_location.country_code != 'IN':
            return None

        if not production_location.location:
            return None

        if not self.__has_covered_sector(production_location):
            return None

        polygon = get_india_labour_line_polygon()
        if polygon is None:
            return None
        if not polygon.geom.contains(production_location.location):
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

        The displayed dates come from the coverage polygon's own
        timestamps — the same rule MIT Living Wage uses (its dates are
        the county boundary rows' timestamps).

        Args:
            raw_data: The dict returned by `_fetch_raw_data` (coverage
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

    def __has_covered_sector(self, production_location) -> bool:
        """
        Check whether the location works in a covered sector.

        The details page passes a FacilityIndex (which carries the
        location's sectors directly); the v1 endpoint passes a Facility
        (which doesn't), so in that case the sectors are looked up from
        the search index by the location's id.

        Args:
            production_location: The Facility or FacilityIndex being
                rendered.
        """
        sectors = getattr(production_location, 'sector', None)
        if sectors is None:
            from api.models.facility.facility_index import FacilityIndex
            sectors = (
                FacilityIndex.objects
                .filter(id=production_location.id)
                .values_list('sector', flat=True)
                .first()
            ) or []
        return bool(set(sectors) & set(INDIA_LABOUR_LINE_SECTORS))

    def __get_phone_number(self) -> Optional[str]:
        """
        Read the helpline number from the partner field's display_text.

        display_text stays editable in the Django admin even on
        protected system fields, so staff can update the number with
        no deploy. A missing field or blank number logs a warning and
        disables the field rather than crashing a page render.
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

        phone_number = (partner_field.display_text or '').strip()
        if not phone_number:
            logger.warning(
                f"Partner field '{self.FIELD_NAME}' has no display_text "
                '(the helpline number); the India Labour Line helpline '
                'cannot be displayed.'
            )
            return None

        return phone_number
