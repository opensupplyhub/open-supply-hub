from django.db import models


class ProductType(models.Model):
    value = models.CharField(
        primary_key=True,
        max_length=50,
        null=False,
        blank=False,
        help_text='A suggested value for product type'
    )
