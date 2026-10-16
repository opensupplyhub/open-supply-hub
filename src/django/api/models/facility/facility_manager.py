from unidecode import unidecode

from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.db.models import Q

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


class FacilityManager(models.Manager):
    """
    Default manager for Facility. Excludes candidate rows.

    Candidates (``is_candidate=True``) are unconfirmed detections from an
    automated source. Every existing ORM code path was written before they
    existed, so the default manager hides them and access to them has to be
    an explicit ``Facility.including_candidates`` call.

    What this filter does and does not cover (Django 5.2 semantics, pinned
    by ``api/tests/test_facility_default_manager.py``):

    * ``Facility.objects`` is declared first on the model, so it is
      ``_default_manager``. That is what ``get_object_or_404``, the admin
      changelist, ``dumpdata`` and DRF's auto-generated ``ModelSerializer``
      FK fields use, so all of those exclude candidates.
    * ``_base_manager`` is left as Django's plain ``Manager``. Forward FK
      access (``claim.facility``), reverse one-to-one access
      (``list_item.created_facility``), ``refresh_from_db()`` and the
      UPDATE issued by ``save()`` go through it, so they still reach a
      candidate. Do not set ``Meta.base_manager_name`` to this manager: it
      would make a claim on a candidate raise ``RelatedObjectDoesNotExist``
      and break saving candidates.
    * Filters that JOIN to Facility from another model
      (``FacilityClaim.objects.filter(facility__name=...)``) never apply the
      target model's manager, so they include candidates. Code that must
      exclude them has to filter ``facility__is_candidate=False`` itself.
    * Reverse FK managers on a Facility instance
      (``facility.facilitymatch_set``) belong to the related model and are
      unaffected.
    * ``ForeignKey.validate()``, which ``full_clean()`` runs, uses
      ``_base_manager``, so a claim or match that points at a candidate
      still validates. ModelForm and admin FK *form fields* build their
      choices from ``_default_manager`` instead, so an admin change form on
      such a claim fails with "select a valid choice" (admin handling is
      OSDEV-3379).
    * ``validate_unique()`` and ``validate_constraints()`` also go through
      ``_default_manager``, so form-level validation cannot see a clash
      with a candidate's ``id`` or ``(source, external_id)``. The database
      constraints still reject it, but as an ``IntegrityError`` rather
      than a field error.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_candidate=False)

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

        facility_processing_filter = FacilityProcessingFilter.from_result(
            FacilityProcessingQuery(params).parse()
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
                    else free_text_query)
                custom_text_search_filter = Q(
                    custom_text_search__unaccent__contains=custom_text
                )

                facilities_qs = facilities_qs \
                    .filter(name_filter |
                            Q(id=free_text_query) |
                            custom_text_search_filter)
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
            unidecode_name = unidecode(native_language_name)
            facilities_qs = facilities_qs.filter(
                native_language_name__icontains=unidecode_name
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

        facility_ids = facilities_qs.values_list('id', flat=True)

        from .facility import Facility
        facilities_qs = Facility.objects.filter(id__in=facility_ids)

        return facilities_qs


class FacilityIncludingCandidatesManager(models.Manager):
    """
    Opt-in manager that returns every Facility row, candidates included.

    Use it only where candidates are the point: ingest and idempotency
    checks on ``(source, external_id)``, OS ID collision checks, candidate
    moderation and promotion. Anything user-facing should stay on
    ``Facility.objects``.
    """
