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
    One production location a campaign invites to claim. When a campaign
    has any of these rows, they are its roster; a campaign with none
    falls back to the v1 roster (the contributor's active lists).
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

    def __str__(self):
        return f'{self.campaign.code} → {self.facility_id}'
