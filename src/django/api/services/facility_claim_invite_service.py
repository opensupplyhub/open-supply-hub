from datetime import timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from api.constants import FacilityClaimStatuses
from api.models import FacilityClaim, FacilityClaimInvite

CLAIM_INVITE_SWITCH = 'claim_invite'

# The same address is invited to the same location at most once per
# window, and a location receives a bounded number of invites per
# window, so the profile link can't be used to flood one inbox or one
# facility. Per-sender volume is bounded by ClaimInviteThrottle.
SAME_RECIPIENT_WINDOW = timedelta(days=30)
PER_FACILITY_WINDOW = timedelta(days=7)
PER_FACILITY_MAX_INVITES = 5


def is_claimed_or_pending(facility):
    return FacilityClaim.objects.filter(
        facility=facility,
        status__in=[
            FacilityClaimStatuses.APPROVED,
            FacilityClaimStatuses.PENDING,
        ],
    ).exists()


def validate_can_invite(facility, recipient_email):
    """
    Raise a ValidationError when this location can't be invited to
    claim right now. The messages are shown to the sender as-is.
    """
    if facility.is_closed:
        raise ValidationError(
            'This production location is marked as closed, so it can\'t '
            'be invited to claim its profile.'
        )

    if is_claimed_or_pending(facility):
        raise ValidationError(
            'This production location has already been claimed, or a '
            'claim is being reviewed.'
        )

    now = timezone.now()
    invites = FacilityClaimInvite.objects.filter(facility=facility)

    if invites.filter(
        recipient_email=recipient_email,
        created_at__gte=now - SAME_RECIPIENT_WINDOW,
    ).exists():
        raise ValidationError(
            'This address was recently invited to claim this production '
            'location.'
        )

    if invites.filter(
        created_at__gte=now - PER_FACILITY_WINDOW,
    ).count() >= PER_FACILITY_MAX_INVITES:
        raise ValidationError(
            'This production location has received several invites this '
            'week. Please try again later.'
        )


def find_invite_for_claim(invite_code, facility):
    """
    The invite a claim was submitted from, or None when the code is
    missing, malformed or belongs to another location. Never raises: a
    bad code must not block the claim itself.
    """
    if not invite_code:
        return None
    try:
        return FacilityClaimInvite.objects.get(
            uuid=invite_code,
            facility=facility,
        )
    except (FacilityClaimInvite.DoesNotExist, DjangoValidationError,
            ValueError):
        return None
