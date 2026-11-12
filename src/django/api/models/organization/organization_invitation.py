import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone


class OrganizationInvitation(models.Model):
    """
    An invitation, sent by an organization Admin, for an existing OS Hub
    account to join the organization.

    Invitations only ever go to an account that already exists, so
    invited_user is always set; email keeps what the Admin typed.
    """
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    REVOKED = 'REVOKED'
    EXPIRED = 'EXPIRED'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
        (REVOKED, 'Revoked'),
        (EXPIRED, 'Expired'),
    )

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the invitation.'
    )
    organization = models.ForeignKey(
        'Organization',
        null=False,
        on_delete=models.CASCADE,
        related_name='invitations',
        help_text='The organization the user is invited to join.'
    )
    invited_user = models.ForeignKey(
        'User',
        null=False,
        on_delete=models.CASCADE,
        related_name='organization_invitations',
        help_text='The existing OS Hub account that was invited.'
    )
    email = models.EmailField(
        null=False,
        blank=False,
        help_text='The email address the Admin entered.'
    )
    role = models.CharField(
        max_length=6,
        null=False,
        # Kept in sync with OrganizationMembership.ROLE_CHOICES.
        choices=(('ADMIN', 'Admin'), ('MEMBER', 'Member')),
        default='MEMBER',
        help_text='The role the user gets when they accept.'
    )
    invited_by = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='The Admin who sent the invitation.'
    )
    status = models.CharField(
        max_length=8,
        null=False,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text='Where the invitation stands.'
    )
    expires_at = models.DateTimeField(
        null=False,
        help_text='After this moment the invitation can no longer be used.'
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the invitation was accepted, declined or revoked.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'invited_user'],
                condition=Q(status='PENDING'),
                name='unique_pending_org_invitation_per_user',
            ),
        ]

    def __str__(self):
        return '{} invited to {} ({})'.format(
            self.email, self.organization_id, self.status
        )

    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()

    @property
    def is_open(self):
        return self.status == self.PENDING and not self.is_expired
