from django.db.models import Q
from django.db.models import Exists, OuterRef
from api.models.extended_field import ExtendedField

from api.constants import MIT_LIVING_WAGE_COUNTRY_CODES
from api.models.wage_indicator_country_data import WageIndicatorCountryData

INDIA_LABOUR_LINE_FIELD = "india_labour_line_helpline"

SYSTEM_PARTNER_FIELD_NAMES = frozenset({
    "wage_indicator",
    "mit_living_wage",
    INDIA_LABOUR_LINE_FIELD,
})


def apply_partner_fields_or_filter(
    facilities_queryset,
    field_names,
    contributor_ids,
):
    """
    Return a queryset filtered to facilities that have data from at least
    one of the given partner field names (OR semantics).

    Regular partner fields are matched through correlated `Exists` subqueries
    against the `ExtendedField` model, scoped to the provided contributors.
    System partner fields use country-code lookups via standard `Q` objects.
    """
    filters = []

    # Zone-set fields are served by polygons, not ExtendedField rows,
    # so they are taken out of the contributed branch and matched by
    # location below. With the `enable_zone_sets` switch off (or the
    # set inactive) nothing comes back here, the names stay in the
    # contributed branch, and that branch finds no rows for them: the
    # filter then matches nothing for those fields, never everything.
    zone_sets = get_active_zone_sets_for_fields(field_names)
    zone_set_field_names = {
        zone_set.partner_field.name for zone_set in zone_sets
    }

    regular_field_names = [
        field_name
        for field_name in field_names
        if field_name not in SYSTEM_PARTNER_FIELD_NAMES
        and field_name not in zone_set_field_names
    ]

    if regular_field_names:
        # Use a correlated Exists subquery on ExtendedField so contributor
        # and partner-field matching stays in SQL without RawSQL/unnest.
        filters.append(
            Exists(
                ExtendedField.objects.filter(
                    facility_id=OuterRef("id"),
                    contributor_id__in=contributor_ids,
                    field_name__in=regular_field_names,
                )
            )
        )

    has_wage_indicator = "wage_indicator" in field_names
    has_mit_living_wage = "mit_living_wage" in field_names

    if has_wage_indicator and has_mit_living_wage:
        wage_indicator_country_codes = set(
            WageIndicatorCountryData.objects.values_list(
                "country_code", flat=True
            )
        )
        country_codes = (
            wage_indicator_country_codes | set(MIT_LIVING_WAGE_COUNTRY_CODES)
        )
        filters.append(Q(country_code__in=country_codes))
    elif has_wage_indicator:
        filters.append(
            Q(
                country_code__in=WageIndicatorCountryData.objects.values(
                    "country_code"
                )
            )
        )
    elif has_mit_living_wage:
        filters.append(Q(country_code__in=MIT_LIVING_WAGE_COUNTRY_CODES))

    if INDIA_LABOUR_LINE_FIELD in field_names:
        filters.append(build_india_labour_line_filter())

    if zone_sets:
        filters.append(build_zone_sets_covered_q(zone_sets))

    if not filters:
        return facilities_queryset

    combined_filter = filters[0]
    for filter_part in filters[1:]:
        combined_filter = combined_filter | filter_part

    return facilities_queryset.filter(combined_filter)


def apply_partner_contributors_filter(
    facilities_queryset,
    partner_contributors,
):
    """
    Filter a FacilityIndex-like queryset by partner contributors.

    Uses active PartnerField names tied to grouped partner fields.
    Multiple contributors use OR semantics.
    """
    if not partner_contributors:
        return facilities_queryset

    from api.models.partner_field import PartnerField

    partner_fields = list(
        PartnerField.objects.filter(
            contributor__id__in=partner_contributors,
            active=True,
            group__isnull=False,
        )
        .values_list("contributor__id", "name")
        .distinct()
    )

    if not partner_fields:
        return facilities_queryset.none()

    field_names = list(
        {
            field_name
            for (
                _partner_contributor_id,
                field_name,
            ) in partner_fields
        }
    )
    contributor_ids = list(
        {
            contributor_id
            for contributor_id, _field_name in partner_fields
        }
    )

    facilities_queryset = apply_partner_fields_or_filter(
        facilities_queryset,
        field_names,
        contributor_ids,
    )

    return facilities_queryset


def get_active_zone_sets_for_fields(field_names):
    """
    Return the active zone sets linked to any of the field names.

    Thin wrapper over the provider-module helper of the same name;
    the import is deferred for the same circular-import reason as
    build_india_labour_line_filter below.
    """
    from api.partner_fields.zone_set_provider import (
        get_active_zone_sets_for_fields as get_zone_sets,
    )

    return get_zone_sets(field_names)


def build_zone_sets_covered_q(zone_sets):
    """
    Return the condition matching the locations the zone sets cover.

    Delegates to the shared helper in the provider module (see
    build_zone_sets_covered_q there) so the search filter and the
    contributor-profile spotlight apply one definition of "covered".
    Deferred import, as above.
    """
    from api.partner_fields.zone_set_provider import (
        build_zone_sets_covered_q as build_covered_q,
    )

    return build_covered_q(zone_sets)


def build_india_labour_line_filter():
    """
    Return a Q matching the locations the India Labour Line covers.

    Delegates to the shared covered-locations rule (see
    build_covered_locations_q in the provider module), so search
    results can never disagree with the contributor-profile spotlight.
    The import is deferred to avoid a circular import at model-loading
    time (the provider module imports models from this package).

    When the boundary polygons are missing, this matches nothing —
    never an unfiltered "everything matches" — so a misconfiguration
    cannot quietly widen search results.
    """
    from api.partner_fields.india_labour_line_provider import (
        build_covered_locations_q,
    )

    covered_q = build_covered_locations_q()
    if covered_q is None:
        return Q(id__in=[])
    return covered_q
