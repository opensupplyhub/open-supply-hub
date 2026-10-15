from django.conf import settings
from django.db import models


class FacilityCandidateVote(models.Model):
    """
    One community member's existence vote on one candidate facility
    (OSDEV-3245, design decision D4).

    The click is the data: there is no reason or documentation field,
    confidence comes from agreement. One row per (facility, user); a user
    who changes their mind updates that row in place rather than adding a
    second one, so the tally is always "current opinion per account".
    The candidate's validation state (unverified / disputed / confirmed /
    retired) is never stored here: it is derived from the live tally by
    ``api.services.candidate_validation`` (design decision D6).

    ``facility`` cascades on purpose: retirement copies the final tally
    onto the NOT_A_FACILITY tombstone first (``retire_candidate``), so
    the per-user rows have nothing left to say once the row is gone.
    """

    class Vote(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        NOT_A_FACILITY = 'not_a_facility', 'Not a facility'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['facility', 'user'],
                name='api_facilitycandidatevote_facility_user_uniq',
            ),
        ]

    facility = models.ForeignKey(
        'Facility',
        on_delete=models.CASCADE,
        related_name='candidate_votes',
        help_text='The candidate facility this vote is about.',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_votes',
        help_text='The account that cast the vote.',
    )
    vote = models.CharField(
        max_length=14,
        choices=Vote.choices,
        help_text=(
            'Whether the voter believes the candidate is a real facility '
            '(confirmed) or not (not_a_facility).'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Moves when the voter changes their vote.',
    )

    def __str__(self):
        return f'{self.user_id} voted {self.vote} on {self.facility_id}'
