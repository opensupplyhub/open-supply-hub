from django import forms
from django.contrib import admin, messages
from django.db.models import Count
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.html import format_html
from waffle import switch_is_active

from api.helpers.geojson_polygon import InvalidPolygonGeoJSON
from api.helpers.geojson_zones import parse_zone_features
from api.helpers.zone_subdivision import subdivide_zone_records
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
    FeatureCollection and, for a set feeding a string field, name the
    feature property that supplies each zone's value; a set feeding an
    object field reads one feature property per key of the field's
    JSON schema instead (OSDEV-3659). The whole file is parsed,
    validated and cut into storage pieces here, in `clean`, before
    anything is saved — a
    bad file, or a feature PostGIS cannot cut, becomes an ordinary red
    form error and the set's existing zones are left untouched. The
    pieces are handed to `ZoneSetAdmin.save_model`, which either swaps
    them in atomically or, in "Add to the existing zones" mode
    (OSDEV-3812), appends them after the stored zones, so a dataset
    too large for one file under the cap can be loaded as several.
    """

    UPLOAD_MODE_REPLACE = 'replace'
    UPLOAD_MODE_ADD = 'add'

    geojson_file = forms.FileField(
        required=False,
        help_text=(
            'Upload a .geojson/.json FeatureCollection with one Polygon '
            'or MultiPolygon feature per zone. Required when creating a '
            'set. When editing, leave empty to keep the current zones; '
            'a new file replaces them all or is added after them, as '
            'the upload mode below says. Features are kept '
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
    upload_mode = forms.ChoiceField(
        required=False,
        initial=UPLOAD_MODE_REPLACE,
        choices=(
            (UPLOAD_MODE_REPLACE, 'Replace all zones'),
            (UPLOAD_MODE_ADD, 'Add to the existing zones'),
        ),
        widget=forms.RadioSelect,
        label='Upload mode',
        help_text=(
            'What the uploaded file does to the zones already stored; '
            'ignored when no file is uploaded. "Replace all zones" '
            'discards them and keeps only this file\'s. "Add to the '
            'existing zones" keeps them and stores this file\'s zones '
            'after them, so a dataset larger than the per-file limit '
            'can be loaded into one set as several files, each under '
            'the limit. An added file is checked exactly as a '
            'replacement is (size, geometry, properties); one that '
            'fails leaves the stored zones untouched. Where zones from '
            'two uploads overlap, the earlier upload wins, so upload '
            'the file whose values should take precedence first. '
            'Changing the value property, or linking or replacing an '
            '"object" partner field, requires a replace. To take one '
            'upload\'s zones out of a set, replace the whole set.'
        ),
    )

    # Same cap as polygon uploads: a bigger file almost certainly means
    # an unsimplified export. A dataset that does not fit under it is
    # loaded as several files in "Add to the existing zones" mode
    # (OSDEV-3812); raising the cap is not the answer, because parsing
    # and cutting a file of several tens of MB would outlast
    # CloudFront's 30 s origin timeout and show staff a 504 while the
    # save completed behind it.
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
        # Filled by clean() when a file is uploaded with the pieces to
        # store (see api.helpers.zone_subdivision); None means "keep
        # the existing zones". `adds_to_existing` says whether they go
        # after the stored zones (add mode on an existing set) or in
        # their place.
        self.parsed_zones = None
        self.adds_to_existing = False

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

    def clean(self):
        """
        Parse the uploaded file (if any) into the zone pieces to store.

        A new set must come with a file. An existing set may be edited
        without one, in which case its zones are kept — unless the
        value property changed, because the stored labels were read
        with the old key and would no longer match, or the set moved
        to, from or between object fields, because the stored zones
        were validated against (and are served by) the old field's
        schema; re-uploading makes the change explicit. The same two
        changes are refused together with a file in add mode
        (OSDEV-3812): the added file would be read with the new key or
        schema while the stored zones were read with the old, so the
        set must be replaced as a whole.

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
        # Add mode means something only for a set that exists; on a
        # new set there is nothing to add to and the file is stored as
        # a replace would store it.
        adding = (
            cleaned_data.get('upload_mode') == self.UPLOAD_MODE_ADD
            and bool(self.instance.pk)
        )

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

        if adding and self.instance.zones.exists():
            # Every stored zone was validated against, and is served
            # by, the key or schema the set has now; an added file
            # read by a new one would leave the set half one way and
            # half the other.
            if 'value_property' in self.changed_data and not feeds_object:
                self.add_error(
                    'value_property',
                    'Changing the value property requires a replace: '
                    'choose "Replace all zones" and upload the whole '
                    'set, so every zone is re-read with the new key.'
                )
            if self._field_change_needs_reupload(partner_field):
                self.add_error(
                    'partner_field',
                    'Linking an "object" partner field or replacing one '
                    'requires a replace: choose "Replace all zones" and '
                    'upload the whole set, so every zone is re-read '
                    'against the new field\'s schema.'
                )
            if self.errors:
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
        self.adds_to_existing = adding

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
        'geojson_file', 'upload_mode', 'zone_summary', 'active', 'uuid',
        'created_at', 'updated_at',
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
        Save the set, then store the uploaded zones if there are any:
        in place of the stored ones, or after them in add mode.

        Django wraps the whole admin save in one transaction, and
        `replace_zones` / `add_zones` are atomic on their own as well,
        so the old zones keep serving right up until the new ones are
        committed. The search-side membership
        (`FacilityIndex.zone_set_ids`) is recomputed in the background
        once they are (see `ZoneSet.replace_zones`), so staff are told
        the two surfaces will disagree briefly.
        """
        super().save_model(request, obj, form, change)
        if form.parsed_zones is None:
            return
        if form.adds_to_existing:
            first = obj.add_zones(form.parsed_zones)
            added = len({p['feature_index'] for p in form.parsed_zones})
            saved = (
                f'{added} zone(s) added to the set as feature(s) '
                f'{first}–{first + added - 1}; the set now holds '
                f'{obj.feature_count}.'
            )
        else:
            obj.replace_zones(form.parsed_zones)
            saved = 'Zones saved.'
        messages.info(request, (
            f'{saved} Which locations the search filter returns '
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
