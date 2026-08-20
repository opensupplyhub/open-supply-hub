import logging
from typing import TYPE_CHECKING

from django.db import transaction

from api.models.extended_field import ExtendedField

if TYPE_CHECKING:
    from api.models.source import Source


log = logging.getLogger(__name__)

# Rows re-attributed per committed chunk. Every updated row fires the
# api_extendedfield trigger, which rebuilds the FacilityIndex summary for
# that row's location, so chunks are kept small enough that no single
# transaction holds locks on api_extendedfield or FacilityIndex rows for
# long.
REASSIGNMENT_CHUNK_SIZE = 500


class SourceService:
    """Operations that span a Source and the records derived from it."""

    @staticmethod
    def reassign_extended_fields(source: 'Source') -> int:
        """
        Re-attribute every ExtendedField that originated from this source's
        facility list items to the source's current contributor, in
        separately committed chunks.

        Chunking trades atomicity for bounded lock time: the source row
        and its extended fields are not updated in one transaction, and an
        interruption leaves the completed chunks committed. That is safe
        because updated rows stop matching the pending queryset, so the
        next call (a re-save, or the backfill_extended_field_contributors
        command) picks up exactly where the interrupted run stopped.

        Must be called OUTSIDE any enclosing transaction (Source.save()
        defers it with transaction.on_commit); inside one, the per-chunk
        commits would silently degrade to savepoints of a single large
        transaction.

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

        pending = ExtendedField.objects.filter(
            facility_list_item__source=source,
        ).exclude(
            contributor_id=source.contributor_id,
        )

        total = 0
        while True:
            chunk_ids = list(
                pending
                .order_by('id')
                .values_list('id', flat=True)[:REASSIGNMENT_CHUNK_SIZE]
            )
            if not chunk_ids:
                break

            # A queryset update is used deliberately: it lets the existing
            # api_extendedfield database trigger refresh the affected
            # FacilityIndex rows, and it leaves `updated_at` alone so the
            # publicly displayed contribution date is preserved. It
            # creates no simple_history rows.
            with transaction.atomic():
                total += ExtendedField.objects.filter(
                    id__in=chunk_ids,
                ).update(contributor_id=source.contributor_id)

        if total:
            log.info(
                'Reassigned %s extended field(s) of source %s to '
                'contributor %s.',
                total,
                source.pk,
                source.contributor_id,
            )

        return total
