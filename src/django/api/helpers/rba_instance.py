"""Instance-scoped guards for the RBA private instance (OSDEV-3435).

The RBA instance receives a one-way nightly sync from public OS Hub. That
sync upserts by uuid, overwrites every synced field of a record that also
exists publicly, and never deletes. A merge performed on the RBA instance
against a publicly-synced record is therefore only half-applied: the
merged-away facility is recreated on the next sync because it still exists
publicly, while the aliases and matches the merge re-pointed stay pointing
at the target. The sync cannot repair that state, so the merge is refused
rather than allowed to produce it.

Merges between records created on the RBA instance are unaffected - the
sync never reads rows that have no public counterpart.

This module is the single source of truth for "is this the RBA instance?"
and "may these facilities be merged here?". Callers should use these
helpers rather than re-implementing either check inline.
"""
import logging

from django.conf import settings

from api.constants import OriginSource

log = logging.getLogger(__name__)


def is_rba_instance():
    """True when this deployment is the RBA private instance."""
    return getattr(
        settings, 'INSTANCE_SOURCE', OriginSource.OSHUB
    ) == OriginSource.RBA


def is_rba_origin(facility):
    """
    True when the facility was created on the RBA instance.

    ``origin_source`` is nullable, and the database trigger's fallback for
    a write that arrives without the session setting is ``os_hub``, so
    anything not explicitly stamped ``rba`` is treated as publicly synced.
    The guard fails closed: an unstamped record is not mergeable.
    """
    return facility.origin_source == OriginSource.RBA


def get_unmergeable_os_ids(*facilities):
    """
    Return the OS IDs, in argument order, that may not be merged here.

    An empty list means the merge is permitted.
    """
    return [
        facility.id
        for facility in facilities
        if not is_rba_origin(facility)
    ]
