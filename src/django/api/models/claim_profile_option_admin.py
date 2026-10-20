from django.contrib import admin, messages
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from api.models.facility.facility_claim import FacilityClaim


class ClaimProfileOptionAdmin(SimpleHistoryAdmin):
    """
    Admin for the claim form's affiliation and certification options.

    Staff add, rename, reorder and deactivate options here. Options are
    never deleted (the name is the value stored on claims); renaming one
    rewrites every claim that holds the old name.
    """

    list_display = ('name', 'is_active', 'sort_order', 'claims_count',
                    'updated_at')
    list_editable = ('is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('claims_count', 'created_at', 'updated_at')
    fields = ('name', 'is_active', 'sort_order', 'claims_count',
              'created_at', 'updated_at')

    @admin.display(description='Claims using it')
    def claims_count(self, obj):
        """How many claims (any status) currently hold this option."""
        if not obj or not obj.pk:
            return 0
        return FacilityClaim.objects.filter(
            **{f'{obj.claim_field}__contains': [obj.name]}
        ).count()

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        if obj is not None and 'name' in form.base_fields:
            form.base_fields['name'].help_text = format_html(
                '{}<br><strong>Renaming updates {} existing claim(s) that '
                'hold "{}".</strong>',
                form.base_fields['name'].help_text,
                self.claims_count(obj),
                obj.name,
            )
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        renamed = getattr(obj, 'renamed_claims_count', 0)
        if change and 'name' in form.changed_data:
            messages.info(
                request,
                f'Renamed to "{obj.name}": {renamed} existing claim(s) '
                'updated. Their production locations will be re-indexed '
                'on the next search sync.',
            )


class ClaimAffiliationAdmin(ClaimProfileOptionAdmin):
    pass


class ClaimCertificationAdmin(ClaimProfileOptionAdmin):
    pass
