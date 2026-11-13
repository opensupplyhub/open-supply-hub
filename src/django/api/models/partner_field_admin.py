"""
Django admin configuration for partner fields.
"""

import logging

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist
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
            'polygon',
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
                            'break the application or data display for users.'
                        )

            except PartnerField.DoesNotExist:
                logger.warning(
                    f'Partner field `{self.instance.pk}` not found. '
                    'System field must exist in database.'
                )

        self._check_linked_zone_set(cleaned_data)

        return cleaned_data

    def _check_linked_zone_set(self, cleaned_data):
        """
        Refuse a type or schema change that the linked zone set's
        stored zones cannot serve.

        A zone set's zones were validated against the field as it was
        when they were uploaded, and the provider reads them by the
        field's current type and schema (OSDEV-3659). So while a set
        with zones is linked:

        - the type cannot change: a string set carries one label, an
          object set one value per schema key;
        - an object field must keep a schema with a "properties" map,
          as the zone set form requires to link one;
        - a property may become required only if every stored feature
          already carries a usable value for it. Properties outside the
          schema are stored at upload, so the way to add a required
          property is to upload a file carrying it first, then change
          the schema. Any other schema edit (titles, formats, optional
          properties, removing a property) is fine: the provider serves
          the keys that exist.

        A field with no zone set, or whose set has no zones, is not
        checked. Nothing here touches the stored zones.
        """
        if not (self.instance and self.instance.pk):
            return
        if not {'type', 'json_schema'} & set(self.changed_data):
            return
        try:
            zone_set = self.instance.zone_set
        except ObjectDoesNotExist:
            return
        total = zone_set.feature_count
        if not total:
            return

        if 'type' in self.changed_data:
            self.add_error(
                'type',
                f'"{self.instance.name}" feeds zone set "{zone_set.name}", '
                f'whose {total} zone(s) were read for a '
                f'"{self.instance.type}" field. Delete the set\'s zones or '
                'link it to another field before changing the type.'
            )
            return
        if cleaned_data.get('type') != PartnerField.OBJECT:
            return

        schema = cleaned_data.get('json_schema')
        properties = schema.get('properties') if isinstance(
            schema, dict) else None
        if not isinstance(properties, dict) or not properties:
            self.add_error(
                'json_schema',
                f'"{self.instance.name}" feeds zone set "{zone_set.name}", '
                'so it needs a JSON schema with a "properties" map: the '
                'set reads and serves one feature property per schema '
                'property.'
            )
            return

        required = [
            key for key in (schema.get('required') or [])
            if isinstance(key, str)
        ]
        problems = [
            f'{missing} of {total} zone(s) have no value for the required '
            f'property "{key}"'
            for key, missing in (
                (key, zone_set.features_lacking(key)) for key in required
            )
            if missing
        ]
        if problems:
            self.add_error(
                'json_schema',
                f'Zone set "{zone_set.name}" does not satisfy this schema: '
                + '; '.join(problems)
                + '. Upload a file that carries the property to the zone '
                'set first (properties outside the schema are stored), '
                'then change the schema.'
            )


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
        "polygon",
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
