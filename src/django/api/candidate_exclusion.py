"""
Candidate-row exclusion for querysets the ``Facility`` default manager
cannot reach.

``Facility.objects`` hides candidates (``is_candidate=True``, OSDEV-3380),
but a filter that JOINs to Facility from another model never applies the
target model's manager, so ``FacilityMatch.objects.filter(...)`` still
returns matches that point at a candidate. Code that must not carry
candidate data forward, such as the one-way RBA database sync, filters
the join itself through this helper (OSDEV-3378).

Kept out of ``sync_databases`` so it can be unit-tested without importing
the synchronizer.
"""


def exclude_candidate_rows(queryset, candidate_lookup):
    """
    Drop candidate facilities, or rows whose Facility FK points at one.

    Arguments:
    queryset -- Any queryset. Passing it through a manager that already
                excludes candidates is harmless; the filter is then
                redundant rather than wrong.
    candidate_lookup -- The ORM path to the candidate flag from the
                queryset's model: ``'is_candidate'`` on Facility itself,
                ``'facility__is_candidate'`` on a model with a ``facility``
                FK. ``None`` leaves the queryset untouched, for models that
                have no path to Facility.

    Rows whose FK is NULL are kept: ``exclude(facility__is_candidate=True)``
    compiles to a null-safe anti-join, so an unmatched FacilityListItem
    still syncs.
    """
    if candidate_lookup is None:
        return queryset
    return queryset.exclude(**{candidate_lookup: True})
