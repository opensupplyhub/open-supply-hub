import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from waffle import switch_is_active

from api.constants import FacilityClaimStatuses, OrganizationSettings
from api.models.facility.facility_claim import FacilityClaim
from api.models.moderation_event import ModerationEvent
from api.models.organization.organization_invitation import (
    OrganizationInvitation,
)
from api.models.organization.organization_membership import (
    OrganizationMembership,
)
from api.models.source import Source
from api.models.user import User

log = logging.getLogger(__name__)

ORGANIZATION_LEVEL_SWITCH = 'organization_level'

# The tables that record which organization a contribution was made for.
STAMPED_MODELS = (Source, ModerationEvent, FacilityClaim)


def is_organization_level_active():
    return switch_is_active(ORGANIZATION_LEVEL_SWITCH)


def get_active_membership(user):
    """
    The user's membership of an active organization, or None. A user
    holds at most one ACTIVE membership.
    """
    if user is None or not user.is_authenticated:
        return None

    return (
        OrganizationMembership.objects
        .select_related('organization')
        .filter(
            user=user,
            status=OrganizationMembership.ACTIVE,
            organization__is_active=True,
        )
        .first()
    )


def get_organization_id_for_contributor(contributor_id):
    """
    The organization a contribution by this contributor is recorded
    against right now, or None. Each contributor has exactly one user,
    so the contributor's organization is that user's active membership.
    """
    if contributor_id is None or not is_organization_level_active():
        return None

    return (
        OrganizationMembership.objects
        .filter(
            user__contributor__id=contributor_id,
            status=OrganizationMembership.ACTIVE,
            organization__is_active=True,
        )
        .values_list('organization_id', flat=True)
        .first()
    )


def stamp_member_contributions(membership):
    """
    Attribute the member's earlier contributions to their organization.

    Only rows that no organization holds yet are touched, so
    contributions already recorded against an organization the person
    belonged to before stay there. Safe to run again: a second run
    finds nothing left to update.

    The facility index names the organization a contribution is recorded
    against, so every source and claim updated here re-indexes its
    production locations through the database triggers. For a member
    with many contributions this is the slow part of joining.

    Returns the number of rows updated per model name.
    """
    contributor_id = (
        User.objects
        .filter(pk=membership.user_id)
        .values_list('contributor__id', flat=True)
        .first()
    )
    if contributor_id is None:
        return {}

    counts = {}
    for model in STAMPED_MODELS:
        counts[model.__name__] = (
            model.objects
            .filter(
                contributor_id=contributor_id,
                organization__isnull=True,
            )
            .update(organization_id=membership.organization_id)
        )

    log.info(
        '[Organization] Attributed earlier contributions of user %s to '
        'organization %s: %s',
        membership.user_id, membership.organization_id, counts,
    )
    return counts


def expire_stale_invitations(organization):
    """Close invitations whose time ran out so they free their seat."""
    return (
        OrganizationInvitation.objects
        .filter(
            organization=organization,
            status=OrganizationInvitation.PENDING,
            expires_at__lte=timezone.now(),
        )
        .update(status=OrganizationInvitation.EXPIRED)
    )


def find_invitable_user(organization, email):
    """
    The existing account an invitation to this email would go to.
    Raises a ValidationError the Admin can act on when the email cannot
    be invited: no confirmed account, already in an organization,
    already invited, or no seat left.
    """
    email = (email or '').strip().lower()
    user = User.objects.filter(email__iexact=email, is_active=True).first()

    if user is None or not user.did_register_and_confirm_email:
        raise ValidationError({
            'email': [
                'No confirmed OS Hub account uses this email address. Ask '
                'the person to register and confirm their email first, '
                'then invite them again.'
            ]
        })

    existing = (
        OrganizationMembership.objects
        .filter(user=user, status=OrganizationMembership.ACTIVE)
        .first()
    )
    if existing is not None:
        if existing.organization_id == organization.id:
            message = 'This person is already a member of the organization.'
        else:
            message = (
                'This person already belongs to another organization. They '
                'need to leave it before they can join this one.'
            )
        raise ValidationError({'email': [message]})

    expire_stale_invitations(organization)

    already_invited = OrganizationInvitation.objects.filter(
        organization=organization,
        invited_user=user,
        status=OrganizationInvitation.PENDING,
    ).exists()
    if already_invited:
        raise ValidationError({
            'email': [
                'This person already has an invitation waiting for an '
                'answer.'
            ]
        })

    if not organization.has_free_seat:
        raise ValidationError({
            'email': [
                'The organization has no free seat. Remove a member or '
                'revoke an invitation, or ask OS Hub to raise the limit.'
            ]
        })

    return user


def email_domain(email):
    """The part of an email address after the @, lower-cased."""
    _, separator, domain = (email or '').strip().lower().rpartition('@')
    return domain if separator else ''


def find_domain_accounts(organization, admin_user):
    """
    Existing OS Hub accounts on the same email domain as the Admin that
    could be invited: confirmed, not in any organization, and without an
    invitation from this organization waiting for an answer.

    Returns (domain, accounts). The domain is None, and nothing is
    suggested, when the Admin's address is on a public mail provider:
    sharing gmail.com does not make two people colleagues.
    """
    domain = email_domain(admin_user.email)
    if not domain or domain in OrganizationSettings.PUBLIC_EMAIL_DOMAINS:
        return None, []

    expire_stale_invitations(organization)

    accounts = (
        User.objects
        .filter(email__iendswith='@' + domain, is_active=True)
        .exclude(pk=admin_user.pk)
        # An account whose primary address was never confirmed cannot be
        # invited, see find_invitable_user.
        .exclude(emailaddress__primary=True, emailaddress__verified=False)
        .exclude(
            organization_memberships__status=OrganizationMembership.ACTIVE
        )
        .exclude(
            pk__in=OrganizationInvitation.objects.filter(
                organization=organization,
                status=OrganizationInvitation.PENDING,
            ).values('invited_user_id')
        )
        .select_related('contributor')
        .order_by('email')
        [:OrganizationSettings.DOMAIN_ACCOUNTS_LIMIT]
    )
    return domain, list(accounts)


