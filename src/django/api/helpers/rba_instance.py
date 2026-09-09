"""Instance-scoped guards for the RBA private instance (OSDEV-3435).

The RBA instance receives a one-way nightly sync from public OS Hub. That
sync upserts by uuid, overwrites the synced fields of any record that also
exists publicly, and never deletes.

A merge deletes the merged-away record locally. If that record also exists
publicly the sync recreates it on the next run, leaving the merge half
applied - the aliases and matches it re-pointed stay with the target while
the absorbed facility is live again. The sync cannot repair that, so the
merge is refused rather than allowed to produce it.

Only the merged-away record carries that risk. The target survives the
merge, and the merge writes none of the target's synced fields, so
absorbing an instance-created duplicate into a publicly-synced record is
safe. That is the ordinary cleanup case on this instance and must keep
working.

Guarding the merged-away record also covers the other reason the guard
exists - absorbing another organisation's facility into an instance
record - because the absorbed facility is the merged-away one.

This module is the single source of truth for "is this the RBA instance?"
and "may this facility be merged away here?". Callers should use these
helpers rather than re-implementing either check inline.
"""
import logging

from django.conf import settings

from api.constants import OriginSource

log = logging.getLogger(__name__)

KNOWN_INSTANCE_SOURCES = frozenset(
    value for value, _ in OriginSource.CHOICES
)


def instance_source():
    """
    This deployment's own origin_source value, normalized.

    Read defensively: the value arrives from an environment variable set in
    a task definition, so stray whitespace or casing must not silently
    change behaviour. An unrecognized value is logged rather than passed
    through, because a typo here would disable the merge guard with no
    other trace.
    """
    raw = getattr(settings, 'INSTANCE_SOURCE', OriginSource.OSHUB) or ''
    value = raw.strip().lower()

    if value not in KNOWN_INSTANCE_SOURCES:
        log.warning(
            'INSTANCE_SOURCE is %r, which is not a known origin_source '
            'value. Treating this deployment as %s.',
            raw, OriginSource.OSHUB,
        )
        return OriginSource.OSHUB

    return value


def is_rba_instance():
    """True when this deployment is the RBA private instance."""
    return instance_source() == OriginSource.RBA


def is_rba_origin(facility):
    """
    True when the facility was created on the RBA instance.

    ``origin_source`` is nullable, and an unstamped row is left NULL rather
    than defaulting to anything, so only an explicit ``rba`` counts. The
    guard fails closed: a record we cannot prove is local is treated as
    publicly synced.
    """
    return facility.origin_source == OriginSource.RBA


def merge_rejection_reason(merged_facility):
    """
    Why this facility may not be merged away here, or None if it may.

    Self-gating: returns None outside the RBA instance, so a caller that
    forgets to check the environment cannot accidentally block merges on
    public OS Hub.
    """
    if not is_rba_instance():
        return None

    if is_rba_origin(merged_facility):
        return None

    log.info(
        'Refusing to merge away %s: it is not %s-origin, so the sync would '
        'recreate it.', merged_facility.id, OriginSource.RBA,
    )
    return (
        '{} was synced from Open Supply Hub and cannot be merged away on '
        'this instance - the next sync would recreate it and leave the '
        'merge half applied. Only production locations created here can be '
        'merged away. If this record duplicates one created here, merge '
        'that one into this record instead.'.format(merged_facility.id)
    )
