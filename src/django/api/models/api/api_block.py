from simple_history.models import HistoricalRecords
from django.db import models


class ApiBlock(models.Model):
    """
    Stores information regarding api blocks incurred by users.
    """
    contributor = models.ForeignKey(
        'Contributor',
        null=False,
        on_delete=models.CASCADE,
        help_text='The contributor to whom the block applies.'
    )
    until = models.DateTimeField(
        null=False,
        help_text='The time until which the block is enforced.'
    )
    active = models.BooleanField(
        default=True,
        help_text='Whether or not the block should restrict access.'
    )
    limit = models.PositiveIntegerField(
        null=False,
        blank=False,
        help_text='The limit value that was exceeded.')
    actual = models.PositiveIntegerField(
        null=False,
        blank=False,
        help_text='The count that exceeded the limit.')
    grace_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='An ad-hoc increase in the limit.')
    grace_created_by = models.ForeignKey(
        'User',
        null=True,
        on_delete=models.SET_NULL,
        help_text='The person who set the grace_limit.')
    grace_reason = models.TextField(
        null=True,
        blank=True,
        help_text=(
            'For moderators to explain the interactions that led '
            'to the grace being granted.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return ('ApiBlock {id} - Contributor {contributor_id} until '
                '{until}').format(**self.__dict__)
