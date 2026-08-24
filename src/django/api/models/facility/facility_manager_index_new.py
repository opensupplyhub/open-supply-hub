import re

from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.db.models import BooleanField, IntegerField, Q
from django.db.models.expressions import RawSQL

from api.facility_type_processing_type import get_facility_and_processing_type
from api.constants import FacilitiesQueryParams
from api.facility_processing_query import parse_facility_processing_query
from api.helpers.helpers import (
    clean,
    format_custom_text,)
from api.os_id import string_matches_os_id_format
from api.models.facility.partner_contributor_filter import (
    apply_partner_contributors_filter,
)


# Also the shortest term a trigram index can narrow, so no free-text filter
# falls back to scanning api_facilityindex.
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

# A word-prefix regex over an unnested array cannot use an index, so the
# trigram index on facility_processing_search_text() gathers the candidate
# locations and the regex rechecks only those. A substring match returns a
# superset of a word-prefix match, so the pair selects exactly what the regex
# alone would. The pattern is normalized by the same functions the indexed
# expression uses, because normalizing it in Python would risk dropping rows
# whose accents unidecode and unaccent() disagree about.
FREE_TEXT_FP_INDEXED_MATCH = """
(
    facility_processing_search_text(facility_type, processing_type)
        LIKE '%%' || immutable_unaccent(lower(%s)) || '%%'
    AND {array_match}
)
"""

# Both tiers scored in one pass over the two arrays. Testing them as four
# separate EXISTS would run the same regex over the same elements twice.
FREE_TEXT_FP_TERM_SCORE = """
(
    SELECT COALESCE(MAX(
        CASE
            WHEN unaccent(elem) ~* unaccent(%s) THEN 2
            WHEN unaccent(elem) ~* unaccent(%s) THEN 1
            ELSE 0
        END
    ), 0)
    FROM unnest(
        COALESCE(facility_type, '{}'::varchar[])
        || COALESCE(processing_type, '{}'::varchar[])
    ) AS elem
)
"""

_LIKE_SPECIAL_CHARACTER_PATTERN = re.compile(r'([\\%_])')


def _classify_fp_filter_value(value):
    trimmed = value.strip()
    if not trimmed:
        return (None, None)

    standard_type = get_facility_and_processing_type(
        value,
        ['Apparel'],
        allow_fuzzy=len(trimmed) >= MIN_FREE_TEXT_FP_LENGTH,
    )
    if standard_type[0] is not None:
        return ('taxonomy', standard_type)

    if len(trimmed) >= MIN_FREE_TEXT_FP_LENGTH:
        return ('free_text', trimmed)

    return (None, None)


def _free_text_fp_terms(
    facility_types,
    processing_types,
    exact_processing_types=None,
):
    terms = []
    exact_processing_type_identities = {
        value.lower() for value in (exact_processing_types or [])
    }
    values = [
        *(facility_types or []),
        *(
            value for value in (processing_types or [])
            if value.lower() not in exact_processing_type_identities
        ),
    ]
    for value in values:
        classification, data = _classify_fp_filter_value(value)
        if classification == 'free_text':
            terms.append(data)
    return terms


def _word_prefix_pattern(term):
    return rf'\m{re.escape(term)}'


def _whole_word_pattern(term):
    return rf'{_word_prefix_pattern(term)}\M'


def _like_term(term):
    """Escape a term for use inside the trigram containment pattern."""
    return _LIKE_SPECIAL_CHARACTER_PATTERN.sub(r'\\\1', term)


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
        parts.append(
            FREE_TEXT_FP_INDEXED_MATCH.format(
                array_match=FREE_TEXT_FP_ARRAY_MATCH
            )
        )
        pattern = _word_prefix_pattern(term)
        params.extend([_like_term(term), pattern, pattern])

    return parts, params


def _append_fp_param_clause(
    param_clauses,
    all_params,
    values,
    overlap_field,
    taxonomy_slot,
):
    if not values:
        return

    parts, params = _build_fp_param_sql_parts(
        values,
        overlap_field,
        taxonomy_slot,
    )
    # A supplied parameter whose values are all invalid must not silently
    # broaden the request to an unfiltered facility search.
    param_clauses.append(
        '(' + ' OR '.join(parts) + ')' if parts else '(FALSE)'
    )
    all_params.extend(params)


def _append_exact_processing_clause(
    param_clauses,
    all_params,
    exact_processing_types,
    legacy_processing_types,
):
    if not exact_processing_types:
        return

    # Overlapping the lower-cased array matches the expression index on it.
    # Lower-casing each element inside an unnest would read every row of
    # api_facilityindex instead.
    exact_clause = 'lower_varchar_array(processing_type) && %s::text[]'
    if param_clauses and legacy_processing_types:
        param_clauses[-1] = f'({param_clauses[-1]} OR {exact_clause})'
    else:
        param_clauses.append(f'({exact_clause})')
    all_params.append([value.lower() for value in exact_processing_types])


def build_fp_match_sql(
    facility_types,
    processing_types,
    exact_processing_types=None,
):
    """
    Build a boolean SQL expression for facility/processing type filters.

    Taxonomy values use array overlap on the param's primary column.
    Unmatched values fall back to an accent-insensitive word-prefix search
    across both columns. Multiple values within one param are OR'd;
    facility_type and processing_type params are AND'd.
    """
    param_clauses = []
    all_params = []

    processing_type_identities = {
        value.lower() for value in (processing_types or [])
    }
    exact_processing_types = [
        value for value in (exact_processing_types or [])
        if value.lower() in processing_type_identities
    ]
    exact_processing_type_identities = {
        value.lower() for value in exact_processing_types
    }
    legacy_processing_types = [
        value for value in (processing_types or [])
        if value.lower() not in exact_processing_type_identities
    ]

    for values, overlap_field, taxonomy_slot in (
        (facility_types, 'facility_type', 2),
        (legacy_processing_types, 'processing_type', 3),
    ):
        _append_fp_param_clause(
            param_clauses,
            all_params,
            values,
            overlap_field,
            taxonomy_slot,
        )

    _append_exact_processing_clause(
        param_clauses,
        all_params,
        exact_processing_types,
        legacy_processing_types,
    )

    if not param_clauses:
        return None, []

    return ' AND '.join(param_clauses), all_params


def build_fp_relevance_sql(
    facility_types,
    processing_types,
    exact_processing_types=None,
):
    """
    Score free-text facility/processing filters across both indexed arrays.

    Whole-word matches score 2 and word-prefix matches score 1. The highest
    score wins when multiple values or indexed array elements match.
    """
    score_parts = []
    params = []

    for term in _free_text_fp_terms(
        facility_types,
        processing_types,
        exact_processing_types,
    ):
        score_parts.append(FREE_TEXT_FP_TERM_SCORE)
        params.extend(
            [
                _whole_word_pattern(term),
                _word_prefix_pattern(term),
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
    exact_processing_types=None,
    annotation_name='_fp_match',
):
    sql, params = build_fp_match_sql(
        facility_types,
        processing_types,
        exact_processing_types,
    )
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
    exact_processing_types=None,
    annotation_name='_fp_relevance',
):
    sql, params = build_fp_relevance_sql(
        facility_types,
        processing_types,
        exact_processing_types,
    )
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

        (
            facility_types,
            processing_types,
            exact_processing_types,
        ) = parse_facility_processing_query(
            params
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

        facilities_qs, has_fp_filter = annotate_facility_processing_match(
            facilities_qs,
            facility_types,
            processing_types,
            exact_processing_types,
        )
        if has_fp_filter:
            facilities_qs = facilities_qs.filter(_fp_match=True)

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
