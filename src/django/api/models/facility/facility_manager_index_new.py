import re

from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.db.models import BooleanField, IntegerField, Q
from django.db.models.expressions import RawSQL

from api.facility_type_processing_type import get_facility_and_processing_type
from api.constants import FacilitiesQueryParams
from api.isic import parse_isic4_filter_values
from api.helpers.helpers import (
    clean,
    format_custom_text,)
from api.os_id import string_matches_os_id_format
from api.models.facility.partner_contributor_filter import (
    apply_partner_contributors_filter,
)


MIN_FREE_TEXT_FP_LENGTH = 3

FREE_TEXT_FP_ARRAY_MATCH = """
(
    EXISTS (
        SELECT 1 FROM unnest(facility_type) AS elem
        WHERE unaccent(elem) ~* unaccent(%s)
    )
    OR EXISTS (
        SELECT 1 FROM unnest(processing_type) AS elem
        WHERE unaccent(elem) ~* unaccent(%s)
    )
)
"""

FREE_TEXT_FP_TERM_SCORE = """
(
    CASE
        WHEN {array_match} THEN 2
        WHEN {array_match} THEN 1
        ELSE 0
    END
)
"""


def _classify_fp_filter_value(value):
    standard_type = get_facility_and_processing_type(value, ['Apparel'])
    if standard_type[0] is not None:
        return ('taxonomy', standard_type)

    trimmed = value.strip()
    if len(trimmed) >= MIN_FREE_TEXT_FP_LENGTH:
        return ('free_text', trimmed)

    return (None, None)


def _free_text_fp_terms(facility_types, processing_types):
    terms = []
    for value in [*(facility_types or []), *(processing_types or [])]:
        classification, data = _classify_fp_filter_value(value)
        if classification == 'free_text':
            terms.append(data)
    return terms


def _word_prefix_pattern(term):
    return rf'\m{re.escape(term)}'


def _whole_word_pattern(term):
    return rf'{_word_prefix_pattern(term)}\M'


def _build_fp_param_sql_parts(values, overlap_field, taxonomy_slot):
    taxonomy_values = []
    free_text_terms = []

    for value in values:
        classification, data = _classify_fp_filter_value(value)
        if classification == 'taxonomy':
            taxonomy_values.append(data[taxonomy_slot])
        elif classification == 'free_text':
            free_text_terms.append(data)

    parts = []
    params = []

    if taxonomy_values:
        parts.append(f'{overlap_field} && %s::varchar[]')
        params.append(taxonomy_values)

    for term in free_text_terms:
        parts.append(FREE_TEXT_FP_ARRAY_MATCH)
        pattern = _word_prefix_pattern(term)
        params.extend([pattern, pattern])

    return parts, params


def build_fp_match_sql(facility_types, processing_types):
    """
    Build a boolean SQL expression for facility/processing type filters.

    Taxonomy values use array overlap on the param's primary column.
    Unmatched values fall back to an accent-insensitive word-prefix search
    across both columns. Multiple values within one param are OR'd;
    facility_type and processing_type params are AND'd.
    """
    param_clauses = []
    all_params = []

    for values, overlap_field, taxonomy_slot in (
        (facility_types, 'facility_type', 2),
        (processing_types, 'processing_type', 3),
    ):
        if not values:
            continue

        parts, params = _build_fp_param_sql_parts(
            values,
            overlap_field,
            taxonomy_slot,
        )
        if parts:
            param_clauses.append('(' + ' OR '.join(parts) + ')')
            all_params.extend(params)
        else:
            # A supplied parameter whose values are all invalid must not
            # silently broaden the request to an unfiltered facility search.
            param_clauses.append('(FALSE)')

    if not param_clauses:
        return None, []

    return ' AND '.join(param_clauses), all_params


def build_fp_relevance_sql(facility_types, processing_types):
    """
    Score free-text facility/processing filters across both indexed arrays.

    Whole-word matches score 2 and word-prefix matches score 1. The highest
    score wins when multiple values or indexed array elements match.
    """
    score_parts = []
    params = []

    for term in _free_text_fp_terms(facility_types, processing_types):
        score_parts.append(
            FREE_TEXT_FP_TERM_SCORE.format(
                array_match=FREE_TEXT_FP_ARRAY_MATCH
            )
        )
        whole_word_pattern = _whole_word_pattern(term)
        word_prefix_pattern = _word_prefix_pattern(term)
        params.extend(
            [
                whole_word_pattern,
                whole_word_pattern,
                word_prefix_pattern,
                word_prefix_pattern,
            ]
        )

    if not score_parts:
        return None, []

    if len(score_parts) == 1:
        return score_parts[0], params

    return f"GREATEST({', '.join(score_parts)})", params


def annotate_facility_processing_match(
    queryset,
    facility_types,
    processing_types,
    annotation_name='_fp_match',
):
    sql, params = build_fp_match_sql(facility_types, processing_types)
    if not sql:
        return queryset, False

    return queryset.annotate(
        **{
            annotation_name: RawSQL(
                sql,
                params,
                output_field=BooleanField(),
            )
        }
    ), True


def annotate_facility_processing_relevance(
    queryset,
    facility_types,
    processing_types,
    annotation_name='_fp_relevance',
):
    sql, params = build_fp_relevance_sql(facility_types, processing_types)
    if not sql:
        return queryset, False

    return queryset.annotate(
        **{
            annotation_name: RawSQL(
                sql,
                params,
                output_field=IntegerField(),
            )
        }
    ), True


def build_isic_filter(parsed_isic_filters):
    if not parsed_isic_filters:
        return None

    isic_filter = Q()
    for field_name, code in parsed_isic_filters:
        isic_filter |= Q(**{f'{field_name}__overlap': [code]})
    return isic_filter


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

        combine_facility_processing_isic = params.get(
            FacilitiesQueryParams.COMBINE_FACILITY_PROCESSING_ISIC, '')

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

        isic_4_filters = params.getlist(FacilitiesQueryParams.ISIC_4)

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

        facilities_qs, has_fp_filter = annotate_facility_processing_match(
            facilities_qs,
            facility_types,
            processing_types,
        )
        parsed_isic_filters = parse_isic4_filter_values(isic_4_filters)
        isic_filter = build_isic_filter(parsed_isic_filters)

        if has_fp_filter and isic_filter:
            if combine_facility_processing_isic.upper() == 'AND':
                facilities_qs = facilities_qs.filter(
                    Q(_fp_match=True) & isic_filter
                )
            else:
                facilities_qs = facilities_qs.filter(
                    Q(_fp_match=True) | isic_filter
                )
        elif has_fp_filter:
            facilities_qs = facilities_qs.filter(_fp_match=True)
        elif isic_filter:
            facilities_qs = facilities_qs.filter(isic_filter)

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

        partner_contributors = params.getlist(
            FacilitiesQueryParams.PARTNER_CONTRIBUTOR
        )

        facilities_qs = apply_partner_contributors_filter(
            facilities_qs,
            partner_contributors,
        )

        return facilities_qs
