from simple_history.models import HistoricalRecords
from django.db import models
from ...constants import OriginSource


class FacilityAlias(models.Model):
    """
    Links the OS ID of a no longer existing Facility to another Facility
    """
    class Meta:
        verbose_name_plural = "facility aliases"

    MERGE = 'MERGE'
    DELETE = 'DELETE'

    REASON_CHOICES = (
        (MERGE, MERGE),
        (DELETE, DELETE),
    )

    os_id = models.CharField(
        max_length=32,
        primary_key=True,
        editable=False,
        help_text=('The OS ID of a no longer existent Facility which '
                   'should be redirected to a different Facility.'))
    facility = models.ForeignKey(
        'Facility',
        null=False,
        on_delete=models.PROTECT,
        help_text='The facility now associated with the os_id'
    )
    reason = models.CharField(
        null=False,
        max_length=6,
        choices=REASON_CHOICES,
        help_text='The reason why this alias was created'
    )
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        null=True,
        max_length=200,
        help_text="The environment value where instance running"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.os_id} -> {self.facility}'
