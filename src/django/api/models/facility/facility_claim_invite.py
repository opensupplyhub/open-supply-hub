import uuid
from django.db import models


class FacilityClaimInvite(models.Model):
    """
    An email invitation, sent by a registered user from an unclaimed
    production location's profile, asking someone at the location to
    claim it. The uuid travels in the claim link (?invite=<uuid>) so a
    claim submitted from the invite can be traced back to it.
    """
    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Code carried in the claim link sent with the invite.'
    )
    facility = models.ForeignKey(
        'Facility',
        null=False,
        on_delete=models.CASCADE,
        related_name='claim_invites',
        help_text='The production location the recipient is invited to '
                  'claim.'
    )
    sent_by_user = models.ForeignKey(
        'User',
        null=False,
        on_delete=models.PROTECT,
        help_text='The user who sent the invite.'
    )
    sent_by_contributor = models.ForeignKey(
        'Contributor',
        null=False,
        on_delete=models.PROTECT,
        help_text='The contributor (organization) named as the sender in '
                  'the invite email.'
    )
    recipient_email = models.EmailField(
        null=False,
        blank=False,
        db_index=True,
        help_text='The email address the invite was sent to.'
    )
    note = models.TextField(
        null=False,
        blank=True,
        default='',
        max_length=500,
        help_text='Optional personal note from the sender, included in the '
                  'email as plain text.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} invited {} to claim {}'.format(
            self.sent_by_contributor_id,
            self.recipient_email,
            self.facility_id,
        )
