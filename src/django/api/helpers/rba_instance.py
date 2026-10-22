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
    change behaviour.

    Three cases, deliberately distinguished:

    - unset or empty - the ordinary public deployment, which is what every
      environment other than a private instance looks like;
    - a recognized value - returned normalized;
    - set to something unrecognized - a misconfiguration, returned as
      ``None``. It must not resolve to ``os_hub``: that is the value that
      makes ``is_rba_instance()`` false, so a task-definition typo on the
      RBA instance would silently disarm the merge guard and permit exactly
      the unrepairable merge it exists to refuse. Callers that gate a
      guard on this must treat ``None`` as unsafe rather than as public.
    """
    raw = getattr(settings, 'INSTANCE_SOURCE', None)

    if raw is None or not str(raw).strip():
        return OriginSource.OSHUB

    value = str(raw).strip().lower()

    if value not in KNOWN_INSTANCE_SOURCES:
        log.error(
            'INSTANCE_SOURCE is %r, which is not a known origin_source '
            'value. This deployment cannot be identified, so instance '
            'guards fail closed until it is corrected.',
            raw,
        )
        return None

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
    public OS Hub. The one exception is a deployment whose INSTANCE_SOURCE
    is unrecognized, which is refused everywhere by design - see
    ``instance_source``.
    """
    source = instance_source()

    if source is None:
        # Misconfigured INSTANCE_SOURCE: we cannot tell whether this is the
        # RBA instance, so refuse. A refused merge on public OS Hub is a
        # loud, immediately recoverable error; a merge the RBA sync then
        # half-undoes is data damage the sync cannot repair.
        return (
            'This deployment is misconfigured: INSTANCE_SOURCE is not a '
            'recognized production location origin. Merging is refused '
            'until it is corrected, because the check that decides whether '
            'a merge is safe here cannot be evaluated.'
        )

    if source != OriginSource.RBA:
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
