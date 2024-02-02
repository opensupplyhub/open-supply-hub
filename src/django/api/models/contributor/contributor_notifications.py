from simple_history.models import HistoricalRecords
from django.db import models


class ContributorNotifications(models.Model):
    """
    Records notifications sent to contributors.
    """
    contributor = models.OneToOneField(
        'Contributor',
        null=False,
        on_delete=models.CASCADE,
        help_text='The contributor to whom the notification was sent.'
    )
    api_limit_warning_sent_on = models.DateTimeField(
        null=True,
        help_text='When a limit warning was sent to the contributor.')
    api_limit_exceeded_sent_on = models.DateTimeField(
        null=True,
        help_text='When a limit exceeded notice was sent to the contributor.')
    api_grace_limit_exceeded_sent_on = models.DateTimeField(
        null=True,
        help_text=('When a grace limit exceeded notice was sent '
                   'to the contributor.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return ('ContributorNotification {id} - Contributor {contributor_id} '
                'Warning: {api_limit_warning_sent_on}, '
                'Exceeded: {api_limit_exceeded_sent_on}, '
                'Grace exceeded: {api_grace_limit_exceeded_sent_on} '
                ).format(**self.__dict__)
