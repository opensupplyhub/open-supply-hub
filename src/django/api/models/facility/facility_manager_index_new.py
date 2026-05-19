from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.db.models import Q, Subquery

from api.facility_type_processing_type import get_facility_and_processing_type
from api.constants import FacilitiesQueryParams
from api.helpers.helpers import (
    clean,
    format_custom_text,)
from api.os_id import string_matches_os_id_format

SYSTEM_PARTNER_FIELD_NAMES = frozenset({'wage_indicator', 'mit_living_wage'})


def _spotlight_q(name):
    """
    Return a Q object filtering FacilityIndex rows that have data
    for the given partner field name.

    System fields (wage_indicator, mit_living_wage) are never stored in
    extended_fields and require country-code-based filters instead.
    Regular fields use the JSONB containment operator on extended_fields.
    """
    if name == 'wage_indicator':
        from api.models.wage_indicator_country_data import WageIndicatorCountryData
        return Q(
            country_code__in=Subquery(
                WageIndicatorCountryData.objects.values('country_code')
            )
        )
    if name == 'mit_living_wage':
        return Q(country_code__in=['US', 'PR', 'VI'])
    return Q(extended_fields__contains=[{"field_name": name}])


def _apply_partner_fields_or_filter(qs, field_names):
    """
    Return a queryset filtered to facilities that have data from at least
    one of the given partner field names (OR semantics).

    extended_fields is ArrayField(JSONField), so partial JSON matching via
    __contains does not work — array containment requires exact element
    equality. Regular fields are handled with a correlated unnest() subquery.
    System fields use country-code lookups via standard Q objects.
    All conditions are combined with OR in a single extra(where=...) clause.
    """
    where_parts = []
    params = []

    regular = [n for n in field_names if n not in SYSTEM_PARTNER_FIELD_NAMES]
    if regular:
        where_parts.append(
            "EXISTS ("
            "  SELECT 1 FROM unnest(extended_fields) AS ef"
            "  WHERE ef->>'field_name' = ANY(%s)"
            ")"
        )
        params.append(regular)

    if 'wage_indicator' in field_names:
        where_parts.append(
            "country_code IN ("
            "  SELECT country_code FROM api_wageindicatorcountrydata"
            ")"
        )

    if 'mit_living_wage' in field_names:
        where_parts.append("country_code IN ('US', 'PR', 'VI')")

    if not where_parts:
        return qs

    or_clause = ' OR '.join(f'({part})' for part in where_parts)
    return qs.extra(where=[f'({or_clause})'], params=params)


