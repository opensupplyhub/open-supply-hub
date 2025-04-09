from django.db import models

class Settings(models.Model):
    """
    Model to store app settings.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text='Name of the setting.'
    )

    description = models.CharField(
        max_length=255,
        help_text='Description of the setting.'
    )

    value = models.CharField(
        max_length=255,
        help_text='Value of the setting.'
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Date when the moderation queue entry was created.'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Date when the moderation queue entry was last updated.',
        db_index=True
    )
