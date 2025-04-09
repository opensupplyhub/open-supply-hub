from django.db import models


class Settings(models.Model):
    """
    Model to store app settings.
    """

    class Name(models.TextChoices):
        OS_SENTENCE_TRANSFORMER_GROUP_ID = 'os_sentence_transformer_group_id', 'OS Sentence Transformer Group ID'
        OS_SENTENCE_TRANSFORMER_MODEL_ID = 'os_sentence_transformer_model_id', 'OS Sentence Transformer Model ID'
        OS_SENTENCE_TRANSFORMER_MODEL_NAME = 'os_sentence_transformer_model_name', 'OS Sentence Transformer Model Name'

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

    def update(self, value: str):
        """
        Update the value of the setting.
        """
        self.value = value
        self.save()

    @staticmethod
    def get(name: str, description: str, value: any = None):
        """
        Get or create a setting with the given name and description.
        """
        defaults = {
            "name": name,
            "description": description,
        }

        if value is not None:
            defaults["value"] = value

        setting, _ = Settings.objects.filter(name=name).get_or_create(
            defaults=defaults,
        )

        return setting
