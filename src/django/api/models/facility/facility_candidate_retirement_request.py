from django.db import models


class FacilityCandidateRetirementRequest(models.Model):
    """
    The pilot's moderation gate on candidate retirement (OSDEV-3245,
    design decision D6 "optionally moderator-gated during the pilot").

    When a vote write finds the tally at consensus-no and
    ``settings.CANDIDATE_AUTO_RETIRE`` is False, the candidate is NOT
    deleted; one of these rows is opened instead and a moderator executes
    the retirement through
    ``POST /api/v1/candidate-retirement-requests/{id}/approve/``.

    Rows exist only while the request is open:

    * ``facility`` is unique, so a candidate has at most one open request;
      later votes refresh ``tally`` on the same row.
    * A vote that dissolves the consensus (the tally no longer meets the
      retire margin) deletes the row: there is nothing left to retire.
    * Approval calls ``retire_candidate``; the candidate row is deleted and
      this row CASCADEs away with it. The audit record (final tally,
      ``retired_by``, ``retired_at``) lives on the NOT_A_FACILITY tombstone
      (design decision D5), not here.

    This is deliberately not a ``ModerationEvent``: that model needs a
    contributor, is indexed into OpenSearch for the moderation dashboard
    and feeds the external auto-approval automation while PENDING, none of
    which fits a request that has no single contributor and must never be
    auto-approved.
    """

    class Meta:
        verbose_name = 'candidate retirement request'

    facility = models.OneToOneField(
        'Facility',
        on_delete=models.CASCADE,
        related_name='candidate_retirement_request',
        help_text='The candidate whose tally reached consensus-no.',
    )
    tally = models.JSONField(
        help_text=(
            'The vote tally when the request was opened or last refreshed, '
            'e.g. {"confirmed": 1, "not_a_facility": 5}.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Moves each time a new vote refreshes the tally.',
    )

    def __str__(self):
        return f'Retirement request for {self.facility_id}'
