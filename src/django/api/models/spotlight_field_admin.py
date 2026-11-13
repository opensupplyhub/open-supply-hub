"""
Django admin for Spotlight partner fields (OSDEV-3788).

Admins approve and activate the fields partners create, one at a time (the
inline on each field set) or all at once (the list actions), set the go-live
date, and see which partners have edited their fields most recently.
"""

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import F
from simple_history.admin import SimpleHistoryAdmin

from .spotlight_field import SpotlightField, SpotlightFieldProperty

GO_LIVE_WARNING = (
    'If you change this date, you may deactivate existing active data. '
    'Tick the box below to confirm you are sure.'
)


class EditedByPartnersFilter(admin.SimpleListFilter):
    """Show only field sets a partner has edited, most recent first."""

    title = 'edited by partners'
    parameter_name = 'edited_by_partners'

    def lookups(self, request, model_admin):
        """Offer a single "Yes" choice."""
        return (('yes', 'Edited by a partner'),)

    def queryset(self, request, queryset):
        """Keep only field sets with a recorded partner edit."""
        if self.value() == 'yes':
            return queryset.filter(last_partner_edit_at__isnull=False)
        return queryset


class SpotlightFieldPropertyInlineForm(forms.ModelForm):
    """
    Inline form for one field. Running the model's own checks here means an
    admin who ticks "active" on an unapproved field gets a clear message
    instead of an error page.
    """

    class Meta:
        model = SpotlightFieldProperty
        fields = ('name', 'display_name', 'approved', 'active')


class SpotlightFieldPropertyInline(admin.TabularInline):
    """Per-field approval and activation checkboxes."""

    model = SpotlightFieldProperty
    form = SpotlightFieldPropertyInlineForm
    extra = 0
    can_delete = False
    fields = ('name', 'display_name', 'field_type', 'approved', 'active',
              'last_partner_edit_at')
    readonly_fields = ('name', 'field_type', 'last_partner_edit_at')

    def has_add_permission(self, request, obj=None):
        """Partners create fields; admins only approve and activate them."""
        return False


class SpotlightFieldAdminForm(forms.ModelForm):
    """
    Field-set form that asks for confirmation before an existing go-live
    date is changed, because changing it can deactivate active fields.
    """

    confirm_date_change = forms.BooleanField(
        required=False,
        label='I understand this may deactivate active fields',
        help_text=GO_LIVE_WARNING,
    )

    class Meta:
        model = SpotlightField
        fields = ('go_live_date',)

    def clean(self):
        """Require the confirmation when a go-live date is being changed."""
        cleaned = super().clean()
        if self.instance.pk and 'go_live_date' in self.changed_data:
            has_active = self.instance.properties.filter(active=True).exists()
            if has_active and not cleaned.get('confirm_date_change'):
                raise ValidationError(GO_LIVE_WARNING)
        return cleaned


class SpotlightFieldAdmin(admin.ModelAdmin):
    """Manage each partner's Spotlight field set."""

    form = SpotlightFieldAdminForm
    inlines = [SpotlightFieldPropertyInline]
    list_display = ('contributor', 'go_live_date', 'field_count',
                    'pending_count', 'last_partner_edit_at')
    list_filter = (EditedByPartnersFilter,)
    search_fields = ('contributor__name',)
    readonly_fields = ('contributor', 'partner_field', 'go_live_applied',
                       'last_partner_edit_at')
    fields = ('contributor', 'partner_field', 'go_live_date',
              'confirm_date_change', 'go_live_applied',
              'last_partner_edit_at')
    actions = ['approve_all', 'approve_and_activate_all', 'activate_all',
               'deactivate_all']

    def get_ordering(self, request):
        """Most recently edited by a partner first, never-edited last."""
        return [F('last_partner_edit_at').desc(nulls_last=True)]

    def has_add_permission(self, request):
        """Field sets are created automatically when a partner adds a field."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Spotlight fields are never deleted."""
        return False

    def field_count(self, obj):
        """Number of fields the partner has created."""
        return obj.properties.count()

    field_count.short_description = 'Fields'

    def pending_count(self, obj):
        """Number of fields waiting for approval."""
        return obj.properties.filter(approved=False).count()

    pending_count.short_description = 'Awaiting approval'

    def save_model(self, request, obj, form, change):
        """Route a go-live date change through the rule that applies it."""
        new_date = obj.go_live_date
        super().save_model(request, obj, form, change)
        if 'go_live_date' in form.changed_data:
            obj.set_go_live_date(new_date, user=request.user)

    def save_formset(self, request, form, formset, change):
        """Stamp approvals and record who made each change."""
        if formset.model is not SpotlightFieldProperty:
            super().save_formset(request, form, formset, change)
            return
        from django.utils import timezone
        for prop in formset.save(commit=False):
            if prop.approved and prop.approved_at is None:
                prop.approved_at = timezone.now()
                prop.approved_by = request.user
            prop._history_user = request.user
            prop.save(sync=False)
        form.instance.sync_partner_field()

    def _run(self, request, queryset, label, change):
        """Apply `change` to every field and report how many were touched."""
        touched = 0
        for field_set in queryset:
            for prop in field_set.properties.all():
                if change(prop, request.user):
                    touched += 1
        self.message_user(
            request, f'{label}: {touched} field(s) updated.', messages.SUCCESS
        )

    @admin.action(description='Approve all fields (stay inactive)')
    def approve_all(self, request, queryset):
        """Approve every unapproved field in the selected sets."""
        def change(prop, user):
            if prop.approved:
                return False
            prop.approve(user)
            return True
        self._run(request, queryset, 'Approved', change)

    @admin.action(description='Approve and activate all fields')
    def approve_and_activate_all(self, request, queryset):
        """Approve every unapproved field and switch it on straight away."""
        def change(prop, user):
            if prop.approved:
                return False
            prop.approve(user, activate=True)
            return True
        self._run(request, queryset, 'Approved and activated', change)

    @admin.action(description='Activate all approved fields')
    def activate_all(self, request, queryset):
        """Switch on every approved field. Unapproved fields are skipped."""
        def change(prop, user):
            if not prop.approved or prop.active:
                return False
            prop.set_active(True, user, is_admin=True)
            return True
        self._run(request, queryset, 'Activated', change)

    @admin.action(description='Deactivate all fields')
    def deactivate_all(self, request, queryset):
        """Switch off every active field in the selected sets."""
        def change(prop, user):
            if not prop.active:
                return False
            prop.set_active(False, user, is_admin=True)
            return True
        self._run(request, queryset, 'Deactivated', change)


class SpotlightFieldPropertyAdmin(SimpleHistoryAdmin):
    """
    Read-mostly view of single fields whose History button shows who changed
    what and when. Edits happen on the field set page.
    """

    list_display = ('name', 'display_name', 'spotlight_field', 'approved',
                    'active', 'updated_at')
    list_filter = ('approved', 'active')
    search_fields = ('name', 'display_name',
                     'spotlight_field__contributor__name')
    readonly_fields = ('spotlight_field', 'name', 'display_name', 'approved',
                       'approved_at', 'approved_by', 'active',
                       'last_partner_edit_at')

    def has_add_permission(self, request):
        """Partners create fields in their dashboard."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Spotlight fields are never deleted."""
        return False
