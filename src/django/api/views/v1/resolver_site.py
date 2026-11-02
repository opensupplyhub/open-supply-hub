"""
Pieces the link type vocabulary and the resolver both need.

They sit here rather than in either module because each one would
otherwise import the other.
"""
from waffle import switch_is_active

from api.identity_record_switches import IDENTITY_RESOLVER_SWITCH
from api.mail import make_oshub_url


def site_root(request):
    """
    Absolute origin for this instance.

    Delegates to the helper the emails use rather than repeating its rules,
    so a resolver link and an emailed link cannot disagree about the host.
    """
    return make_oshub_url(request)


def resolution_is_open():
    """
    Whether the public read side of the pilot is turned on, off by
    default. Opening it makes the resolver answer for every OS ID on this
    instance rather than only the ones carrying a registered record.
    """
    return switch_is_active(IDENTITY_RESOLVER_SWITCH)
