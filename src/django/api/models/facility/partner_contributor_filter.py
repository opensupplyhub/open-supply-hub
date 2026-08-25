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
    regular_field_names = [
        field_name
        for field_name in field_names
        if field_name not in SYSTEM_PARTNER_FIELD_NAMES
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
