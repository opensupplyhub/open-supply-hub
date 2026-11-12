import uuid

from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from api.constants import OrganizationSettings


class Organization(models.Model):
    """
    A group of existing OS Hub accounts that work as one team.

    An organization sits on top of the account model and changes none of
    it: every member keeps their own user, contributor and public
    attribution. OS Hub staff create organizations in the Django admin
    and name the first Admin, who then invites other existing accounts.
    """
    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the organization.'
    )
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        unique=True,
        help_text=(
            'The name the organization is shown under: to its members, and '
            'publicly as the contributor of the production location data '
            'its members contribute.'
        )
    )
    legal_name = models.CharField(
        max_length=200,
        null=False,
        blank=True,
        help_text='The legal or billing name of the organization.'
    )
    parent_entity_name = models.CharField(
        max_length=200,
        null=False,
        blank=True,
        help_text=('The name of the larger entity that owns the '
                   'organization, if any.')
    )
    seat_limit = models.PositiveIntegerField(
        null=False,
        default=OrganizationSettings.DEFAULT_SEAT_LIMIT,
        help_text=('The most people the organization can hold: active '
                   'members plus invitations still waiting for an answer.')
    )
    is_active = models.BooleanField(
        null=False,
        default=True,
        help_text=('Unselect to deactivate the organization instead of '
                   'deleting it. Its members lose the organization views '
                   'and new contributions stop being recorded against it; '
                   'no data is deleted.')
    )
    dashboard_enabled = models.BooleanField(
        'dashboard enabled',
        null=False,
        default=False,
        help_text=('The paid organization dashboard. Select when the '
                   'organization buys it and unselect when that '
                   'subscription ends; no data is deleted.')
    )
    notes = models.TextField(
        null=False,
        blank=True,
        help_text='Internal notes for OS Hub staff.'
    )
    created_by = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='The staff user who created the organization.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords(excluded_fields=['uuid'])

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return '{} ({})'.format(self.name, self.id)

    def active_memberships(self):
        from .organization_membership import OrganizationMembership
        return self.memberships.filter(
            status=OrganizationMembership.ACTIVE
        )

    def open_invitations(self):
        from .organization_invitation import OrganizationInvitation
        return self.invitations.filter(
            status=OrganizationInvitation.PENDING,
            expires_at__gt=timezone.now(),
        )

    @property
    def seats_used(self):
        """Active members plus invitations still waiting for an answer."""
        return (
            self.active_memberships().count()
            + self.open_invitations().count()
        )

    @property
    def has_free_seat(self):
        return self.seats_used < self.seat_limit
