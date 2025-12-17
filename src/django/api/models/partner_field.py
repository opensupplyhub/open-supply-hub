import uuid

from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField

from api.constants import PARTNER_FIELD_LIST_KEY
from api.models.partner_field_manager import PartnerFieldManager


class PartnerField(models.Model):
    '''
    Partner Field that will be protected for contribution.
    '''
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
        verbose_name_plural = 'partner field'

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
    label = models.CharField(
        max_length=200,
        blank=True,
        help_text=('The partner field label.'))
    base_url = models.URLField(
        max_length=2000,
        blank=True,
    )
    display_text = models.CharField(
        max_length=500,
        blank=True,
    )
    source_by = RichTextField(
        blank=True,
        null=True,
        config_name='default',
        help_text=(
            'Rich text field describing '
            'the source of this partner field.'
        )
    )

    json_schema = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            'JSON Schema for validating object type partner fields. '
            'Used when type is "object".'
        )
    )

    active = models.BooleanField(
        default=True,
        help_text=(
            'Indicates if this partner field is active. '
            'Inactive fields are not available for contributions and '
            'will not appear in listings.'
        )
    )

    system_field = models.BooleanField(
        default=False,
        help_text=(
            'Indicates if this is a system field. '
            'System fields cannot be deleted and have restricted editing.'
        )
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PartnerFieldManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check if this is an existing system field.
        if self.pk:
            try:
                original = PartnerField.objects \
                    .get_all_including_inactive() \
                    .get(
                        pk=self.pk
                    )
                if original.system_field:
                    # Only allow editing of label, source_by, display_text,
                    # and active.
                    editable_fields = [
                        'label', 'source_by', 'display_text', 'active'
                    ]
                    changed_fields = []

                    for field in self._meta.fields:
                        field_name = field.name
                        # Skip auto fields and editable fields.
                        if field_name in ['updated_at', 'created_at'] or \
                           field_name in editable_fields:
                            continue

                        original_value = getattr(original, field_name)
                        current_value = getattr(self, field_name)

                        if original_value != current_value:
                            changed_fields.append(field_name)

                    if changed_fields:
                        raise ValidationError(
                            f'Cannot modify {", ".join(changed_fields)} for '
                            f'system field. Only label, source_by, '
                            f'display_text, and active can be edited.'
                        )

                # Invalidate cache if active status changed.
                if original.active != self.active:
                    cache.delete(PARTNER_FIELD_LIST_KEY)
                    cache.delete('partner_field_names')
            except PartnerField.DoesNotExist:
                pass

        super().save(*args, **kwargs)
        cache.delete(PARTNER_FIELD_LIST_KEY)
        cache.delete('partner_field_names')

    def delete(self, *args, **kwargs):
        if self.system_field:
            raise ValidationError(
                'Cannot delete system field. System fields are protected.'
            )
        result = super().delete(*args, **kwargs)
        cache.delete(PARTNER_FIELD_LIST_KEY)
        cache.delete('partner_field_names')
        return result
