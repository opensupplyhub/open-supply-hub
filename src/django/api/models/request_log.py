from django.db import models


class RequestLog(models.Model):
    """
    Logs non-webapp API requests by User
    """
    user = models.ForeignKey(
        'User',
        null=False,
        on_delete=models.CASCADE,
        help_text='The User account that made the request'
    )
    token = models.CharField(
        max_length=40,
        null=False,
        db_index=True,
        help_text='The API token used to make the request'
    )
    method = models.CharField(
        max_length=6,
        null=False,
        blank=False,
        help_text='The HTTP verb used to make the request'
    )
    path = models.CharField(
        max_length=2083,
        null=False,
        help_text='The requested resource path'
    )
    response_code = models.IntegerField(
        null=True,
        help_text='The HTTP status code returned to the requester'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        created_at = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f'{created_at} - {self.user.email} '
            f'- {self.method} {self.path} '
            f'{self.response_code} ({self.id})'
        )
