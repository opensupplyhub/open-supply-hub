import json
import logging

from django import forms
from django.db import transaction
from django.urls import path
from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.gis.admin import GISModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from api.helpers.geojson_polygon import (
    InvalidPolygonGeoJSON,
    parse_polygon_geojson,
)
from api.models.polygon import Polygon
from api.models.sector_group import SectorGroup
from api.models.partner_field_group import PartnerFieldGroup
from api.models.wage_indicator_country_data import WageIndicatorCountryData
from api.models.wage_indicator_link_text_config import (
    WageIndicatorLinkTextConfig
)
from api.models.us_county_tigerline import USCountyTigerline
from api.models.partner_data_file_upload import PartnerDataFileUpload
from api.partner_data_file_upload.batch import (
    submit_partner_data_file_upload_job,
)
from api.partner_data_file_upload.errors import format_upload_processing_error
from allauth.account.models import EmailAddress
from simple_history.admin import SimpleHistoryAdmin
from waffle import switch_is_active
from waffle.models import Flag, Sample, Switch
from waffle.admin import FlagAdmin, SampleAdmin, SwitchAdmin

from api import models
from api.models.partner_field import PartnerField
from api.models.partner_field_admin import PartnerFieldAdmin

from api.reports import get_report_names, run_report

logger = logging.getLogger(__name__)


class ApiAdminSite(AdminSite):
    site_header = 'Open Supply Hub Admin'

    def get_urls(self):
        base_urls = super(ApiAdminSite, self).get_urls()
        urls = [
            path('reports/<str:name>/',
                 self.admin_view(self.report_view)),
            path('reports/', self.admin_view(self.reports_list_view),
                 name='reports')
        ]
        return urls + base_urls

    def report_view(self, request, name):
        context = run_report(name)
        return render(request, 'reports/report.html', context)

    def reports_list_view(self, request):
        return render(request, 'reports/reports.html', {
            'names': get_report_names()
        })


admin_site = ApiAdminSite()


class OarUserAdmin(UserAdmin):
    exclude = ('last_name', 'date_joined', 'first_name', 'username')
    fieldsets = (
        (None, {'fields': ('email', 'is_staff', 'is_superuser', 'is_active',
                           'should_receive_newsletter',
                           'has_agreed_to_terms_of_service',
                           'groups', 'burst_rate', 'sustained_rate',
                           'data_upload_rate')}),
    )
    search_fields = ('email',)
    list_display = ('email', 'is_active')


class FacilityHistoryAdmin(GISModelAdmin, SimpleHistoryAdmin):
    history_list_display = ('name', 'address', 'location')

    readonly_fields = ('created_from',)

    gis_widget_kwargs = {
        'attrs': {
            'map_width': 600,
            'map_height': 400,
        }
    }

    class Media:
        css = {'all': ('admin/css/gis_map_fix.css',)}


class FacilityListAdmin(admin.ModelAdmin):
    readonly_fields = ('replaced_by_link',)

    @admin.display(description='Replaced by')
    def replaced_by_link(self, obj):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse(
                    'admin:api_facilitylist_change',
                    args=[obj.replaced_by.id]
                ),
                obj.replaced_by
            )
        )


class FacilityListItemAdmin(admin.ModelAdmin):
    exclude = ('processing_results',)
    readonly_fields = (
        'facility',
        'moderation_event',
        'pretty_processing_results',
        'source',
    )

    def pretty_processing_results(self, instance):
        # The processing_results field is populated exclusively from processing
        # code so we are not in danger of rendering potentially unsafe user
        # submitted content
        return mark_safe('<pre>{}</pre>'.format(
            json.dumps(instance.processing_results, indent=2)))

    pretty_processing_results.short_description = 'Processing results'


class FacilityMatchAdmin(SimpleHistoryAdmin):
    exclude = ('results',)
    history_list_display = ('status', 'facility')
    readonly_fields = ('facility_list_item', 'facility',
                       'confidence', 'status', 'pretty_results')

    def pretty_results(self, instance):
        # The status field is populated exclusively from processing code so we
        # are not in danger of rendering potentially unsafe user submitted
        # content
        return mark_safe('<pre>{}</pre>'.format(
            json.dumps(instance.results, indent=2)))

    pretty_results.short_description = 'Results'


class ContributorAdmin(SimpleHistoryAdmin):
    history_list_display = ('is_verified', 'verification_notes')
    search_fields = ('name', 'admin__email')
    filter_horizontal = ('partner_fields',)

    def get_ordering(self, request):
        return ['name']


class FacilityClaimAdmin(SimpleHistoryAdmin):
    autocomplete_fields = ('parent_company', )
    history_list_display = ('id', 'contact_person', 'created_at', 'status')
    readonly_fields = ('contributor', 'facility', 'status_change_reason',
                       'status_change_by', 'status_change_date', 'status')


class FacilityClaimReviewNoteAdmin(SimpleHistoryAdmin):
    history_list_display = ('id', 'created_at')
    readonly_fields = ('claim', 'author')


