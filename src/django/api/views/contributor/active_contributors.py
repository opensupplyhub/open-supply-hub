from ...models import Contributor, FacilityListItem, Source


def active_contributors():
    valid_sources = Source.objects.filter(
        is_active=True, is_public=True, create=True,
        facilitylistitem__status__in=FacilityListItem.COMPLETE_STATUSES)
    return Contributor.objects.filter(source__in=valid_sources).distinct()
