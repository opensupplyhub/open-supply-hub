import uuid

from django.core.validators import RegexValidator
from django.db import models

# Codes go into public claim links (`?campaign=CODE`), so keep them to a
# URL-safe, unambiguous upper-case alphabet.
CAMPAIGN_CODE_VALIDATOR = RegexValidator(
    regex=r'^[A-Z0-9][A-Z0-9-]*$',
    message=(
        'Use upper-case letters, digits and hyphens only, starting with a '
        'letter or digit.'
    ),
)


class ClaimCampaign(models.Model):
    """
    A campaign run by a contributor (e.g. a brand) to get its suppliers
    to claim their production location profiles.
    """

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        CLOSED = 'CLOSED', 'Closed'

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the claim campaign.'
    )
    contributor = models.ForeignKey(
        'Contributor',
        null=False,
        on_delete=models.PROTECT,
        help_text='The contributor who owns this claim campaign.')
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The campaign name.')
    code = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        unique=True,
        validators=[CAMPAIGN_CODE_VALIDATOR],
        help_text='Unique human-readable campaign code used in claim links.')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text='The campaign status.')
    uses_roster = models.BooleanField(
        default=False,
        verbose_name='chosen suppliers only',
        help_text=(
            'On: the campaign invites only the suppliers listed below, even '
            'if that list becomes empty. Off (v1): it covers every '
            'production location on the brand\'s active lists. Turned on '
            'automatically when suppliers are chosen.'
        ))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.code})'


class ClaimCampaignSupplier(models.Model):
    """
    One production location a campaign invites to claim. A campaign with
    `uses_roster` set invites exactly these (none, if all are removed); a
    campaign without it uses the v1 roster (the contributor's active
    lists).
    """

    campaign = models.ForeignKey(
        ClaimCampaign,
        null=False,
        on_delete=models.CASCADE,
        related_name='suppliers',
        help_text='The campaign that invites this production location.')
    facility = models.ForeignKey(
        'Facility',
        null=False,
        on_delete=models.CASCADE,
        related_name='claim_campaign_suppliers',
        help_text='The invited production location.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['campaign', 'facility'],
                name='unique_claim_campaign_supplier',
            ),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Choosing a supplier (here, or in Django admin) puts the campaign
        # on its chosen roster for good, so removing every supplier later
        # leaves it empty instead of covering all the brand's lists.
        if not self.campaign.uses_roster:
            ClaimCampaign.objects.filter(pk=self.campaign_id).update(
                uses_roster=True
            )
            self.campaign.uses_roster = True

    def __str__(self):
        return f'{self.campaign.code} → {self.facility_id}'
