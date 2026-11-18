from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils import timezone
from simple_history.admin import SimpleHistoryAdmin

from api.mail import send_organization_member_added_email
from api.models.organization.organization_invitation import (
    OrganizationInvitation,
)
from api.models.organization.organization_membership import (
    OrganizationMembership,
)
from api.services.organization_service import stamp_member_contributions


class OrganizationMembershipInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        """An organization always has at least one active Admin."""
        super().clean()
        if any(self.errors):
            return

        has_active_admin = any(
            form.cleaned_data
            and not form.cleaned_data.get('DELETE', False)
            and form.cleaned_data.get('role') == OrganizationMembership.ADMIN
            and form.cleaned_data.get('status')
            == OrganizationMembership.ACTIVE
            for form in self.forms
        )
        if not has_active_admin:
            raise ValidationError(
                'Name at least one active Admin: add a member below with '
                'the Admin role and the Active status.'
            )


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    formset = OrganizationMembershipInlineFormSet
    fk_name = 'organization'
    fields = ('user', 'role', 'status', 'joined_at', 'removed_at')
    readonly_fields = ('removed_at',)
    raw_id_fields = ('user',)
    extra = 0
    verbose_name = 'member'
    verbose_name_plural = (
        'members (pick existing OS Hub accounts; the first one needs the '
        'Admin role)'
    )


class OrganizationInvitationInline(admin.TabularInline):
    model = OrganizationInvitation
    fk_name = 'organization'
    fields = ('email', 'role', 'status', 'invited_by', 'expires_at',
              'responded_at', 'created_at')
    readonly_fields = fields
    extra = 0
    can_delete = False
    verbose_name = 'invitation'
    verbose_name_plural = 'invitations (sent by the organization\'s Admins)'

    def has_add_permission(self, request, obj=None):
        return False


class OrganizationAdmin(SimpleHistoryAdmin):
    """
    Where OS Hub staff create an organization, name its first Admin,
    set its seat limit and switch its paid dashboard on or off. There
    is no self-service creation and no email-domain check.
    """
    list_display = ('name', 'active_member_count', 'seat_limit',
                    'dashboard_enabled', 'is_active', 'created_at')
    list_filter = ('is_active', 'dashboard_enabled')
    search_fields = ('name', 'legal_name', 'memberships__user__email')
    readonly_fields = ('uuid', 'created_by', 'created_at', 'updated_at')
    history_list_display = ('seat_limit', 'dashboard_enabled', 'is_active')
    inlines = (OrganizationMembershipInline, OrganizationInvitationInline)
    fields = ('name', 'legal_name', 'parent_entity_name', 'seat_limit',
              'dashboard_enabled', 'is_active', 'notes', 'uuid',
              'created_by', 'created_at', 'updated_at')

    @admin.display(description='active members')
    def active_member_count(self, organization):
        return organization.active_memberships().count()

    def save_model(self, request, obj, form, change):
        if not change and obj.created_by_id is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if formset.model is not OrganizationMembership:
            return super().save_formset(request, form, formset, change)

        memberships = formset.save(commit=False)
        for deleted in formset.deleted_objects:
            deleted.delete()

        for membership in memberships:
            is_new = membership.pk is None
            if membership.status == OrganizationMembership.REMOVED:
                if membership.removed_at is None:
                    membership.removed_at = timezone.now()
                    membership.removed_by = request.user
            else:
                membership.removed_at = None
                membership.removed_by = None
            membership.save()

            if is_new and membership.is_active:
                # A member added by staff joins the same way an invited
                # one does: their earlier contributions are attributed
                # to the organization and they are told.
                stamp_member_contributions(membership)
                send_organization_member_added_email(request, membership)

        formset.save_m2m()
