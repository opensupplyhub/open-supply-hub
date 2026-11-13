from django.contrib.postgres import fields as postgres
from django.db import models

from api.constants import FacilityClaimLiveCheckStatuses


class FacilityClaimLiveCheck(models.Model):
    """
    One live check of a claim (OSDEV-3804): the claimant asked for the
    claim to be reviewed by the claims automation pipeline right away,
    and this row records how that went. A claim has at most a few of
    these; the newest is the one the claimant is shown.
    """

    STATUS_CHOICES = (
        (FacilityClaimLiveCheckStatuses.CHECKING,
         FacilityClaimLiveCheckStatuses.CHECKING),
        (FacilityClaimLiveCheckStatuses.PASSED,
         FacilityClaimLiveCheckStatuses.PASSED),
        (FacilityClaimLiveCheckStatuses.NOT_PASSED,
         FacilityClaimLiveCheckStatuses.NOT_PASSED),
        (FacilityClaimLiveCheckStatuses.UNAVAILABLE,
         FacilityClaimLiveCheckStatuses.UNAVAILABLE),
    )

    claim = models.ForeignKey(
        'FacilityClaim',
        null=False,
        on_delete=models.CASCADE,
        related_name='live_checks',
        help_text='The facility claim that was checked.')
    status = models.CharField(
        max_length=200,
        null=False,
        choices=STATUS_CHOICES,
        default=FacilityClaimLiveCheckStatuses.CHECKING,
        help_text=('Where the check stands. CHECKING = the claims '
                   'automation pipeline was asked and has not answered. '
                   'PASSED = the claim was approved. NOT_PASSED = the '
                   'pipeline held the claim. UNAVAILABLE = the check '
                   'could not run or did not answer in time.'))
    fixes = postgres.ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text=('Keys of the preset fixes shown to the claimant when '
                   'the check did not pass. Empty otherwise.'))
    last_polled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=('When the claim form last asked for this check. A '
                   'result that arrives after the form has stopped '
                   'asking is emailed to the claimant instead.'))
    emailed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=('When the result of this check was emailed to the '
                   'claimant. Empty when they saw it on the page or '
                   'there was nothing to send.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Live check {} of claim {}: {}'.format(
            self.id, self.claim_id, self.status
        )
