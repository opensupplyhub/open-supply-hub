"""
Community validation of candidate facilities (OSDEV-3245, design
decisions D4 and D6).

A candidate's validation state is never stored: it is derived from the
live tally of ``FacilityCandidateVote`` rows each time it is needed.

    state        tally condition                      behavior
    -----------  -----------------------------------  ----------------------
    unverified   total < CANDIDATE_VOTE_THRESHOLD     voting open
    disputed     threshold reached, no consensus      voting open, labeled
    confirmed    confirmed share >= CONFIRM_MARGIN    voting closed (409)
    retired      not_a_facility share >= RETIRE_MARGIN hard delete + tombstone

"confirmed" is therefore "consensus-yes right now": the moment the tally
reaches it, ``POST .../candidate-votes/`` answers 409 and the tally can
no longer move, so the state is stable without a stored flag. Later
concerns about a confirmed location use the normal flows (closure
report etc.), exactly as D6 says.

"retired" is the only irreversible edge and is moderator-gated during the
pilot: with ``CANDIDATE_AUTO_RETIRE`` off (default) a vote that reaches
consensus-no opens a ``FacilityCandidateRetirementRequest`` instead of
deleting anything, voting stays open, and the API reports the candidate
as ``retirement_pending`` (an API-only label: the D6 state is "retired",
but the OS ID still resolves). A moderator executes the retirement via
``POST /api/v1/candidate-retirement-requests/{id}/approve/``. With the
toggle on, the vote that reaches consensus-no retires the candidate on
the spot through ``retire_candidate``.

The thresholds come from Django settings (env-backed, see
``oar/settings.py``); ``derive_state`` also takes them as keyword
arguments so it can be unit-tested as a pure function without a database.
"""
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.db.models import Count

from api.models.facility.facility import Facility
from api.models.facility.facility_candidate_retirement_request import (
    FacilityCandidateRetirementRequest,
)
from api.models.facility.facility_candidate_vote import FacilityCandidateVote
from api.services.candidate_retirement import retire_candidate

UNVERIFIED = 'unverified'
DISPUTED = 'disputed'
CONFIRMED = 'confirmed'
RETIRED = 'retired'
# API-only label for a candidate at consensus-no that the moderation gate
# has not yet retired. Never returned by derive_state.
RETIREMENT_PENDING = 'retirement_pending'

CONFIRMED_VOTE = FacilityCandidateVote.Vote.CONFIRMED.value
NOT_A_FACILITY_VOTE = FacilityCandidateVote.Vote.NOT_A_FACILITY.value


def tally(facility):
    """The live vote tally: ``{"confirmed": n, "not_a_facility": m}``."""
    counts = {CONFIRMED_VOTE: 0, NOT_A_FACILITY_VOTE: 0}
    rows = (
        FacilityCandidateVote.objects
        .filter(facility=facility)
        .values('vote')
        .annotate(count=Count('id'))
    )
    for row in rows:
        counts[row['vote']] = row['count']
    return counts


def derive_state(
    vote_tally,
    *,
    threshold=None,
    confirm_margin=None,
    retire_margin=None,
):
    """
    Map a tally to one of UNVERIFIED / DISPUTED / CONFIRMED / RETIRED.

    Pure: no database access. The three knobs default to the Django
    settings (``CANDIDATE_VOTE_THRESHOLD``, ``CANDIDATE_CONFIRM_MARGIN``,
    ``CANDIDATE_RETIRE_MARGIN``). A share is that side's votes divided by
    the total, compared with ``>=`` against its margin. If a
    misconfiguration (both margins <= 0.5) lets both sides reach their
    margin at once, there is no consensus and the state is DISPUTED.
    """
    if threshold is None:
        threshold = settings.CANDIDATE_VOTE_THRESHOLD
    if confirm_margin is None:
        confirm_margin = settings.CANDIDATE_CONFIRM_MARGIN
    if retire_margin is None:
        retire_margin = settings.CANDIDATE_RETIRE_MARGIN

    confirmed = vote_tally.get(CONFIRMED_VOTE, 0)
    not_a_facility = vote_tally.get(NOT_A_FACILITY_VOTE, 0)
    total = confirmed + not_a_facility

    if total == 0 or total < threshold:
        return UNVERIFIED

    is_confirmed = confirmed / total >= confirm_margin
    is_retired = not_a_facility / total >= retire_margin
    if is_confirmed and not is_retired:
        return CONFIRMED
    if is_retired and not is_confirmed:
        return RETIRED
    return DISPUTED


def voting_is_closed(state):
    """Existence voting closes once the candidate is confirmed (D6)."""
    return state == CONFIRMED


def public_state(state, retired=False):
    """
    The ``state`` value the API reports. Equal to the derived state
    except at consensus-no under the moderation gate: the candidate is
    not gone, so it is reported as ``retirement_pending``.
    """
    if state == RETIRED and not retired:
        return RETIREMENT_PENDING
    return state


@dataclass
class VoteOutcome:
    created: bool
    vote: str
    tally: dict
    state: str
    retired: bool = False
    tombstone: Optional[object] = None

    @property
    def reported_state(self):
        return public_state(self.state, retired=self.retired)


class VotingClosedError(Exception):
    """Raised when a vote is cast on a confirmed candidate."""


@transaction.atomic
def cast_vote(facility, user, vote):
    """
    Record ``user``'s ``vote`` on candidate ``facility`` and apply the
    consequences of the new tally.

    * One row per (facility, user): a repeat vote updates in place
      (``created`` tells the API 201 from 200).
    * The candidate row is locked for the duration, so concurrent votes
      on the same candidate serialize and the retirement decision is
      made on a consistent tally.
    * Raises ``VotingClosedError`` if the candidate is already confirmed.
    * At consensus-no: retires the candidate when
      ``CANDIDATE_AUTO_RETIRE`` is on, otherwise opens or refreshes the
      candidate's ``FacilityCandidateRetirementRequest``. Any other state
      dissolves an open request, since there is no longer anything to
      retire.
    """
    facility = (
        Facility.including_candidates
        .select_for_update()
        .get(pk=facility.pk)
    )

    if voting_is_closed(derive_state(tally(facility))):
        raise VotingClosedError(facility.id)

    _, created = FacilityCandidateVote.objects.update_or_create(
        facility=facility,
        user=user,
        defaults={'vote': vote},
    )

    new_tally = tally(facility)
    state = derive_state(new_tally)
    outcome = VoteOutcome(
        created=created, vote=vote, tally=new_tally, state=state
    )

    if state != RETIRED:
        FacilityCandidateRetirementRequest.objects.filter(
            facility=facility
        ).delete()
        return outcome

    if settings.CANDIDATE_AUTO_RETIRE:
        # Deleting the facility CASCADEs the votes and any open request;
        # the tombstone keeps the final tally.
        outcome.tombstone = retire_candidate(
            facility, new_tally, retired_by=user
        )
        outcome.retired = True
        return outcome

    FacilityCandidateRetirementRequest.objects.update_or_create(
        facility=facility,
        defaults={'tally': new_tally},
    )
    return outcome


def approve_retirement(request, moderator):
    """
    Execute an open retirement request: retire the candidate with the
    live tally (not the snapshot, in case votes arrived since) and credit
    ``moderator`` as ``retired_by``. The request row CASCADEs away with
    the facility. Returns the tombstone.
    """
    with transaction.atomic():
        facility = (
            Facility.including_candidates
            .select_for_update()
            .get(pk=request.facility_id)
        )
        return retire_candidate(
            facility, tally(facility), retired_by=moderator
        )
