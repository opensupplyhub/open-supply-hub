from django.db import models


class DynamicSetting(models.Model):
    """
    This table serves as a dynamic settings.
    """
    cached_tile_expiration_time = models.IntegerField(
        default=604800,
        null=False,
        blank=False,
        help_text='The expiration time in seconds for the cached tile.')

    def __str__(self):
        return ('Dynamic settings, update this entry to configure the app '
                'dynamically.')

    def save(self, *args, **kwargs):
        if DynamicSetting.objects.exists() and self.pk == 1:
            # If an entry already exists, allow updates.
            super().save(*args, **kwargs)
        else:
            # If no entry exists, allow creation of the first entry.
            if not DynamicSetting.objects.exists() and self.pk is None:
                super().save(*args, **kwargs)
            else:
                raise Exception(('Creating a new entry is not allowed. Only '
                                 'updates of the existing one are permitted.'))

    def delete(self, *args, **kwargs):
        raise Exception(("The entry in the dynamic settings can't be deleted "
                         "since it can lead to the outage of the app."))

    @classmethod
    def load(cls):
        obj = cls.objects.get(pk=1)
        return obj