def get_onboarding_progress(organization):
    """
    Which first steps the organization has taken, for the checklist on
    the My Organization page.
    """
    has_contributions = (
        Source.objects.filter(organization=organization).exists()
        or ModerationEvent.objects.filter(organization=organization).exists()
    )
    has_claims = (
        FacilityClaim.objects
        .filter(organization=organization)
        .exclude(status__in=(
            FacilityClaimStatuses.DENIED,
            FacilityClaimStatuses.REVOKED,
        ))
        .exists()
    )
    return {
        'has_contributions': has_contributions,
        'has_colleagues': organization.active_memberships().count() > 1,
        'has_claims': has_claims,
    }


@transaction.atomic
def create_invitation(organization, invited_by, email, role):
    # Lock the organization so concurrent invitations are checked
    # against the seat limit one at a time.
    organization = (
        type(organization).objects
        .select_for_update()
        .get(pk=organization.pk)
    )
    invited_user = find_invitable_user(organization, email)

    return OrganizationInvitation.objects.create(
        organization=organization,
        invited_user=invited_user,
        email=invited_user.email,
        role=role,
        invited_by=invited_by,
        expires_at=timezone.now() + timedelta(
            days=OrganizationSettings.INVITATION_LIFETIME_DAYS
        ),
    )


def _close_invitation(invitation, status):
    invitation.status = status
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=['status', 'responded_at'])
    return invitation


def _get_open_invitation_for_update(invitation):
    invitation = (
        OrganizationInvitation.objects
        .select_for_update()
        .select_related('organization')
        .get(pk=invitation.pk)
    )
    if invitation.status != OrganizationInvitation.PENDING:
        raise ValidationError(
            'This invitation is no longer waiting for an answer.'
        )
    if invitation.is_expired:
        # Left as it is: this request is about to roll back, and
        # expire_stale_invitations closes the row the next time the
        # organization's invitations are listed or added to.
        raise ValidationError('This invitation has expired.')
    return invitation


@transaction.atomic
def accept_invitation(invitation, user):
    """
    Turn an open invitation into an ACTIVE membership and attribute the
    new member's earlier contributions to the organization.
    """
    invitation = _get_open_invitation_for_update(invitation)

    if invitation.invited_user_id != user.id:
        raise ValidationError('This invitation was sent to someone else.')
    if not invitation.organization.is_active:
        raise ValidationError('This organization is no longer active.')
    if OrganizationMembership.objects.filter(
        user=user, status=OrganizationMembership.ACTIVE
    ).exists():
        raise ValidationError(
            'You already belong to an organization. Leave it before '
            'joining another one.'
        )

    membership = OrganizationMembership.objects.create(
        organization=invitation.organization,
        user=user,
        role=invitation.role,
        invited_by=invitation.invited_by,
    )
    _close_invitation(invitation, OrganizationInvitation.ACCEPTED)
    stamp_member_contributions(membership)

    return membership


@transaction.atomic
def decline_invitation(invitation, user):
    invitation = _get_open_invitation_for_update(invitation)
    if invitation.invited_user_id != user.id:
        raise ValidationError('This invitation was sent to someone else.')
    return _close_invitation(invitation, OrganizationInvitation.DECLINED)


@transaction.atomic
def revoke_invitation(invitation):
    invitation = (
        OrganizationInvitation.objects
        .select_for_update()
        .get(pk=invitation.pk)
    )
    if invitation.status != OrganizationInvitation.PENDING:
        raise ValidationError(
            'Only an invitation that is still waiting can be revoked.'
        )
    return _close_invitation(invitation, OrganizationInvitation.REVOKED)


def _other_active_admins(membership):
    return (
        OrganizationMembership.objects
        .filter(
            organization_id=membership.organization_id,
            status=OrganizationMembership.ACTIVE,
            role=OrganizationMembership.ADMIN,
        )
        .exclude(pk=membership.pk)
    )


def _require_another_admin(membership, action):
    """An organization always keeps at least one Admin."""
    if membership.is_admin and not _other_active_admins(membership).exists():
        raise ValidationError(
            'This is the organization\'s only Admin. Make another member '
            'an Admin before {}.'.format(action)
        )


@transaction.atomic
def change_member_role(membership, role):
    membership = (
        OrganizationMembership.objects
        .select_for_update()
        .get(pk=membership.pk)
    )
    if not membership.is_active:
        raise ValidationError('This person is no longer a member.')
    if role == membership.role:
        return membership
    if role != OrganizationMembership.ADMIN:
        _require_another_admin(membership, 'changing this role')

    membership.role = role
    membership.save(update_fields=['role', 'updated_at'])
    return membership


@transaction.atomic
def remove_member(membership, removed_by):
    """
    End a membership. The person's account, contributor and data are
    untouched, and contributions already recorded against the
    organization stay with it.
    """
    membership = (
        OrganizationMembership.objects
        .select_for_update()
        .get(pk=membership.pk)
    )
    if not membership.is_active:
        raise ValidationError('This person is no longer a member.')

    leaving = removed_by is not None and removed_by.id == membership.user_id
    _require_another_admin(
        membership, 'leaving' if leaving else 'removing this member'
    )

    membership.status = OrganizationMembership.REMOVED
    membership.removed_at = timezone.now()
    membership.removed_by = removed_by
    membership.save(
        update_fields=['status', 'removed_at', 'removed_by', 'updated_at']
    )
    return membership
