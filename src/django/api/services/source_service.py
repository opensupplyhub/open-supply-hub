import logging
from typing import TYPE_CHECKING

from api.models.extended_field import ExtendedField

if TYPE_CHECKING:
    from api.models.source import Source


log = logging.getLogger(__name__)


class SourceService:
    """Operations that span a Source and the records derived from it."""

    @staticmethod
    def reassign_extended_fields(source: 'Source') -> int:
        """
        Re-attribute every ExtendedField that originated from this source's
        facility list items to the source's current contributor.

        Covers both LIST and SINGLE sources, because the relation is
        resolved through `FacilityListItem.source` rather than through
        `Source.facility_list` (which is NULL for SINGLE sources).

        Extended fields created from a FacilityClaim have no
        `facility_list_item` and are intentionally left untouched.

        Returns the number of rows updated.
        """
        if source.contributor_id is None:
            log.warning(
                'Source %s has no contributor; skipping extended field '
                'reassignment.',
                source.pk,
            )
            return 0

        # A queryset update is used deliberately: it lets the existing
        # api_extendedfield database trigger refresh the affected
        # FacilityIndex rows, and it leaves `updated_at` alone so the
        # publicly displayed contribution date is preserved. It creates no
        # simple_history rows.
        updated = ExtendedField.objects.filter(
            facility_list_item__source=source,
        ).exclude(
            contributor_id=source.contributor_id,
        ).update(contributor_id=source.contributor_id)

        if updated:
            log.info(
                'Reassigned %s extended field(s) of source %s to '
                'contributor %s.',
                updated,
                source.pk,
                source.contributor_id,
            )

        return updated
