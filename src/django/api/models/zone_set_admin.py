import json

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Count
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.html import format_html
from waffle import switch_is_active

from api.helpers.geojson_polygon import InvalidPolygonGeoJSON
from api.helpers.geojson_zones import parse_zone_features
from api.helpers.location_filters import (
    clean_filters as clean_location_filters,
)
from api.helpers.zone_subdivision import subdivide_zone_records
from api.models.partner_field import PartnerField
from api.models.polygon_admin import PolygonForm
from api.models.sector import Sector
from api.models.zone_set import ZoneSet
from api.partner_fields.registry import (
    ZONE_SETS_SWITCH,
    system_partner_field_registry,
)


class ZoneSetForm(forms.ModelForm):
    """
    Admin form for creating and editing zone sets.

    Zones are not edited as rows: staff upload a GeoJSON
    FeatureCollection and, for a set feeding a string field, name the
    feature property that supplies each zone's value; a set feeding an
    object field reads one feature property per key of the field's
    JSON schema instead (OSDEV-3659). The whole file is parsed,
    validated and cut into storage pieces here, in `clean`, before
    anything is saved — a
    bad file, or a feature PostGIS cannot cut, becomes an ordinary red
    form error and the set's existing zones are left untouched. The
    pieces are handed to `ZoneSetAdmin.save_model`, which swaps them
    in atomically.
    """

    geojson_file = forms.FileField(
        required=False,
        help_text=(
            'Upload a .geojson/.json FeatureCollection with one Polygon '
            'or MultiPolygon feature per zone. Required when creating a '
            'set. When editing, leave empty to keep the current zones; '
            'uploading a new file replaces them all. Features are kept '
            'separate (not merged); if zones overlap, the feature that '
            'comes first in the file wins. Large features are stored '
            'as several small pieces that share the feature\'s value, '
            'so a dissolved layer performs the same as one of many '
            'small features. For an "object" partner field, each '
            'feature must carry a property named after every key the '
            'field\'s JSON schema lists as required; other schema keys '
            'are served when present.'
        ),
    )

    # Same cap as polygon uploads: a bigger file almost certainly means
    # an unsimplified export. Whether a set can be assembled from
    # several files is still an open question (OSDEV-3551).
    GEOJSON_FILE_MAX_BYTES = PolygonForm.GEOJSON_FILE_MAX_BYTES

    class Meta:
        model = ZoneSet
        # `filters` is deliberately not a form field: it is built from
        # the three filter_* fields below (see `_post_clean`), so staff
        # pick sectors from a list and type product names instead of
        # editing JSON.
        fields = (
            'name', 'description', 'partner_field', 'value_property',
            'active',
        )

    # The filter keys that have no dedicated field on this form. They
    # stay editable as JSON in `filter_other` so a set keeps every
    # filter polygons allow, without a screen per key.
    OTHER_FILTER_KEYS = (
        'country', 'facility_type', 'processing_type', 'parent_company',
    )

    filter_sectors = forms.MultipleChoiceField(
        required=False,
        label='Filter: sectors',
        # The admin's own searchable picker (the one the sector group
        # screen uses): every OS Hub sector on the left with a search
        # box, the chosen ones on the right. Far easier to use than a
        # plain list box with 100+ entries.
        widget=FilteredSelectMultiple('sectors', is_stacked=False),
        help_text=(
            'Optional. Choose any number of sectors from the full OS '
            'Hub sector list: search, then double-click a sector (or '
            'use the arrow) to move it to "Chosen sectors". The '
            'dataset shows only on locations in at least one chosen '
            'sector. If product types (or another filter) are also '
            'set, a location must match ALL of the filled boxes: the '
            'boxes combine with AND, and the values inside one box are '
            'alternatives. Leave the chosen box empty for no sector '
            'filter.'
        ),
    )
    filter_product_types = forms.CharField(
        required=False,
        max_length=10000,
        label='Filter: product types',
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'sugar\nsugarcane\nsugar cane',
        }),
        help_text=(
            'Optional. Type ONE product type per line: press Enter '
            'between products. Do not use commas, semicolons or '
            'bullets. Example (three lines): sugar / sugarcane / sugar '
            'cane. A location that has ANY of the listed products '
            'matches. Capital letters do not matter (Sugar Cane and '
            'sugar cane are the same), but everything else must match: '
            'spaces, hyphens and plurals, so sugarcane, sugar cane and '
            'sugar-cane are three different entries and "sugar" does '
            'not match "sugarcane". Extra spaces at the start or end '
            'of a line and blank lines are ignored. If a sector is also '
            'selected, a location must match both. Leave empty for no '
            'product filter.'
        ),
    )
    filter_other = forms.CharField(
        required=False,
        max_length=5000,
        label='Filter: other (advanced)',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': '{"country": ["KH", "ID"]}',
        }),
        help_text=(
            'Optional, for developers and careful editors. JSON for the '
            'remaining filters. Allowed keys: country (two-letter '
            'codes), facility_type, processing_type, parent_company. '
            'Each key takes a list in square brackets with each value '
            'in double quotes and commas between values. Example: '
            '{"country": ["KH", "ID"]}. Leave empty for none. Use the '
            'two boxes above for sector and product type.'
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_filter_fields()
        # The default manager hides inactive partner fields, which
        # would make a set whose field was later deactivated impossible
        # to edit or retire (the saved choice is "not valid"), and
        # would stop a dataset being staged against a field that is
        # not switched on yet.
        self.fields['partner_field'].queryset = (
            PartnerField.objects.get_all_including_inactive()
        )
        # Filled by clean() when a file is uploaded with the pieces to
        # store (see api.helpers.zone_subdivision); None means "keep
        # the existing zones".
        self.parsed_zones = None

    def clean_partner_field(self):
        """
        Check the linked field can carry a zone value.

        The provider emits a plain string (`raw_value`) for a string
        field and one value per schema key (`raw_values`) for an
        object field, so the field must be one of those two: an
        int/float field would serve a mis-shaped value to the API, and
        an object field without a schema gives the page nothing to
        render by and the upload nothing to validate against. And it
        must not be a field one of the hard-wired providers already
        serves, or the registry would yield two providers for one name.
        """
        partner_field = self.cleaned_data.get('partner_field')
        if partner_field is None:
            return partner_field
        if partner_field.type == PartnerField.OBJECT:
            if not partner_field.object_schema_properties():
                raise forms.ValidationError(
                    f'"{partner_field.name}" is an "{PartnerField.OBJECT}" '
                    'field without a JSON schema. A zone set fills an '
                    'object field one feature property per schema '
                    'property, so the schema is required: give the field '
                    'a schema with a "properties" map first.'
                )
        elif partner_field.type != PartnerField.STRING:
            raise forms.ValidationError(
                f'A zone set can only feed a "{PartnerField.STRING}" '
                f'partner field or an "{PartnerField.OBJECT}" field with '
                f'a JSON schema; "{partner_field.name}" is '
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

    def _init_filter_fields(self):
        """
        Fill the filter fields: the sector choices, and, when editing a
        saved set, what it already filters on.

        The choices are the sector taxonomy, so a set can only be
        limited to a sector name locations can carry. A sector a saved
        set uses that is no longer in the taxonomy is kept as a choice,
        so opening and saving the set does not silently drop it.
        """
        saved = (self.instance.filters or {}) if self.instance.pk else {}
        sector_names = list(
            Sector.objects.order_by('name').values_list('name', flat=True)
        )
        sector_names += [
            name for name in saved.get('sector', [])
            if name not in sector_names
        ]
        self.fields['filter_sectors'].choices = [
            (name, name) for name in sector_names
        ]
        if self.instance.pk and not self.is_bound:
            self.initial['filter_sectors'] = saved.get('sector', [])
            self.initial['filter_product_types'] = '\n'.join(
                saved.get('product_type', [])
            )
            other = {
                key: value for key, value in saved.items()
                if key in self.OTHER_FILTER_KEYS
            }
            self.initial['filter_other'] = (
                json.dumps(other) if other else ''
            )

    def clean_filter_product_types(self):
        """
        Split the product box into one product type per line.

        Blank lines are dropped and a repeated line is kept once. A
        line with a comma or semicolon in it is refused rather than
        guessed at: it almost always means several products typed on
        one line, and splitting or keeping it would both quietly
        filter on the wrong text (matching is exact apart from
        capitals, which the shared filter helper lower-cases).
        """
        products = []
        for line in self.cleaned_data['filter_product_types'].splitlines():
            line = line.strip()
            if not line:
                continue
            if ',' in line or ';' in line:
                raise forms.ValidationError(
                    f'"{line}" has a comma or semicolon. Put each '
                    'product type on its own line (press Enter between '
                    'them), without commas.'
                )
            if line not in products:
                products.append(line)
        return products

    def clean_filter_other(self):
        """
        Parse the advanced box: JSON for the filters that have no field
        of their own. Sector and product type must be set in their own
        boxes so a value cannot be entered twice in two places.
        """
        raw = self.cleaned_data['filter_other'].strip()
        if not raw:
            return {}
        try:
            other = json.loads(raw)
        except ValueError as exc:
            raise forms.ValidationError(
                f'Not valid JSON: {exc}. Example: {{"country": ["KH"]}}'
            ) from exc
        if not isinstance(other, dict):
            raise forms.ValidationError(
                'Use a JSON object, e.g. {"country": ["KH"]}.'
            )
        misplaced = [key for key in other if key not in self.OTHER_FILTER_KEYS]
        if misplaced:
            raise forms.ValidationError(
                f'{", ".join(misplaced)} cannot be set here. Use the '
                'sector and product type boxes for those; this box takes '
                f'only: {", ".join(self.OTHER_FILTER_KEYS)}.'
            )
        return other

    def _post_clean(self):
        """
        Combine the filter fields into the set's `filters` setting.

        Runs after the model form has copied the other fields onto the
        instance, so this assignment is the one that sticks. The result
        goes through the same check polygons use
        (`api.helpers.location_filters`), so an empty list or blank
        value is a form error here, not a field that quietly never
        shows. The filters are applied to each location when it is
        served, not stored with the zones, so editing them needs no
        re-upload.
        """
        super()._post_clean()
        if self.errors:
            return
        filters = dict(self.cleaned_data.get('filter_other') or {})
        if self.cleaned_data.get('filter_sectors'):
            filters['sector'] = list(self.cleaned_data['filter_sectors'])
        if self.cleaned_data.get('filter_product_types'):
            filters['product_type'] = self.cleaned_data[
                'filter_product_types'
            ]
        try:
            self.instance.filters = clean_location_filters(filters)
        except ValueError as exc:
            self.add_error(None, str(exc))

    def clean(self):
        """
        Parse the uploaded file (if any) into the zone pieces to store.

        A new set must come with a file. An existing set may be edited
        without one, in which case its zones are kept — unless the
        value property changed, because the stored labels were read
        with the old key and would no longer match, or the set moved
        to, from or between object fields, because the stored zones
        were validated against (and are served by) the old field's
        schema; re-uploading makes the change explicit.

        The value property is required only for a string field: an
        object field reads one feature property per schema key, so
        whatever was typed is cleared rather than stored as a stale
        setting.
        """
        cleaned_data = super().clean()
        geojson_file = cleaned_data.get('geojson_file')
        partner_field = cleaned_data.get('partner_field')
        feeds_object = (
            partner_field is not None
            and partner_field.type == PartnerField.OBJECT
        )

        if feeds_object:
            cleaned_data['value_property'] = None
        elif (
            not cleaned_data.get('value_property')
            and 'partner_field' not in self.errors
        ):
            self.add_error(
                'value_property',
                'Choose which feature property supplies the zone value. '
                'Only a set that feeds an "object" partner field can '
                'leave this empty.'
            )
        value_property = cleaned_data.get('value_property')

        if not geojson_file:
            if not self.instance.pk:
                raise forms.ValidationError(
                    'Upload a GeoJSON FeatureCollection file.'
                )
            if not self.instance.zones.exists():
                return cleaned_data
            if (
                'value_property' in self.changed_data
                and 'value_property' not in self.errors
                and not feeds_object
            ):
                self.add_error(
                    'value_property',
                    'Upload the file again when changing the value '
                    'property, so every zone is re-read with the new '
                    'key.'
                )
            if self._field_change_needs_reupload(partner_field):
                self.add_error(
                    'partner_field',
                    'Upload the file again when linking an "object" '
                    'partner field or replacing one, so every zone is '
                    're-read against the new field\'s schema.'
                )
            return cleaned_data

        if 'value_property' in self.errors:
            # The file cannot be read by a key that is missing; the
            # error above already says what to fix.
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

        # Subdividing here rather than at save time means a feature
        # PostGIS returns no piece for is reported like any other bad
        # file, instead of surfacing after validation as a server
        # error once the set itself has been saved.
        try:
            if feeds_object:
                records = parse_zone_features(
                    raw, schema=partner_field.json_schema
                )
            else:
                records = parse_zone_features(raw, value_property)
            self.parsed_zones = subdivide_zone_records(records)
        except InvalidPolygonGeoJSON as exc:
            raise forms.ValidationError(str(exc)) from exc

        return cleaned_data

    def _field_change_needs_reupload(self, partner_field):
        """
        Whether swapping the linked field invalidates the stored zones.

        Zones feeding an object field were validated against that
        field's schema and are served by its keys; zones feeding a
        string field carry one label. So a set that has zones and
        moves to an object field, away from one, or from one object
        field to another must be re-read from the file. Moving between
        string fields (or from no field to a string field) keeps the
        same shape and needs nothing.

        Args:
            partner_field: The field the form is about to link, or
                None. The instance still holds the saved field, since
                the model form only copies cleaned data onto it after
                `clean` returns.
        """
        if 'partner_field' not in self.changed_data:
            return False
        original = self.instance.partner_field
        return any(
            field is not None and field.type == PartnerField.OBJECT
            for field in (original, partner_field)
        )


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
        'filter_sectors', 'filter_product_types', 'filter_other',
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
        """Annotate the feature count so the list view needs one query."""
        return super().get_queryset(request).annotate(
            _zone_count=Count('zones__feature_index', distinct=True)
        )

    @admin.display(description='Zones', ordering='_zone_count')
    def zone_count(self, obj):
        """
        Number of zones in the set, counting source features rather
        than the pieces they are stored as (from the list annotation).
        """
        count = getattr(obj, '_zone_count', None)
        if count is None:
            return obj.zones.aggregate(
                n=Count('feature_index', distinct=True)
            )['n']
        return count

    @admin.display(description='Current zones')
    def zone_summary(self, obj):
        """
        One-line description of the saved zones (feature and piece
        counts, distinct labels), so staff can sanity-check an upload
        at a glance.

        Args:
            obj: The ZoneSet being displayed, or an unsaved instance on
                the add page (which has no zones yet).
        """
        if not obj or not obj.pk:
            return '(no zones saved yet)'
        zones = obj.zones.all()
        counts = zones.aggregate(
            features=Count('feature_index', distinct=True),
            pieces=Count('id'),
        )
        if counts['pieces'] == 0:
            return '(no zones saved yet)'
        if obj.feeds_object_field:
            # An object field is served one value per schema key, so
            # the keys are what staff need to check against the
            # field's schema and the page; the label is only the first
            # required property and says little on its own.
            return (
                f'{counts["features"]} zone(s) stored as '
                f'{counts["pieces"]} piece(s); serving schema keys: '
                f'{", ".join(obj.schema_keys)}'
            )
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
        return (
            f'{counts["features"]} zone(s) stored as {counts["pieces"]} '
            f'piece(s); labels: {shown}'
        )

    def save_model(self, request, obj, form, change):
        """
        Save the set, then swap in the uploaded zones if there are any.

        Django wraps the whole admin save in one transaction, and
        `replace_zones` is atomic on its own as well, so the old zones
        keep serving right up until the new ones are committed. The
        search-side membership (`FacilityIndex.zone_set_ids`) is
        recomputed in the background once they are (see
        `ZoneSet.replace_zones`), so staff are told the two surfaces
        will disagree briefly.
        """
        super().save_model(request, obj, form, change)
        if form.parsed_zones is not None:
            obj.replace_zones(form.parsed_zones)
            messages.info(request, (
                'Zones saved. Which locations the search filter returns '
                'for this dataset is being recomputed in the background '
                '(a pass over every indexed location); until it finishes, '
                'Spotlight Partners search results reflect the previous '
                'zones. Location pages show the new zones at once.'
            ))


class ZoneAdmin(admin.ModelAdmin):
    """
    Read-only listing of zones, for checking what an upload produced.
    One row per stored piece: a feature cut into several pieces at
    upload appears once per piece, with the same feature index and
    label. Zones are created and replaced only through their zone set.
    """

    list_display = (
        'zone_set', 'feature_index', 'piece_index', 'label', 'created_at',
    )
    list_filter = ('zone_set',)
    search_fields = ('value__label',)
    readonly_fields = ('zone_set', 'feature_index', 'piece_index', 'label',
                       'value', 'created_at')
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
