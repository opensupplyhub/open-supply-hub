from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.db.models import Exists, OuterRef, Q

from api.constants import FacilitiesQueryParams
from api.helpers.helpers import (
    clean,
    format_custom_text,)
from api.os_id import string_matches_os_id_format
from api.models.facility.partner_contributor_filter import (
    apply_partner_contributors_filter,
)
from api.services.facility_processing_filter import FacilityProcessingFilter
from api.services.facility_processing_query import FacilityProcessingQuery


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

        facilities_qs, has_fp_filter = (
            facility_processing_filter.annotate_match(facilities_qs)
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
