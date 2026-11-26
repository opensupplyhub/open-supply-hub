import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone
from simple_history.models import HistoricalRecords


class OrganizationMembership(models.Model):
    """
    Ties an existing user to an organization with a role.

    The membership attaches to the user; the member's contributor comes
    along through the existing one-to-one Contributor.admin link, which
    is not modified. Removed memberships are kept so the organization
    can still tell who a former member was.
    """
    ADMIN = 'ADMIN'
    MEMBER = 'MEMBER'

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MEMBER, 'Member'),
    )

    ACTIVE = 'ACTIVE'
    REMOVED = 'REMOVED'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (REMOVED, 'Removed'),
    )

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the membership.'
    )
    organization = models.ForeignKey(
        'Organization',
        null=False,
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text='The organization the user belongs to.'
    )
    user = models.ForeignKey(
        'User',
        null=False,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        help_text='The existing OS Hub account that is a member.'
    )
    role = models.CharField(
        max_length=6,
        null=False,
        choices=ROLE_CHOICES,
        default=MEMBER,
        help_text=('Admins manage the organization\'s people; Members '
                   'belong to it.')
    )
    status = models.CharField(
        max_length=7,
        null=False,
        choices=STATUS_CHOICES,
        default=ACTIVE,
        help_text='Removed memberships are kept for the audit trail.'
    )
    invited_by = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=('The user whose invitation created the membership. '
                   'Empty when OS Hub staff added the member.')
    )
    joined_at = models.DateTimeField(
        null=False,
        default=timezone.now,
        help_text='When the user became a member.'
    )
    removed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the membership ended.'
    )
    removed_by = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=('The user who ended the membership; the member '
                   'themselves when they left.')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords(excluded_fields=['uuid'])

    class Meta:
        ordering = ('joined_at',)
        constraints = [
            # A user belongs to one organization at a time.
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(status='ACTIVE'),
                name='unique_active_org_membership_per_user',
                violation_error_message=(
                    'This user already belongs to an organization.'
                ),
            ),
        ]

    def __str__(self):
        return '{} in {} ({}, {})'.format(
            self.user_id, self.organization_id, self.role, self.status
        )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_active(self):
        return self.status == self.ACTIVE
