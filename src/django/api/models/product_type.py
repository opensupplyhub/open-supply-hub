import uuid
from django.db import models


class ProductType(models.Model):
    value = models.CharField(
        primary_key=True,
        max_length=50,
        null=False,
        blank=False,
        help_text='A suggested value for product type'
    )
    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text='Unique identifier for the product type.'
    )
