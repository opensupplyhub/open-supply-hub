"""Pilot guardrail for candidate facility creation (OSDEV-3248).

During the Earth Genome pilot exactly one contributor may create Facility
rows that are candidates (``is_candidate=True``) or that carry an empty
name or address: the Contributor the candidate ingest pipeline
(OSDEV-3244) writes under, designated by the
``EARTH_GENOME_CONTRIBUTOR_ID`` setting (a Contributor id read from the
environment variable of the same name).

The database accepts ``''`` for ``name`` and ``address`` (design decision
D1: empty-string sentinel, columns stay NOT NULL), so nothing below the
API validators stops an arbitrary ``Facility.objects.create()`` from
writing a nameless row. ``Facility.save()`` calls
:func:`assert_may_create_candidate` on every insert to close that gap at
the model boundary, where every ORM write path converges.
"""
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied


class CandidateCreationNotAllowed(PermissionDenied):
    """A non-Earth-Genome path tried to create a candidate or nameless row.

    Subclasses Django's ``PermissionDenied`` because that is what every
    layer above the model already handles: Django's own middleware turns
    it into a 403 page and DRF's default exception handler into a 403
    response carrying this message, so a misconfigured caller surfaces as
    a clear refusal rather than a 500.
    """


def is_earth_genome_contributor(contributor) -> bool:
    """True when ``contributor`` is the designated Earth Genome contributor.

    ``contributor`` may be a ``Contributor`` instance, a contributor id, or
    None. Always False while ``EARTH_GENOME_CONTRIBUTOR_ID`` is None.
    """
    designated = settings.EARTH_GENOME_CONTRIBUTOR_ID
    if designated is None or contributor is None:
        return False
    contributor_id = getattr(contributor, 'id', contributor)
    return contributor_id == designated


def _creating_contributor_id(facility):
    """The id of the contributor behind ``facility.created_from``, or None.

    None whenever the chain ``created_from -> source -> contributor`` is
    broken at any link, so a missing link is rejected rather than trusted.
    """
    if facility.created_from_id is None:
        return None
    try:
        source = facility.created_from.source
    except ObjectDoesNotExist:
        return None
    if source is None:
        return None
    return source.contributor_id


def assert_may_create_candidate(facility) -> None:
    """Raise ``CandidateCreationNotAllowed`` unless ``facility`` was created
    from a list item owned by the Earth Genome contributor.

    Call this only for rows that are candidates or lack a name or address;
    normal named facilities are never subject to the check.
    """
    contributor_id = _creating_contributor_id(facility)
    if is_earth_genome_contributor(contributor_id):
        return
    raise CandidateCreationNotAllowed(
        'Only the Earth Genome contributor may create candidate or '
        'nameless facilities during the pilot. '
        'created_from.source.contributor_id={!r}, '
        'settings.EARTH_GENOME_CONTRIBUTOR_ID={!r}, is_candidate={!r}, '
        'name={!r}, address={!r}.'.format(
            contributor_id,
            settings.EARTH_GENOME_CONTRIBUTOR_ID,
            facility.is_candidate,
            facility.name,
            facility.address,
        )
    )
