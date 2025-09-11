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
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the partner field.'
    )
    name = models.CharField(
        max_length=200,
        primary_key=True,
        help_text=('The partner field name.'))
    type = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        choices=TYPE_CHOICES,
        help_text=('The partner field type.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return the partner field's name as its string representation.
        
        This is used by Django (e.g., admin and shell) whenever the model instance is converted to a string.
        
        Returns:
            str: The value of the `name` field.
        """
        return self.name
