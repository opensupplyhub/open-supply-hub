import uuid

from django.db import models


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
        help_text='Unique human-readable campaign code used in claim links.')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text='The campaign status.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.code})'
