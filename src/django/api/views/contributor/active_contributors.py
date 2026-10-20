from django.db.models import Q

from ...models import Contributor, FacilityListItem, Source


def active_contributors():
    # A contributor is active through at least one complete list item
    # whose facility is visible. An item attached to a candidate facility
    # (Earth Genome ingest: SINGLE source, MATCHED item, is_candidate row)
    # is not shown anywhere, so it must not list the contributor in
    # GET /api/contributors/ or bump /api/contributors/active_count/
    # (OSDEV-3376). FK joins never apply Facility.objects, hence the
    # explicit is_candidate test. All conditions sit in one filter() call
    # so they apply to the same joined item; a NULL facility is tolerated
    # because legacy rows and fixtures have complete items without one.
    valid_sources = Source.objects.filter(
        Q(facilitylistitem__facility__isnull=True)
        | Q(facilitylistitem__facility__is_candidate=False),
        is_active=True, is_public=True, create=True,
        facilitylistitem__status__in=FacilityListItem.COMPLETE_STATUSES,
    )
    return Contributor.objects.filter(source__in=valid_sources).distinct()
