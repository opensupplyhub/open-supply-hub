from django import forms
from django.contrib import admin, messages
from django.db.models import Count
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.html import format_html
from waffle import switch_is_active

from api.helpers.geojson_polygon import InvalidPolygonGeoJSON
from api.helpers.geojson_zones import parse_zone_features
from api.models.partner_field import PartnerField
from api.models.polygon_admin import PolygonForm
from api.models.zone_set import ZoneSet
from api.partner_fields.registry import (
    ZONE_SETS_SWITCH,
    system_partner_field_registry,
)


class ZoneSetForm(forms.ModelForm):
    """
    Admin form for creating and editing zone sets.

    Zones are not edited as rows: staff upload a GeoJSON
    FeatureCollection and name the feature property that supplies
    each zone's value. The whole file is parsed and validated here, in
    `clean`, before anything is saved — a bad file becomes an ordinary
    red form error and the set's existing zones are left untouched.
    The parsed zones are handed to `ZoneSetAdmin.save_model`, which
    swaps them in atomically.
    """

    geojson_file = forms.FileField(
        required=False,
        help_text=(
            'Upload a .geojson/.json FeatureCollection with one Polygon '
            'or MultiPolygon feature per zone. Required when creating a '
            'set. When editing, leave empty to keep the current zones; '
            'uploading a new file replaces them all. Features are kept '
            'separate (not merged); if zones overlap, the feature that '
            'comes first in the file wins.'
        ),
    )

    # Same cap as polygon uploads: a bigger file almost certainly means
    # an unsimplified export. Whether a set can be assembled from
    # several files is still an open question (OSDEV-3551).
    GEOJSON_FILE_MAX_BYTES = PolygonForm.GEOJSON_FILE_MAX_BYTES

    class Meta:
        model = ZoneSet
        fields = (
            'name', 'description', 'partner_field', 'value_property',
            'active',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The default manager hides inactive partner fields, which
        # would make a set whose field was later deactivated impossible
        # to edit or retire (the saved choice is "not valid"), and
        # would stop a dataset being staged against a field that is
        # not switched on yet.
        self.fields['partner_field'].queryset = (
            PartnerField.objects.get_all_including_inactive()
        )
        # Filled by clean() when a file is uploaded; None means "keep
        # the existing zones".
        self.parsed_zones = None

    def clean_partner_field(self):
        """
        Check the linked field can carry a zone value.

        The provider emits a plain string (`raw_value`), so the field
        must be string-typed: an object/int/float field would serve a
        mis-shaped value to the API and the downloads. And it must not
        be a field one of the hard-wired providers already serves, or
        the registry would yield two providers for one name.
        """
        partner_field = self.cleaned_data.get('partner_field')
        if partner_field is None:
            return partner_field
        if partner_field.type != PartnerField.STRING:
            raise forms.ValidationError(
                f'A zone set can only feed a "{PartnerField.STRING}" '
                f'partner field; "{partner_field.name}" is '
                f'"{partner_field.type}".'
            )
        if partner_field.name in (
            system_partner_field_registry.hard_wired_field_names
        ):
            raise forms.ValidationError(
                f'"{partner_field.name}" is served by a built-in '
                'provider and cannot be fed by a zone set.'
            )
        return partner_field

    def clean(self):
        """
        Parse the uploaded file (if any) into zone records.

        A new set must come with a file. An existing set may be edited
        without one, in which case its zones are kept — unless the
        value property changed, because the stored labels were read
        with the old key and would no longer match; re-uploading makes
        the change explicit.
        """
        cleaned_data = super().clean()
        geojson_file = cleaned_data.get('geojson_file')
        value_property = cleaned_data.get('value_property')

        if not geojson_file:
            if not self.instance.pk:
                raise forms.ValidationError(
                    'Upload a GeoJSON FeatureCollection file.'
                )
            if (
                'value_property' in self.changed_data
                and self.instance.zones.exists()
            ):
                self.add_error(
                    'value_property',
                    'Upload the file again when changing the value '
                    'property, so every zone is re-read with the new '
                    'key.'
                )
            return cleaned_data

        if geojson_file.size > self.GEOJSON_FILE_MAX_BYTES:
            raise forms.ValidationError(
                f'GeoJSON file is too large '
                f'({filesizeformat(geojson_file.size)}; limit '
                f'{filesizeformat(self.GEOJSON_FILE_MAX_BYTES)}). '
                'Simplify the geometry (e.g. with mapshaper.org) and '
                'try again.'
            )
        try:
            raw = geojson_file.read().decode('utf-8')
        except UnicodeDecodeError as exc:
            raise forms.ValidationError(
                f'Could not read the file as UTF-8 text: {exc}'
            ) from exc

        try:
            self.parsed_zones = parse_zone_features(raw, value_property)
        except InvalidPolygonGeoJSON as exc:
            raise forms.ValidationError(str(exc)) from exc

        return cleaned_data


class ZoneSetAdmin(admin.ModelAdmin):
    """Admin for zone sets and their GeoJSON uploads."""

    form = ZoneSetForm
    list_display = (
        'name', 'partner_field', 'value_property', 'zone_count',
        'active', 'updated_at',
    )
    list_filter = ('active',)
    search_fields = ('name', 'description', 'partner_field__name')
    readonly_fields = (
        'uuid', 'zone_summary', 'created_at', 'updated_at',
    )
    fields = (
        'name', 'description', 'partner_field', 'value_property',
        'geojson_file', 'zone_summary', 'active', 'uuid', 'created_at',
        'updated_at',
    )

    def changelist_view(self, request, extra_context=None):
        self._warn_if_zone_sets_switched_off(request)
        return super().changelist_view(request, extra_context)

    def changeform_view(
        self, request, object_id=None, form_url='', extra_context=None
    ):
        self._warn_if_zone_sets_switched_off(request)
        return super().changeform_view(
            request, object_id, form_url, extra_context
        )

    def _warn_if_zone_sets_switched_off(self, request):
        """
        Tell staff, on the zone set screens, when zone sets are off.

        With `enable_zone_sets` inactive a set can be uploaded, linked
        and marked active and still show nothing on any location page,
        with no hint why: the switch lives on a different admin screen.
        Only on GET, so a save that redirects to the list does not
        queue the same warning twice.

        Args:
            request: The admin request to attach the warning to.
        """
        if request.method != 'GET' or switch_is_active(ZONE_SETS_SWITCH):
            return
        messages.warning(request, format_html(
            'The <a href="{}">{}</a> switch is off, so no zone set '
            'serves values on location pages, whatever its "active" '
            'flag says. Turn the switch on when the datasets are ready '
            'to go live.',
            reverse('admin:waffle_switch_changelist'),
            ZONE_SETS_SWITCH,
        ))

    def get_queryset(self, request):
        """Annotate the zone count so the list view needs one query."""
        return super().get_queryset(request).annotate(
            _zone_count=Count('zones')
        )

    @admin.display(description='Zones', ordering='_zone_count')
    def zone_count(self, obj):
        """Number of zones in the set (from the list annotation)."""
        count = getattr(obj, '_zone_count', None)
        return obj.zones.count() if count is None else count

    @admin.display(description='Current zones')
    def zone_summary(self, obj):
        """
        One-line description of the saved zones (count, distinct
        labels, and lon/lat extent), so staff can sanity-check an
        upload at a glance.

        Args:
            obj: The ZoneSet being displayed, or an unsaved instance on
                the add page (which has no zones yet).
        """
        if not obj or not obj.pk:
            return '(no zones saved yet)'
        zones = obj.zones.all()
        count = zones.count()
        if count == 0:
            return '(no zones saved yet)'
        # Distinct labels straight from the database: pulling every
        # zone's full JSON (label plus all source properties) into
        # Python just to dedupe it is slow on large uploads.
        labels = sorted(
            zones.order_by()
            .values_list('value__label', flat=True)
            .distinct()
        )
        shown = ', '.join(labels[:10])
        if len(labels) > 10:
            shown += f', … ({len(labels)} distinct)'
        return f'{count} zone(s); labels: {shown}'

    def save_model(self, request, obj, form, change):
        """
        Save the set, then swap in the uploaded zones if there are any.

        Django wraps the whole admin save in one transaction, and
        `replace_zones` is atomic on its own as well, so the old zones
        keep serving right up until the new ones are committed.
        """
        super().save_model(request, obj, form, change)
        if form.parsed_zones is not None:
            obj.replace_zones(form.parsed_zones)


class ZoneAdmin(admin.ModelAdmin):
    """
    Read-only listing of zones, for checking what an upload produced.
    Zones are created and replaced only through their zone set.
    """

    list_display = ('zone_set', 'feature_index', 'label', 'created_at')
    list_filter = ('zone_set',)
    search_fields = ('value__label',)
    readonly_fields = ('zone_set', 'feature_index', 'label', 'value',
                       'created_at')
    fields = readonly_fields

    @admin.display(description='Label')
    def label(self, obj):
        """The zone's displayed value."""
        return obj.label

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
