from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.db.models import Exists, OuterRef, Q

from api.constants import FacilitiesQueryParams
from api.isic import build_isic_filter, parse_isic_filter_values
from api.helpers.helpers import (
    clean,
    format_custom_text,)
from api.os_id import string_matches_os_id_format
# Imported for the side effect of registering the immutable_unaccent
# lookup used by build_name_token_filter.
from api.models.facility.facility_name_search import (  # noqa: F401
    ImmutableUnaccentTransform,
)
from api.models.facility.partner_contributor_filter import (
    apply_partner_contributors_filter,
)
from api.services.facility_processing_filter import FacilityProcessingFilter
from api.services.facility_processing_query import FacilityProcessingQuery


# Unit numbers are written both ways in facility names, so a numeral
# token matches either spelling. 1/I is deliberately absent: a '%I%'
# substring matches nearly every name. See OSDEV-3907.
ARABIC_TO_ROMAN = {
    '2': 'II', '3': 'III', '4': 'IV', '5': 'V', '6': 'VI', '7': 'VII',
    '8': 'VIII', '9': 'IX', '10': 'X', '11': 'XI', '12': 'XII',
    '13': 'XIII', '14': 'XIV', '15': 'XV', '16': 'XVI', '17': 'XVII',
    '18': 'XVIII', '19': 'XIX', '20': 'XX',
}
ROMAN_TO_ARABIC = {
    roman: arabic for arabic, roman in ARABIC_TO_ROMAN.items()
}


def numeral_counterpart(token):
    """The other spelling of a unit number, or None."""
    upper = token.upper()
    return ARABIC_TO_ROMAN.get(upper) or ROMAN_TO_ARABIC.get(upper)


def build_name_token_filter(text):
    """
    Match every whitespace-separated word in ``text`` against ``name``.

    A single ``ILIKE`` on the whole typed string required the words to
    appear in that order with nothing between them, so "Interloop Hosiery"
    missed "Interloop Limited (Hosiery Division I)". See OSDEV-3790.

    Folds accents through ``immutable_unaccent`` rather than Django's
    ``__unaccent`` so the predicate matches the trigram index of 0269; the
    two spell the same comparison, but only this one can be indexed
    (OSDEV-3793).

    A numeral token matches its roman or arabic counterpart as well, so
    "Unit IV" finds "Unit 4" and vice versa (OSDEV-3907).
    """
    tokens = text.split()
    if not tokens:
        return Q(name__immutable_unaccent__icontains=text)

    # A GIN trigram index cannot extract a single trigram from a string
    # shorter than three characters, so for a query with no longer token
    # the index matches every row and Postgres rechecks all of them: `07`
    # measured 36.9 s against 3.6 s for the sequential scan it replaced,
    # and 89.8 s through the full API, on an endpoint needing no
    # authentication.
    #
    # Django's own `__unaccent` emits the STABLE `unaccent()`, which is
    # exactly the same comparison but cannot be indexed, so it steers the
    # planner back to the scan this query wants. Results are identical
    # either way; only the plan differs. See OSDEV-3793.
    minimum = FacilityProcessingFilter.MIN_FREE_TEXT_LENGTH
    indexable = any(len(token) >= minimum for token in tokens)
    lookup = (
        'name__immutable_unaccent__icontains'
        if indexable
        else 'name__unaccent__icontains'
    )

    has_unit_token = any(token.lower() == 'unit' for token in tokens)

    name_filter = Q()
    for token in tokens:
        token_filter = Q(**{lookup: token})
        counterpart = numeral_counterpart(token)
        if counterpart is not None:
            if counterpart.isdigit():
                token_filter |= Q(**{lookup: counterpart})
            else:
                # A roman counterpart appears inside ordinary words ("IV"
                # in "Private"), so the added branch matches whole words
                # only. The typed token keeps its substring semantics.
                token_filter |= Q(
                    name__iregex=r'\m{}\M'.format(counterpart)
                )
        elif token == '1' and has_unit_token:
            # 1 has no general roman twin: standalone "I" is the India
            # marker in thousands of names ("Texport Syndicate (I) Ltd").
            # But 62 production names write unit one as "Unit I", so when
            # the query says "unit 1" the added branch matches an I only
            # directly after "unit" in the name, which the India marker
            # never is. See OSDEV-3907.
            token_filter |= Q(
                name__iregex=r'\munit[^a-z0-9]{0,4}i\M'
            )
        name_filter &= token_filter
    return name_filter


# strict_word_similarity needs enough trigrams to score a word; shorter
# tokens stay exact, so a typo in them is not rescued.
FUZZY_MIN_TOKEN_LENGTH = 4

# Each fuzzy token costs one trigram index scan (~150 ms over 2.5M rows)
# on an endpoint that needs no authentication, and only zero-result
# queries get here. A person correcting a typo types a handful of words;
# a query with more fuzzy-eligible tokens than this stays at zero results
# rather than paying an unbounded AND of index scans.
FUZZY_MAX_TOKENS = 6