class FacilityAliasAdmin(SimpleHistoryAdmin):
    history_list_display = ('os_id', 'facility')
    readonly_fields = ('os_id', 'facility', 'reason')


class SourceAdmin(admin.ModelAdmin):
    autocomplete_fields = ('contributor', )
    readonly_fields = ('source_type', 'facility_list', 'create')
    list_filter = ('source_type', 'contributor')


class RequestLogAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'token', 'method', 'path', 'response_code',
                       'created_at')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='',
                        extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(RequestLogAdmin, self).changeform_view(
            request, object_id, extra_context=extra_context)


class ApiLimitAdmin(admin.ModelAdmin):
    autocomplete_fields = ('contributor', )
    history_list_display = ('contributor', 'period_limit', 'created_at',
                            'updated_at', 'period_start_date')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["contributor", ]
        else:
            return []


class FacilityDownloadLimitAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'free_download_records',
                    'paid_download_records',
                    'updated_at',
                    'purchase_date',
                    )
    search_fields = ('user__email', 'user__contributor__name')
    autocomplete_fields = ('user',)

    def get_ordering(self, request):
        return ('user',)


class ExtendedFieldAdmin(admin.ModelAdmin):
    readonly_fields = ('contributor', 'facility', 'facility_list_item',
                       'facility_claim')


class SectorAdmin(admin.ModelAdmin):
    filter_horizontal = ('groups',)

    def get_ordering(self, request):
        return ['name']


class SectorGroupAdmin(admin.ModelAdmin):
    readonly_fields = ('related_sectors',)

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields if obj else []

    def get_fields(self, request, obj=None):
        fields = ['name']
        if obj:
            fields.append('related_sectors')
        return fields

    def related_sectors(self, obj):
        return obj.related_sectors()

    related_sectors.short_description = 'Related Sectors'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        if obj and obj.sectors.exists():
            messages.warning(
                request,
                _(
                    "Sector group '%s' cannot be deleted because it is "
                    "associated with one or more sectors."
                )
                % obj,
            )
            return False
        return super().has_delete_permission(request, obj)

    def get_ordering(self, request):
        return ['name']


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'primary', 'verified')
    search_fields = ('email', 'user__email')
    list_filter = ('verified', 'primary')


