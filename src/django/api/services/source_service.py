import logging

from django.db import transaction

from api.models.extended_field import ExtendedField
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
    def reassign_extended_fields(source_pk: int) -> int:
        """
        Re-attribute every ExtendedField that originated from this source's
        facility list items to the source's current contributor, in
        separately committed chunks.

        The function takes a primary key rather than a Source instance,
        and each chunk transaction locks the source row and re-reads its
        current `contributor_id` before selecting and updating fields.
        Callbacks queued by concurrent reassignments of the same source
        can execute out of order; a stale callback that captured an older
        contributor would otherwise overwrite rows a newer callback had
        already re-attributed. Reading the target under the row lock makes
        every callback converge on the latest committed value, and the
        lock serializes concurrent callbacks (and in-flight source
        updates) against each chunk.

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
        total = 0
        while True:
            with transaction.atomic():
                source = (
                    Source.objects
                    .select_for_update()
                    .filter(pk=source_pk)
                    .first()
                )
                if source is None:
                    log.info(
                        'Source %s no longer exists; stopping extended '
                        'field reassignment.',
                        source_pk,
                    )
                    break

                if source.contributor_id is None:
                    # ExtendedField.contributor is NOT NULL, so a cleared
                    # contributor cannot be propagated.
                    log.warning(
                        'Source %s has no contributor; skipping extended '
                        'field reassignment.',
                        source_pk,
                    )
                    break

                chunk_ids = list(
                    ExtendedField.objects
                    .filter(facility_list_item__source_id=source_pk)
                    .exclude(contributor_id=source.contributor_id)
                    .order_by('id')
                    .values_list('id', flat=True)[:REASSIGNMENT_CHUNK_SIZE]
                )
                if not chunk_ids:
                    break

                # A queryset update is used deliberately: it lets the
                # existing api_extendedfield database trigger refresh the
                # affected FacilityIndex rows, and it leaves `updated_at`
                # alone so the publicly displayed contribution date is
                # preserved. It creates no simple_history rows.
                total += ExtendedField.objects.filter(
                    id__in=chunk_ids,
                ).update(contributor_id=source.contributor_id)

        if total:
            log.info(
                'Reassigned %s extended field(s) of source %s.',
                total,
                source_pk,
            )

        return total
