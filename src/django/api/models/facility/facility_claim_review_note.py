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
        help_text=('How the note was delivered. CLAIMANT_MESSAGE = emailed '
                   'to the claimant via the message-claimant action. '
                   'INTERNAL = not sent directly, although the reason text '
                   'in deny/revoke notes may still reach the claimant '
                   'inside status emails. Rows created before this field '
                   'existed default to INTERNAL regardless of delivery.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()
