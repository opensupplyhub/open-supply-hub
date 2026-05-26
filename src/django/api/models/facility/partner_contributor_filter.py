from django.db.models import Q
from django.db.models import Exists, OuterRef
from api.models.extended_field import ExtendedField

from api.constants import MIT_LIVING_WAGE_COUNTRY_CODES
from api.models.wage_indicator_country_data import WageIndicatorCountryData

SYSTEM_PARTNER_FIELD_NAMES = frozenset({"wage_indicator", "mit_living_wage"})


def apply_partner_fields_or_filter(
    qs,
    field_names,
    contributor_ids,
):
    """
    Return a queryset filtered to facilities that have data from at least
    one of the given partner field names (OR semantics).

    extended_fields is ArrayField(JSONField), so partial JSON matching via
    __contains does not work — array containment requires exact element
    equality. Regular fields are handled with a correlated unnest() subquery.
    System fields use country-code lookups via standard Q objects.
    """
    filters = []

    regular = [n for n in field_names if n not in SYSTEM_PARTNER_FIELD_NAMES]

    if regular:
        # We need to use a subquery to match the extended fields because
        # the extended fields are an ArrayField(JSONField).
        filters.append(
            Exists(
                ExtendedField.objects.filter(
                    facility_id=OuterRef("id"),
                    contributor_id__in=contributor_ids,
                    field_name__in=regular,
                )
            )
        )

    if "wage_indicator" in field_names:
        filters.append(
            Q(
                country_code__in=WageIndicatorCountryData.objects.values(
                    "country_code"
                )
            )
        )

    if "mit_living_wage" in field_names:
        filters.append(Q(country_code__in=MIT_LIVING_WAGE_COUNTRY_CODES))

    if not filters:
        return qs

    combined_filter = filters[0]
    for filter_part in filters[1:]:
        combined_filter = combined_filter | filter_part

    return qs.filter(combined_filter)


def apply_partner_contributors_filter(
    qs,
    partner_contributors,
    combine_partner_contributors="",
):
    """
    Filter a FacilityIndex-like queryset by partner contributors.

    Uses active PartnerField names tied to grouped partner fields.
    Supports OR (default) and AND semantics across contributors.
    """
    if not partner_contributors:
        return qs

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

    if combine_partner_contributors.upper() == "AND":
        for contributor_id in partner_contributors:
            contributor_field_names = [
                field_name
                for (
                    partner_contributor_id,
                    field_name,
                ) in partner_fields
                if str(partner_contributor_id) == str(contributor_id)
            ]

            if not contributor_field_names:
                qs = qs.none()
                break

            qs = apply_partner_fields_or_filter(
                qs,
                contributor_field_names,
                partner_contributors,
            )
    else:
        field_names = list(
            {
                field_name
                for (
                    _partner_contributor_id,
                    field_name,
                ) in partner_fields
            }
        )
        if field_names:
            qs = apply_partner_fields_or_filter(
                qs,
                field_names,
                partner_contributors,
            )

    return qs
