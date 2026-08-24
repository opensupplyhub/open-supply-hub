from django import forms
from django.contrib import admin
from django.template.defaultfilters import filesizeformat

from api.helpers.geojson_polygon import (
    InvalidPolygonGeoJSON,
    parse_polygon_geojson,
)
from api.models.polygon import Polygon


class PolygonForm(forms.ModelForm):
    """
    Admin form for creating and editing Polygon boundaries.

    The geometry itself is not edited as a raw model field: staff
    provide it as GeoJSON, either by uploading a file or pasting text,
    and the form parses and validates it (via
    `api.helpers.geojson_polygon`) before anything is saved. Parsing
    problems come back as ordinary red form errors rather than 500s.
    """

    geojson_file = forms.FileField(
        required=False,
        help_text=(
            'Upload a .geojson/.json file containing a Polygon, '
            'MultiPolygon, Feature, or FeatureCollection geometry.'
        ),
    )
    geojson_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 10}),
        help_text=(
            'Or paste GeoJSON directly. Ignored if a file is uploaded. '
            'When editing, this shows the currently saved boundary; '
            'edit or replace it to change the boundary, or leave it '
            'unchanged (or blank) to keep it.'
        ),
    )

    # Boundaries larger than this are not echoed back into the text
    # box when editing, to keep the page loadable.
    GEOJSON_PREFILL_MAX_CHARS = 1_000_000

    # Cap uploads: anything bigger almost certainly means an
    # undissolved or unsimplified export, and the geometry would bloat
    # every containment query even if it parsed.
    GEOJSON_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB

    class Meta:
        model = Polygon
        fields = ('name', 'display_name', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # When editing an existing polygon, show its saved boundary in
        # the paste box so staff can see and tweak what is stored
        # (without this, the stored geometry would be invisible in the
        # admin). Very large boundaries are summarized instead so the
        # page stays loadable.
        if self.instance.pk and self.instance.geom:
            geojson = self.instance.geom.geojson
            if len(geojson) <= self.GEOJSON_PREFILL_MAX_CHARS:
                self.fields['geojson_text'].initial = geojson
            else:
                self.fields['geojson_text'].help_text = (
                    'The current boundary is too large to display here. '
                    'Paste or upload GeoJSON to replace it, or leave '
                    'blank to keep it.'
                )

    def clean(self):
        """
        Resolve which GeoJSON input to use and parse it into geometry.

        Precedence: an uploaded file wins over pasted text; if neither
        is provided while editing an existing polygon, the saved
        boundary is kept; if neither is provided on a brand-new
        polygon, that is an error (a polygon must have a boundary).
        """
        cleaned_data = super().clean()
        geojson_file = cleaned_data.get('geojson_file')
        geojson_text = cleaned_data.get('geojson_text')

        if geojson_file:
            if geojson_file.size > self.GEOJSON_FILE_MAX_BYTES:
                raise forms.ValidationError(
                    f'GeoJSON file is too large '
                    f'({filesizeformat(geojson_file.size)}; limit '
                    f'{filesizeformat(self.GEOJSON_FILE_MAX_BYTES)}). '
                    'Simplify the boundary (e.g. with mapshaper.org) '
                    'and try again.'
                )
            try:
                raw = geojson_file.read().decode('utf-8')
            except UnicodeDecodeError as exc:
                raise forms.ValidationError(
                    f'Could not read the file as UTF-8 text: {exc}'
                ) from exc
        elif geojson_text:
            raw = geojson_text
        elif self.instance.pk and self.instance.geom:
            return cleaned_data
        else:
            raise forms.ValidationError(
                'Upload a GeoJSON file or paste GeoJSON text.'
            )

        try:
            self.instance.geom = parse_polygon_geojson(raw)
        except InvalidPolygonGeoJSON as exc:
            raise forms.ValidationError(str(exc)) from exc

        return cleaned_data


class PolygonAdmin(admin.ModelAdmin):
    """Admin for Polygon boundaries."""

    form = PolygonForm
    list_display = (
        'name', 'display_name', 'boundary_summary', 'created_at',
        'updated_at',
    )
    search_fields = ('name', 'display_name', 'description')
    readonly_fields = (
        'uuid', 'boundary_summary', 'created_at', 'updated_at',
    )

    @admin.display(description='Boundary')
    def boundary_summary(self, obj):
        """
        One-line description of the saved geometry (part count, vertex
        count, and lon/lat extent), shown on the change page and as a
        list column so staff can sanity-check a boundary at a glance.

        Args:
            obj: The Polygon being displayed, or an unsaved instance
                on the add page (which has no boundary yet).
        """
        if not obj or not obj.pk or not obj.geom:
            return '(no boundary saved yet)'
        extent = ', '.join(f'{value:.3f}' for value in obj.geom.extent)
        return (
            f'{len(obj.geom)} part(s), {obj.geom.num_coords} vertices, '
            f'extent (lon/lat): {extent}'
        )
