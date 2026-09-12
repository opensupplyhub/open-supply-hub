from simple_history.models import HistoricalRecords
from django.db import models

from api.constants import FacilityClaimReviewNoteTypes


class FacilityClaimReviewNote(models.Model):
    """
    A note entered by an administrator when reviewing a FacilityClaim.
    """

    NOTE_TYPE_CHOICES = (
        (FacilityClaimReviewNoteTypes.INTERNAL,
         FacilityClaimReviewNoteTypes.INTERNAL),
        (FacilityClaimReviewNoteTypes.CLAIMANT_MESSAGE,
         FacilityClaimReviewNoteTypes.CLAIMANT_MESSAGE),
        (FacilityClaimReviewNoteTypes.CLAIMANT_UPDATE,
         FacilityClaimReviewNoteTypes.CLAIMANT_UPDATE),
    )

    claim = models.ForeignKey(
        'FacilityClaim',
        null=False,
        on_delete=models.PROTECT,
        help_text='The facility claim for this note'
    )
    author = models.ForeignKey(
        'User',
        null=False,
        on_delete=models.PROTECT,
        help_text='The author of the facility claim review note')
    note = models.TextField(
        null=False,
        blank=False,
        help_text='The review note')
    note_type = models.CharField(
        max_length=200,
        null=False,
        choices=NOTE_TYPE_CHOICES,
        default=FacilityClaimReviewNoteTypes.INTERNAL,
        db_default=FacilityClaimReviewNoteTypes.INTERNAL,
        help_text=('Direction of the note. INTERNAL = moderator to '
                   'moderator (though the reason text in deny/revoke notes '
                   'may still reach the claimant inside status emails). '
                   'CLAIMANT_MESSAGE = moderator to claimant, emailed via '
                   'the message-claimant action. CLAIMANT_UPDATE = claimant '
                   'to moderator, recorded when a claimant edits their '
                   'pending claim or uploads documents (OSDEV-2278). Rows '
                   'created before this field existed default to INTERNAL '
                   'regardless of direction.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()