def build_fuzzy_name_filter(text):
    """
    The zero-result fallback: match each word approximately.

    Each token long enough to carry trigrams must be strictly word-similar
    to the name (the indexed ``<<%`` operator at the database default
    threshold); shorter tokens keep their exact substring match. Returns
    None when no token is long enough to match approximately — so a purely
    short query never takes the fallback — or when more than
    ``FUZZY_MAX_TOKENS`` are eligible, which bounds the cost of a
    deliberately long no-match query. See OSDEV-3906.
    """
    tokens = text.split()
    fuzzy_eligible = sum(
        1 for token in tokens if len(token) >= FUZZY_MIN_TOKEN_LENGTH
    )
    if fuzzy_eligible == 0 or fuzzy_eligible > FUZZY_MAX_TOKENS:
        return None

    name_filter = Q()
    for token in tokens:
        if len(token) >= FUZZY_MIN_TOKEN_LENGTH:
            name_filter &= Q(
                name__immutable_unaccent__strict_word_similar=token
            )
        else:
            name_filter &= Q(name__immutable_unaccent__icontains=token)
    return name_filter


class FacilityIndexNewManager(models.Manager):
    def without_candidates(self):
        """
        FacilityIndex rows whose Facility is not a candidate.

        ``api_facilityindex`` has no ``is_candidate`` column, so the
        ``Facility.objects`` default manager (OSDEV-3380) cannot protect
        surfaces that read the index directly: ``/api/facilities/``,
        ``/api/facilities-downloads/``, the vector tiles and the CSV
        export. The index trigger is being taught to skip candidate rows
        (OSDEV-3243); this is the Django-side guard for rows that reach the
        index anyway. It is a ``NOT EXISTS`` against the partial
        ``api_facility_is_candidate_idx`` index, so it costs one probe of
        a small set per row rather than a join against ``api_facility``.

        Deliberately not folded into ``get_queryset()``: the details view
        (``FacilityIndex.objects.get(pk=...)``) must keep resolving a
        candidate so OSDEV-3249 can render it labeled, and the
        processing/merge code looks up index rows by id after writes.
        """
        from .facility import Facility

        return self.get_queryset().filter(
            ~Exists(
                Facility.including_candidates.filter(
                    id=OuterRef('id'),
                    is_candidate=True,
                )
            )
        )

    def filter_by_query_params(
        self,
        params,
        facility_processing_filter=None,
    ):
        """
        Create a Facility queryset filtered by a list of request query params.

        Arguments:
        self (queryset) -- A queryset on the Facility model
        params (dict) -- Request query parameters whose potential choices are
                        enumerated in `api.constants.FacilitiesQueryParams`.
        facility_processing_filter (FacilityProcessingFilter) -- Optional
                        preclassified filter reused by callers that also
                        annotate relevance.

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

        if facility_processing_filter is None:
            facility_processing_filter = (
                FacilityProcessingFilter.from_result(
                    FacilityProcessingQuery(params).parse()
                )
            )

        product_types = params.getlist(FacilitiesQueryParams.PRODUCT_TYPE)

        number_of_workers = params.getlist(
            FacilitiesQueryParams.NUMBER_OF_WORKERS
        )

        native_language_name = params.get(
            FacilitiesQueryParams.NATIVE_LANGUAGE_NAME, None
        )

        sectors = params.getlist(FacilitiesQueryParams.SECTOR)

        isic_params = {
            '4': params.getlist(FacilitiesQueryParams.ISIC_4),
            '5': params.getlist(FacilitiesQueryParams.ISIC_5),
        }

        from .facility_index import FacilityIndex
        # Not ``self``: test_facility_search_accented_characters calls this
        # method unbound with the TestCase as ``self``.
        facilities_qs = FacilityIndex.objects.without_candidates()

        if id is None and string_matches_os_id_format(free_text_query):
            id = free_text_query
            free_text_query = None

        if id is not None:
            from .facility_alias import FacilityAlias

            try:
                # A NOT_A_FACILITY tombstone has facility_id None, so a
                # retired OS ID rewrites to id=None and matches nothing
                # rather than redirecting (OSDEV-3246).
                id = FacilityAlias.objects.get(pk=id).facility_id
            except FacilityAlias.DoesNotExist:
                pass

            facilities_qs = facilities_qs.filter(id=id)

        if free_text_query is not None:
            name_filter = build_name_token_filter(free_text_query)
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
                exact_qs = facilities_qs \
                    .filter(name_filter | Q(id=free_text_query))
                # Only when the typed words match no name at all does the
                # search retry approximately, so established queries gain
                # no fuzzy noise. The probe is answered by the trigram
                # index; later filters (country, sector, ...) cannot
                # rescue a name that matches nothing, so probing before
                # they apply is sound. See OSDEV-3906.
                if not exact_qs.exists():
                    fuzzy_filter = build_fuzzy_name_filter(free_text_query)
                    if fuzzy_filter is not None:
                        exact_qs = facilities_qs.filter(fuzzy_filter)
                facilities_qs = exact_qs

        # `name` is deprecated in favor of `q`. We keep `name` available for
        # backward compatibility, matching per word as `q` does: both are
        # public parameters, so the same query must not find results under
        # one and nothing under the other.
        if name is not None:
            name_filter = build_name_token_filter(name)
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

        facilities_qs, has_fp_filter = (
            facility_processing_filter.annotate_match(facilities_qs)
        )
        if has_fp_filter:
            facilities_qs = facilities_qs.filter(_fp_match=True)

        isic_filter = build_isic_filter({
            revision: parse_isic_filter_values(values)
            for revision, values in isic_params.items()
        })
        if isic_filter:
            facilities_qs = facilities_qs.filter(isic_filter)
        elif any(any(values) for values in isic_params.values()):
            # ISIC was asked for but nothing in it is a level:code value.
            # Ignoring it would present every location as a match
            # (OSDEV-3340 AC4).
            facilities_qs = facilities_qs.none()

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
