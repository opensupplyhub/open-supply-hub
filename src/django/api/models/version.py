from django.db import models


class Version(models.Model):
    """
    A table storing feature version numbers.
    """
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        primary_key=True,
        help_text='The name of a feature with versions.')
    version = models.IntegerField(
        null=False,
        blank=False,
        help_text='The version number of the feature.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
