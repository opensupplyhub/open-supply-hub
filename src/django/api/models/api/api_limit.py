from simple_history.models import HistoricalRecords
from django.db import models
from django.utils import timezone


class ApiLimit(models.Model):
    """
    Stores the number of requests a Contributor can make monthly/yearly.
    """
    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'

    RENEWAL_PERIOD_CHOICES = (
        (MONTHLY, MONTHLY),
        (YEARLY, YEARLY)
    )

    contributor = models.OneToOneField(
        'Contributor',
        null=False,
        on_delete=models.CASCADE,
        help_text='The contributor to whom the limit applies.'
    )
    yearly_limit = models.PositiveIntegerField(
        null=False,
        blank=False,
        help_text='The number of requests a contributor can make per year.')
    period_start_date = models.DateTimeField(
        null=False,
        default=timezone.now,
        help_text='The date when the contract began.')
    renewal_period = models.CharField(
        max_length=200,
        null=False,
        blank=True,
        choices=RENEWAL_PERIOD_CHOICES,
        help_text=('Any limit set up on the 29th, 30th, or 31st '
                   'will renew on the 1st of the following month.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return (
            f'ApiLimit {self.id} - {self.contributor.name}'
            f'({self.contributor.id})'
            f' - limit {self.yearly_limit}'
        )
