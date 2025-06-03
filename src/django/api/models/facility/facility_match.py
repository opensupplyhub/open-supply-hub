from simple_history.models import HistoricalRecords

from django.db import models
from ...constants import OriginSource


class FacilityMatch(models.Model):
    """
    Matches between existing facilities and uploaded facility list items.
    """
    class Meta:
        verbose_name_plural = "facility matches"

    PENDING = 'PENDING'
    AUTOMATIC = 'AUTOMATIC'
    CONFIRMED = 'CONFIRMED'
    REJECTED = 'REJECTED'
    MERGED = 'MERGED'

    # These values must stay in sync with the `facilityMatchStatusChoicesEnum`
    # in the client's constants.js file.
    STATUS_CHOICES = (
        (PENDING, PENDING),
        (AUTOMATIC, AUTOMATIC),
        (CONFIRMED, CONFIRMED),
        (REJECTED, REJECTED),
        (MERGED, MERGED),
    )

    facility_list_item = models.ForeignKey(
        'FacilityListItem',
        on_delete=models.PROTECT,
        help_text='The list item being matched to an existing facility.')
    facility = models.ForeignKey(
        'Facility',
        on_delete=models.PROTECT,
        help_text=('The existing facility that may match an uploaded list '
                   'item.'))
    results = models.JSONField(
        help_text='Diagnostic details from the matching process.')
    confidence = models.DecimalField(
        null=False,
        max_digits=5,
        decimal_places=2,
        default=0.0,
        help_text=('A numeric representation of how confident the app is that '
                   'the list item matches the existing facility. Larger '
                   'numbers are better.'))
    status = models.CharField(
        null=False,
        max_length=9,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text=('The current status of the match. AUTOMATIC if the '
                   'application made a match with high confidence. PENDING '
                   'if confirmation from the contributor admin is required. '
                   'CONFIRMED if the admin approves the match. REJECTED if '
                   'the admin rejects the match. Only one row for a given '
                   'and facility list item pair should have either AUTOMATIC '
                   'or CONFIRMED status'))
    is_active = models.BooleanField(
        null=False,
        default=True,
        help_text=('A facility match is_active if its associated list item '
                   'not been removed; when a list item is removed, this '
                   'field will be set to False.')
    )
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        default=OriginSource.OSHUB,
        max_length=200,
        help_text="The environment value where instance running"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    @property
    def source(self):
        return self.facility_list_item.source

    @property
    def should_display_association(self):
        return (self.is_active
                and self.facility_list_item.source.is_active
                and self.facility_list_item.source.is_public)

    def __str__(self):
        return f'{self.facility_list_item} - {self.facility} - {self.status}'
