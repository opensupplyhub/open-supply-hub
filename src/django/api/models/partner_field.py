import uuid
import logging

from django.db import models
from django.core.cache import cache
from django_ckeditor_5.fields import CKEditor5Field

from api.constants import PARTNER_FIELD_LIST_KEY, PARTNER_FIELD_NAMES_KEY
from api.models.partner_field_manager import PartnerFieldManager

logger = logging.getLogger(__name__)


class PartnerField(models.Model):
    """
    Partner Field that will be protected for contribution.
    """

    INT = "int"
    FLOAT = "float"
    STRING = "string"
    OBJECT = "object"

    TYPE_CHOICES = (
        (INT, INT),
        (FLOAT, FLOAT),
        (STRING, STRING),
        (OBJECT, OBJECT),
    )

    class Meta:
        verbose_name_plural = "Partner fields"

    uuid = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        help_text="Unique identifier for the partner field.",
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        null=False,
        help_text=("The partner field name."),
    )
    type = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        choices=TYPE_CHOICES,
        help_text=("The partner field type."),
    )
    unit = models.CharField(
        max_length=200,
        blank=True,
        help_text=("The partner field unit."),
    )
    label = models.CharField(
        max_length=200,
        blank=True,
        help_text=("The partner field label."),
    )
    base_url = models.URLField(
        max_length=2000,
        blank=True,
    )
    display_text = models.CharField(
        max_length=500,
        blank=True,
    )
    source_by = CKEditor5Field(
        blank=True,
        null=True,
        help_text=(
            "Rich text field describing the source of this partner field."
        ),
    )
    json_schema = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            "JSON Schema for validating object type partner fields. "
            'Used when type is "object".'
        ),
    )
    active = models.BooleanField(
        default=True,
        help_text=(
            "Indicates if this partner field is active. "
            "Inactive fields are not available for contributions and "
            "will not appear in listings."
        ),
    )
    system_field = models.BooleanField(
        default=False,
        help_text=(
            "Indicates if this is a system field. "
            "System fields cannot be deleted and have restricted editing."
        ),
    )
    group = models.ForeignKey(
        'PartnerFieldGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partner_fields',
        help_text="The group this partner field belongs to.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PartnerFieldManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Save partner field and invalidate cache if needed."""
        self.clean()
        if self._state.adding:
            self.__invalidate_cache()
            return super().save(*args, **kwargs)

        try:
            original = PartnerField.objects \
                .get_all_including_inactive() \
                .get(pk=self.pk)

            if original.active != self.active:
                self.__invalidate_cache()
        except PartnerField.DoesNotExist:
            logger.warning(
                f"Partner field `{self.pk}` not found. "
                "System field must exist in database."
            )
            self.__invalidate_cache()

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete partner field and invalidate cache."""
        result = super().delete(*args, **kwargs)
        self.__invalidate_cache()
        return result

    def clean(self):
        if self.source_by:
            cleaned = self.source_by.strip()
            # Set to empty string if content is just CKEditor placeholder.
            self.source_by = '' if cleaned == '<p>&nbsp;</p>' else cleaned

    def __invalidate_cache(self):
        """Invalidate cache for partner field list and names."""
        cache.delete(PARTNER_FIELD_LIST_KEY)
        cache.delete(PARTNER_FIELD_NAMES_KEY)
