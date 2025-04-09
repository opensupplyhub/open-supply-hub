from django.db import models


class Settings(models.Model):
    """
    Model to store app settings.
    """

    class Name(models.TextChoices):
        OS_SENTENCE_TRANSFORMER_GROUP_ID = 'os_sentence_transformer_group_id', 'OS Sentence Transformer Group ID'

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

    @staticmethod
    def get(name: str, description: str):
        setting, _ = Settings.objects.get_or_create(
            defaults={
                "name": name,
                "description": description,
            }
        )

        return setting
