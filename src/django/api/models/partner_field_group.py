import uuid
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class PartnerFieldGroup(models.Model):
    """
    Group for partner fields.
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        help_text="Unique identifier for the partner field group.",
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        null=False,
        help_text="The partner field group name.",
    )
    order = models.IntegerField(
        default=0,
        help_text="Order for the partner field group in the UI.",
    )
    icon_file = models.FileField(
        upload_to="partner_field_groups/icons/",
        blank=True,
        null=True,
        help_text="Upload an icon image.",
    )
    icon_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Material UI icon name (e.g. 'check_circle').",
    )
    description = CKEditor5Field(
        blank=True,
        null=True,
        help_text="Rich text description of the partner field group.",
    )
    helper_text = CKEditor5Field(
        blank=True,
        null=True,
        help_text="Rich text helper text for the partner field group.",
    )

    class Meta:
        verbose_name_plural = "Partner field groups"
        ordering = ["order"]

    def __str__(self):
        return self.name
