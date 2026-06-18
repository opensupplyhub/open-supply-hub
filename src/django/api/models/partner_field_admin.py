"""
Django admin configuration for partner fields.
"""

import logging

from django import forms
from django.contrib import admin, messages
from jsoneditor.forms import JSONEditor

from .partner_field import PartnerField

logger = logging.getLogger(__name__)


class PartnerFieldAdminForm(forms.ModelForm):
    """
    Admin form for creating and editing partner fields.
    """

    json_schema = forms.JSONField(
        required=False,
        widget=JSONEditor(
            init_options={"mode": "code", "modes": ["code", "tree"]},
            attrs={
                'style': 'width: 800px; height: 400px;'
            }
        )
    )

    class Meta:
        """
        Meta configuration for the partner field admin form.
        """

        model = PartnerField
        fields = [
            'name',
            'type',
            'unit',
            'label',
            'source_by',
            'base_url',
            'display_text',
            'json_schema',
            'active',
            'system_field',
            'available_in_api',
            'available_in_data_downloads',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validate that protected fields of system fields are not modified.
        """
        cleaned_data = super().clean()

        if self.instance and self.instance.pk and self.instance.system_field:
            try:
                original = PartnerField.objects.get(pk=self.instance.pk)

                protected_fields = {
                    'name': 'Name',
                    'type': 'Type',
                    'json_schema': 'JSON Schema',
                    'system_field': 'System Field'
                }

                for field_name, field_label in protected_fields.items():
                    original_value = getattr(original, field_name)
                    current_value = cleaned_data.get(field_name)

                    if original_value != current_value:
                        self.add_error(
                            field_name,
                            f'{field_label} cannot be modified for '
                            'system-defined fields. Editing this field may '
                            'break the application or data display for users. '
                            'Only label, unit, source by, base url, display '
                            'text, active, and availability settings can be '
                            'edited.'
                        )

            except PartnerField.DoesNotExist:
                logger.warning(
                    f'Partner field `{self.instance.pk}` not found. '
                    'System field must exist in database.'
                )

        return cleaned_data


class PartnerFieldAdmin(admin.ModelAdmin):
    """
    Admin interface for managing partner field definitions and availability.
    """

    form = PartnerFieldAdminForm
    list_display = (
        "name",
        "type",
        "label",
        "unit",
        "group",
        "active",
        "system_field",
        "available_in_api",
        "available_in_data_downloads",
        "created_at",
    )
    search_fields = ("name", "type", "label", "unit", "source_by")
    list_filter = (
        "active",
        "system_field",
        "available_in_api",
        "available_in_data_downloads",
        "type",
        "group",
    )
    readonly_fields = ("uuid", "created_at", "updated_at")
    fields = (
        "name",
        "type",
        "unit",
        "label",
        "group",
        "source_by",
        "base_url",
        "display_text",
        "json_schema",
        "active",
        "system_field",
        "available_in_api",
        "available_in_data_downloads",
        "created_at",
        "updated_at",
    )

    def get_queryset(self, request):
        """
        Return all partner fields, including inactive ones, for admin views.
        """
        qs = self.model.objects.get_all_including_inactive()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of system-defined partner fields.
        """
        if obj and obj.system_field:
            messages.warning(
                request,
                f'Partner field \'{obj.name}\' cannot be deleted because it '
                'is a system-defined field.'
            )
            return False

        return super().has_delete_permission(request, obj)

    class Media:
        """
        Static assets required by the partner field admin interface.
        """

        js = (
            'admin/js/jquery.init.js',
            'admin/js/partner_field_admin.js',
        )