class FacilityIndexNewManager(models.Manager):
    def filter_by_query_params(self, params):
        """
        Create a Facility queryset filtered by a list of request query params.

        Arguments:
        self (queryset) -- A queryset on the Facility model
        params (dict) -- Request query parameters whose potential choices are
                        enumerated in `api.constants.FacilitiesQueryParams`.

        Returns:
        A queryset on the Facility model
        """

        id = params.get(FacilitiesQueryParams.ID, None)

        free_text_query = params.get(FacilitiesQueryParams.Q, None)

        name = params.get(FacilitiesQueryParams.NAME, None)

        contributors = params.getlist(FacilitiesQueryParams.CONTRIBUTORS)

        lists = params.getlist(FacilitiesQueryParams.LISTS)

        contributor_types = params \
            .getlist(FacilitiesQueryParams.CONTRIBUTOR_TYPES)

        countries = params.getlist(FacilitiesQueryParams.COUNTRIES)

        combine_contributors = params.get(
            FacilitiesQueryParams.COMBINE_CONTRIBUTORS, '')

        boundary = params.get(
            FacilitiesQueryParams.BOUNDARY, None
        )

        embed = params.get(
            FacilitiesQueryParams.EMBED, None
        )

        parent_companies = params.getlist(FacilitiesQueryParams.PARENT_COMPANY)

        facility_types = params.getlist(FacilitiesQueryParams.FACILITY_TYPE)

        processing_types = params.getlist(
            FacilitiesQueryParams.PROCESSING_TYPE
        )

        product_types = params.getlist(FacilitiesQueryParams.PRODUCT_TYPE)

        number_of_workers = params.getlist(
            FacilitiesQueryParams.NUMBER_OF_WORKERS
        )

        native_language_name = params.get(
            FacilitiesQueryParams.NATIVE_LANGUAGE_NAME, None
        )

        sectors = params.getlist(FacilitiesQueryParams.SECTOR)

        from .facility_index import FacilityIndex
        facilities_qs = FacilityIndex.objects.all()

        if id is None and string_matches_os_id_format(free_text_query):
            id = free_text_query
            free_text_query = None

        if id is not None:
            from .facility_alias import FacilityAlias

            try:
                id = FacilityAlias.objects.get(pk=id).facility_id
            except FacilityAlias.DoesNotExist:
                pass

            facilities_qs = facilities_qs.filter(id=id)

        if free_text_query is not None:
            name_filter = Q(name__unaccent__icontains=free_text_query)
            if embed is not None:
                custom_text = (
                    format_custom_text(contributors[0], free_text_query)
                    if contributors
                    else free_text_query
                )
                custom_text_search_filter = Q(
                    custom_text_search__unaccent__contains=custom_text
                )

                facilities_qs = facilities_qs \
                    .filter(name_filter |
                            Q(id=free_text_query) |
                            custom_text_search_filter
                            )
            else:
                facilities_qs = facilities_qs \
                    .filter(name_filter | Q(id=free_text_query))

        # `name` is deprecated in favor of `q`. We keep `name` available for
        # backward compatibility.
        if name is not None:
            name_filter = Q(name__unaccent__icontains=name)
            facilities_qs = facilities_qs.filter(name_filter | Q(id=name))

        if countries is not None and len(countries):
            facilities_qs = facilities_qs \
                .filter(country_code__in=countries)

        if len(contributor_types):
            facilities_qs = facilities_qs \
                .filter(contrib_types__overlap=contributor_types)

        if len(contributors):
            if combine_contributors.upper() == 'AND':
                facilities_qs = facilities_qs.filter(
                    contributors_id__contains=contributors
                )
            else:
                facilities_qs = facilities_qs.filter(
                    contributors_id__overlap=contributors
                )

        if len(lists):
            facilities_qs = facilities_qs.filter(lists__overlap=lists)

        if boundary is not None:
            facilities_qs = facilities_qs.filter(
                location__within=GEOSGeometry(boundary)
            )

        if len(parent_companies):
            parent_company_id = []
            parent_company_name = []
            for parent_company in parent_companies:
                if parent_company.isnumeric():
                    parent_company_id.append(parent_company)
                else:
                    parent_company_name.append(parent_company)
            if len(parent_company_id) or len(parent_company_name):
                facilities_qs = facilities_qs.filter(
                    Q(parent_company_id__overlap=parent_company_id) |
                    Q(parent_company_name__overlap=parent_company_name)
                )

        if len(facility_types):
            standard_facility_types = []
            for facility_type in facility_types:
                standard_type = get_facility_and_processing_type(
                    facility_type, ['Apparel']
                )
                if standard_type[0] is not None:
                    standard_facility_types.append(standard_type[2])
            facilities_qs = facilities_qs.filter(
                facility_type__overlap=standard_facility_types
            )

        if len(processing_types):
            standard_processing_types = []
            for processing_type in processing_types:
                standard_type = get_facility_and_processing_type(
                    processing_type, ['Apparel']
                )
                if standard_type[0] is not None:
                    standard_processing_types.append(standard_type[3])
            facilities_qs = facilities_qs.filter(
                processing_type__overlap=standard_processing_types
            )

        if len(product_types):
            clean_product_types = []
            for product_type in product_types:
                clean_product_types.append(clean(product_type))
            facilities_qs = facilities_qs.filter(
                product_type__overlap=clean_product_types
            )

        if len(number_of_workers):
            facilities_qs = facilities_qs.filter(
                number_of_workers__overlap=number_of_workers
            )

        if native_language_name is not None:
            facilities_qs = facilities_qs.filter(
                native_language_name__icontains=native_language_name
            )

        if len(sectors):
            facilities_qs = facilities_qs.filter(
                sector__overlap=sectors
            )

        partner_field_groups = params.getlist(
            FacilitiesQueryParams.PARTNER_FIELD_GROUP
        )
        partner_fields = params.getlist(FacilitiesQueryParams.PARTNER_FIELD)

        if partner_field_groups or partner_fields:
            from api.models.partner_field import PartnerField

            # AC5 / mixed: group-level OR constraints (one per selected group).
            # Each group is applied as an independent AND constraint — any
            # facility must satisfy every selected group, but within a single
            # group any partner match is sufficient.
            for group_id in partner_field_groups:
                group_field_names = list(
                    PartnerField.objects.filter(
                        group_id=group_id, active=True
                    ).values_list('name', flat=True)
                )
                if group_field_names:
                    group_q = Q()
                    for field_name in group_field_names:
                        group_q |= _spotlight_q(field_name)
                    facilities_qs = facilities_qs.filter(group_q)

            # AC4 / mixed: individual partner AND constraints.
            # Each chained .filter() call enforces an independent AND condition.
            for field_name in partner_fields:
                facilities_qs = facilities_qs.filter(_spotlight_q(field_name))

        partner_contributors = params.getlist(
            FacilitiesQueryParams.PARTNER_CONTRIBUTOR
        )

        if partner_contributors:
            from api.models.partner_field import PartnerField

            field_names = list(
                PartnerField.objects.filter(
                    contributor__id__in=partner_contributors,
                    active=True,
                ).values_list('name', flat=True).distinct()
            )

            if field_names:
                facilities_qs = _apply_partner_fields_or_filter(
                    facilities_qs, field_names
                )

        return facilities_qs
