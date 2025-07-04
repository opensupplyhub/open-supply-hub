from django.db import models


class DownloadLog(models.Model):
    """
    Log CSV download requests from the web client
    """
    user = models.ForeignKey(
        'User',
        null=False,
        on_delete=models.CASCADE,
        help_text='The User account that made the request'
    )
    path = models.CharField(
        max_length=4096,
        null=False,
        help_text='The requested resource path'
    )
    record_count = models.IntegerField(
        null=False,
        help_text='The number of records in the downloaded file'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
