import uuid
from django.db import models


class PartnerField(models.Model):
    """
    Partner Field that will be protected for contribution.
    """
    INT = 'int'
    FLOAT = 'float'
    STRING = 'string'
    OBJECT = 'object'

    TYPE_CHOICES = (
        (INT, INT),
        (FLOAT, FLOAT),
        (STRING, STRING),
        (OBJECT, OBJECT)
    )

    class Meta:
        verbose_name_plural = "partner field"

    uuid = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        help_text='Unique identifier for the partner field.'
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        null=False,
        help_text=('The partner field name.'))
    type = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        choices=TYPE_CHOICES,
        help_text=('The partner field type.'))
    unit = models.CharField(
        max_length=200,
        blank=True,
        help_text=('The partner field unit.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