class WageIndicatorCountryDataAdmin(admin.ModelAdmin):
    list_display = ('country_code', 'living_wage_link_national',
                    'minimum_wage_link_english', 'minimum_wage_link_national')
    search_fields = ('country_code',)
    fields = ('country_code', 'living_wage_link_national',
              'minimum_wage_link_english', 'minimum_wage_link_national',
              'created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        '''
        Make country_code readonly when editing, but editable when creating.
        '''
        if obj:
            return ('country_code', 'created_at', 'updated_at')

        return ('created_at', 'updated_at')


class WageIndicatorLinkTextConfigAdmin(admin.ModelAdmin):
    list_display = ('link_type', 'display_text')
    search_fields = ('link_type', 'display_text')


class USCountyTigerlineAdmin(admin.ModelAdmin):
    list_display = ('geoid', 'name')
    search_fields = ('geoid', 'name')
    readonly_fields = ('created_at', 'updated_at')


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


# Name of the waffle switch gating the polygon admin. Flipping it in
# the admin (Waffle > Switches) shows or hides the whole Polygons
# section immediately — no deploy or restart needed.
POLYGONS_SWITCH = 'polygons'


def code_referenced_polygon_names():
    """
    Return the polygon names that code depends on.

    System partner field providers that are driven by polygons declare
    the names they look up in a `POLYGON_NAMES` class attribute.
    Renaming or deleting one of those polygons silently severs the
    code link (the feature goes dormant with a logged warning), so the
    admin uses this list to warn staff at the moment of the edit.
    """
    from api.partner_fields.registry import system_partner_field_registry
    names = set()
    for provider in system_partner_field_registry.providers:
        names.update(getattr(provider, 'POLYGON_NAMES', []))
    return names


class PolygonAdmin(admin.ModelAdmin):
    """
    Admin for Polygon boundaries, gated behind the `polygons` waffle
    switch: every permission method below requires the switch to be
    active, so when it is off the section is hidden from the admin
    index and direct URLs are refused.
    """

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

    def save_model(self, request, obj, form, change):
        """Warn when a rename is about to sever a code reference."""
        if change:
            original = Polygon.objects.filter(pk=obj.pk).first()
            referenced = code_referenced_polygon_names()
            if (
                original is not None
                and original.name != obj.name
                and original.name in referenced
            ):
                messages.warning(
                    request,
                    f"Heads up: code references this polygon by its old "
                    f"name '{original.name}'. The feature using it will "
                    f"stop finding it until the code is updated or the "
                    f"name is restored."
                )
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """Warn when deleting a polygon that code references."""
        self.__warn_if_referenced(request, [obj])
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Warn on bulk deletes that include code-referenced polygons."""
        self.__warn_if_referenced(request, queryset)
        super().delete_queryset(request, queryset)

    def __warn_if_referenced(self, request, polygons):
        referenced = code_referenced_polygon_names()
        for polygon in polygons:
            if polygon.name in referenced:
                messages.warning(
                    request,
                    f"Heads up: code references the polygon "
                    f"'{polygon.name}'. Deleting it will make the "
                    f"feature using it go dormant (with a logged "
                    f"warning) until a polygon with this name exists "
                    f"again."
                )

    def has_module_permission(self, request):
        return (
            switch_is_active(POLYGONS_SWITCH)
            and super().has_module_permission(request)
        )

    def has_view_permission(self, request, obj=None):
        return (
            switch_is_active(POLYGONS_SWITCH)
            and super().has_view_permission(request, obj)
        )

    def has_add_permission(self, request):
        return (
            switch_is_active(POLYGONS_SWITCH)
            and super().has_add_permission(request)
        )

    def has_change_permission(self, request, obj=None):
        return (
            switch_is_active(POLYGONS_SWITCH)
            and super().has_change_permission(request, obj)
        )

    def has_delete_permission(self, request, obj=None):
        return (
            switch_is_active(POLYGONS_SWITCH)
            and super().has_delete_permission(request, obj)
        )


class PartnerDataFileUploadAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "contributor",
        "status",
        "batch_job_id",
        "created_by",
        "created_at",
        "processed_at",
    )
    list_filter = ("status", "contributor")
    search_fields = (
        "uuid",
        "google_drive_file_link",
        "batch_job_id",
        "contributor__name",
        "contributor__admin__email",
        "created_by__email",
    )
    readonly_fields = (
        "uuid",
        "status",
        "batch_job_id",
        "created_by",
        "processed_at",
        "processing_error",
        "created_at",
        "updated_at",
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            obj.status = PartnerDataFileUpload.Status.PROCESSING
            obj.processing_error = ""
        super().save_model(request, obj, form, change)

        if change:
            return

        upload_uuid = obj.uuid

        def enqueue_batch_job():
            upload = PartnerDataFileUpload.objects.get(pk=upload_uuid)
            try:
                job_id = submit_partner_data_file_upload_job(upload_uuid)
                upload.batch_job_id = job_id
                upload.save(update_fields=["batch_job_id", "updated_at"])
                messages.success(
                    request,
                    (
                        "Partner data file was queued for moderation "
                        f"ingestion. Batch job ID: {job_id}"
                    ),
                )
            except Exception as error:
                error_message = format_upload_processing_error(error)
                upload.status = PartnerDataFileUpload.Status.FAILED
                upload.processing_error = error_message
                upload.save(
                    update_fields=[
                        "status",
                        "processing_error",
                        "updated_at",
                    ]
                )
                messages.error(
                    request,
                    (
                        "Partner data file was saved but "
                        "Batch submission failed. "
                        f"Error: {error_message}"
                    ),
                )

        transaction.on_commit(enqueue_batch_job)


admin_site.register(models.Version)
admin_site.register(models.User, OarUserAdmin)
admin_site.register(models.Contributor, ContributorAdmin)
admin_site.register(models.FacilityList, FacilityListAdmin)
admin_site.register(models.ExtendedField, ExtendedFieldAdmin)
admin_site.register(models.Source, SourceAdmin)
admin_site.register(models.FacilityListItem, FacilityListItemAdmin)
admin_site.register(models.Facility, FacilityHistoryAdmin)
admin_site.register(models.FacilityMatch, FacilityMatchAdmin)
admin_site.register(models.FacilityClaim, FacilityClaimAdmin)
admin_site.register(models.FacilityClaimReviewNote,
                    FacilityClaimReviewNoteAdmin)
admin_site.register(models.FacilityAlias, FacilityAliasAdmin)
admin_site.register(Flag, FlagAdmin)
admin_site.register(Sample, SampleAdmin)
admin_site.register(Switch, SwitchAdmin)
admin_site.register(Group)
admin_site.register(models.RequestLog, RequestLogAdmin)
admin_site.register(models.ApiLimit, ApiLimitAdmin)
admin_site.register(models.Sector, SectorAdmin)
admin_site.register(SectorGroup, SectorGroupAdmin)
admin_site.register(models.FacilityDownloadLimit, FacilityDownloadLimitAdmin)
admin_site.register(PartnerField, PartnerFieldAdmin)
admin_site.register(PartnerFieldGroup)
admin_site.register(EmailAddress, EmailAddressAdmin)
admin_site.register(WageIndicatorCountryData, WageIndicatorCountryDataAdmin)
admin_site.register(
    WageIndicatorLinkTextConfig, WageIndicatorLinkTextConfigAdmin
)
admin_site.register(USCountyTigerline, USCountyTigerlineAdmin)
admin_site.register(Polygon, PolygonAdmin)
admin_site.register(models.PartnerDataFileUpload, PartnerDataFileUploadAdmin)
