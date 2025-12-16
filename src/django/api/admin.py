import json

from django import forms
from django.urls import path
from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from api.models.sector_group import SectorGroup
from api.models.partner_field import PartnerField
from api.models.wage_indicator_country_data import WageIndicatorCountryData
from api.models.us_county_tigerline import USCountyTigerline
from allauth.account.models import EmailAddress
from simple_history.admin import SimpleHistoryAdmin
from waffle.models import Flag, Sample, Switch
from waffle.admin import FlagAdmin, SampleAdmin, SwitchAdmin
from ckeditor.widgets import CKEditorWidget
from jsoneditor.forms import JSONEditor

from api import models

from api.reports import get_report_names, run_report


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


class FacilityHistoryAdmin(SimpleHistoryAdmin):
    history_list_display = ('name', 'address', 'location')

    readonly_fields = ('created_from',)


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
    readonly_fields = ('facility', 'pretty_processing_results', 'source')

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


class PartnerFieldAdminForm(forms.ModelForm):
    source_by = forms.CharField(
        required=False,
        widget=CKEditorWidget()
    )
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
        model = PartnerField
        fields = [
            'name',
            'type',
            'unit',
            'label',
            'source_by',
            'base_url',
            'display_text',
            'json_schema'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PartnerFieldAdmin(admin.ModelAdmin):
    form = PartnerFieldAdminForm
    list_display = ('name', 'type', 'label', 'unit', 'source_by', 'created_at')
    search_fields = ('name', 'type', 'label', 'unit', 'source_by')
    readonly_fields = ('uuid', 'created_at', 'updated_at')

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/partner_field_admin.js',
        )


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'primary', 'verified')
    search_fields = ('email', 'user__email')
    list_filter = ('verified', 'primary')


class WageIndicatorCountryDataAdmin(admin.ModelAdmin):
    list_display = ('country_code', 'living_wage_link_national',
                    'minimum_wage_link_english', 'minimum_wage_link_national')
    search_fields = ('country_code',)
    readonly_fields = ('country_code', 'created_at', 'updated_at')


class USCountyTigerlineAdmin(admin.ModelAdmin):
    list_display = ('geoid', 'name')
    search_fields = ('geoid', 'name')
    readonly_fields = ('geoid', 'name', 'geometry','created_at', 'updated_at')


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
admin_site.register(EmailAddress, EmailAddressAdmin)
admin_site.register(WageIndicatorCountryData, WageIndicatorCountryDataAdmin)
admin_site.register(USCountyTigerline, USCountyTigerlineAdmin)
