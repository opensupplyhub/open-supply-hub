from simple_history.models import HistoricalRecords
from django.db import models
from api.models.transactions.index_facilities_new import index_facilities_new


def hooked_index_facilities(**kwargs):
    instance = kwargs.get('instance')
    index_facilities_new([instance.facility_id])


class FacilityMatchTemp(models.Model):
    """
    [A/B Test model] Matches between existing facilities and uploaded facility
    list items.
    """
    class Meta:
        verbose_name_plural = "facility matches temp"

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
        'FacilityListItemTemp',
        on_delete=models.PROTECT,
        help_text='The list item being matched to an existing facility.')
    facility_id = models.CharField(
        max_length=200,
        null=True,
        blank=False,
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
    version = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='The version of Dedupe Hub instance that used.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __init__(self, *args, **kwargs):
        super(FacilityMatchTemp, self).__init__(*args, **kwargs)
        self.__original_is_active = self.is_active

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super(FacilityMatchTemp, self).save(
            force_insert, force_update, *args, **kwargs)

        if self.__original_is_active and not self.is_active:
            if self.facility.revert_ppe(self.facility_list_item):
                self.facility.save()

        self.__original_is_active = self.is_active

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

    @staticmethod
    def post_save(sender, **kwargs):
        pass
        # hooked_index_facilities(**kwargs)

    @staticmethod
    def post_delete(sender, **kwargs):
        pass
        # hooked_index_facilities(**kwargs)
