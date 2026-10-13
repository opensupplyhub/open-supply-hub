from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings
from rest_framework import exceptions, status
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.permissions import AllowAny
from rest_framework.renderers import (
    JSONRenderer,
    StaticHTMLRenderer,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from waffle import switch_is_active

from api.os_id import validate_os_id
from api.services.identity_record_retrieval import has_live_record
from api.services.os_id_presence import os_id_exists_here

LINKSET_MEDIA_TYPE = 'application/linkset+json'

# Set by scope doc 3.1. The identifier path is the public contract, so it is
# named here rather than spelled out at each call site.
RESOLVER_PATH_PREFIX = 'osid'

PRODUCTION_LOCATION_PAGE_SWITCH = 'enable_production_location_page'

# Scope doc 3.4. Worded to say only what this instance can answer for.
#
# It must not say the identifier is invalid, because it may be perfectly
# valid on another instance, and it must not hint that it exists elsewhere,
# because that would leak the existence of private-instance identifiers one
# probe at a time (NFR-08, AC-09). The same wording is returned whether the
# identifier was never issued anywhere or was issued only on a private
# instance, so the two cases are not distinguishable from outside.
NOT_RESOLVABLE_HERE = (
    'This identifier is not resolvable here.'
)


class LinksetRenderer(JSONRenderer):
    """
    An RFC 9264 link-set is JSON, but it must be served under its own media
    type so a client can ask for it by content negotiation rather than by a
    separate path. Registering it here is what keeps an
    `Accept: application/linkset+json` request from being refused as not
    acceptable before the handler runs.
    """

    media_type = LINKSET_MEDIA_TYPE
    format = 'linkset'


class ResolverContentNegotiation(DefaultContentNegotiation):
    """
    A resolver should answer rather than refuse.

    The default negotiation returns 406 when the Accept header is empty or
    names something we do not render. For an identifier that anyone may hold
    and paste into any client, refusing to resolve on those grounds is worse
    than redirecting to the page. The view decides what to return by reading
    the Accept header itself, so the selected renderer only matters for
    serialising a link-set, and falling back is safe.
    """

    def select_renderer(self, request, renderers, format_suffix=None):
        try:
            return super().select_renderer(
                request, renderers, format_suffix
            )
        except exceptions.NotAcceptable:
            return renderers[0], renderers[0].media_type


def _error(detail, status_code):
    """
    An error body that stays JSON whatever the caller asked for.

    A DRF Response is rendered by whichever renderer negotiation picked, so
    a browser sending `Accept: text/html` would receive the detail dict
    rendered as HTML, which is a Python repr rather than anything a client
    can read. The body here is machine-readable either way, so it is
    returned directly instead. A branded error page for browsers is the
    frontend's concern (OSDEV-3584).
    """
    return JsonResponse({'detail': detail}, status=status_code)


def _site_root(request):
    """
    Absolute origin for this instance, matching the convention in
    api/mail.py so resolver links and emailed links cannot disagree.
    """
    if settings.DEBUG:
        return 'http://localhost:6543'
    host = request.get_host() if request else settings.EXTERNAL_DOMAIN
    return 'https://{}'.format(host)


def _production_location_url(request, os_id):
    """
    The ordinary page for an OS ID.

    Built from the identifier rather than from a Facility instance on
    purpose: FR-14 requires an OS ID with no registered record to resolve to
    the ordinary page, so this must not depend on a lookup succeeding.
    """
    route_prefix = (
        'production-locations'
        if switch_is_active(PRODUCTION_LOCATION_PAGE_SWITCH)
        else 'facilities'
    )
    return '{}/{}/{}'.format(_site_root(request), route_prefix, os_id)


def _identity_record_url(request, os_id):
    """The page showing the registered record (scope doc 2.6)."""
    return '{}/identity-record'.format(
        _production_location_url(request, os_id)
    )


def _destination(request, os_id):
    """
    Where a browser holding this identifier should land.

    Scope doc 3.1: an identifier with a registered record goes to the page
    showing that record, and one without goes to the ordinary location page.
    The second is FR-14 and is a normal answer rather than an error, which
    is why this is a branch and not a guard.
    """
    if has_live_record(os_id):
        return _identity_record_url(request, os_id)
    return _production_location_url(request, os_id)


def _wants_linkset(request):
    """
    True when the caller explicitly asked for a link-set.

    Deliberately an explicit opt-in rather than whatever content negotiation
    happens to select. A bare request, including the `*/*` that command line
    clients send by default, should behave like a browser and redirect.
    """
    accept = request.headers.get('Accept', '')
    return LINKSET_MEDIA_TYPE in accept


class IdentityResolverView(APIView):
    """
    GET /osid/{os_id}

    Two behaviours on one path, chosen by the Accept header (scope doc 3.1,
    FR-19):

      Accept: text/html                 -> 302 to the production location page
      Accept: application/linkset+json  -> 200 with an RFC 9264 link-set

    Public by design. An identifier is only useful if anyone holding it can
    resolve it, so this overrides the project default permission rather than
    inheriting it. Throttling is inherited from DEFAULT_THROTTLE_CLASSES and
    is what keeps that openness from being free to abuse; OSDEV-3587 revisits
    the rate for a public resolver.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    renderer_classes = (JSONRenderer, LinksetRenderer, StaticHTMLRenderer)
    content_negotiation_class = ResolverContentNegotiation

    def get(self, request, os_id):
        # AC#3. Checked before anything touches the database, so a malformed
        # identifier costs a string comparison rather than a query.
        if not validate_os_id(os_id, raise_on_invalid=False):
            return _error(
                'The identifier is not a well-formed OS ID.',
                status.HTTP_400_BAD_REQUEST,
            )

        # Scope doc 3.4. An identifier issued only on a private instance is
        # indistinguishable from a public one without this lookup, so the
        # answer has to be careful about what it implies: not resolvable
        # here, which is true, rather than invalid or nonexistent, which we
        # cannot know and which would be false for the private-instance case
        # (NFR-08, AC-09).
        if not os_id_exists_here(os_id):
            return _error(
                NOT_RESOLVABLE_HERE, status.HTTP_404_NOT_FOUND
            )

        if _wants_linkset(request):
            return Response(
                self._linkset(request, os_id),
                status=status.HTTP_200_OK,
                content_type=LINKSET_MEDIA_TYPE,
            )

        return HttpResponseRedirect(_destination(request, os_id))

    def _linkset(self, request, os_id):
        """
        The link-set envelope.

        Only the Open Supply Hub entry is emitted here. The registered
        external record entry, and the relation type names that carry it, are
        OSDEV-3582: per scope doc 2.1 the link-set is produced by the
        issuer's open-source implementation behind this API, so the relation
        names come from the UNTP registry rather than being coined by us.
        Emitting a placeholder name now would put a guess on a public
        contract.
        """
        anchor = '{}/{}/{}'.format(
            _site_root(request), RESOLVER_PATH_PREFIX, os_id
        )
        return {
            'linkset': [
                {
                    'anchor': anchor,
                    'item': [
                        {
                            'href': _destination(request, os_id),
                            'type': 'text/html',
                            'title': 'Open Supply Hub production location',
                        }
                    ],
                }
            ]
        }


class ResolverDescriptionView(APIView):
    """
    GET /.well-known/resolver

    The resolver description document from scope doc 3.1. Describes what this
    resolver answers for, so a client can discover the identifier path rather
    than having it hard-coded.

    Minimal on purpose. The full ISO 18975 vocabulary is the issuer's to
    settle alongside the relation type names in OSDEV-3582.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    renderer_classes = (JSONRenderer,)
    content_negotiation_class = ResolverContentNegotiation

    def get(self, request):
        root = _site_root(request)
        return Response(
            {
                'name': 'Open Supply Hub identity resolver',
                'resolverRoot': '{}/{}/'.format(
                    root, RESOLVER_PATH_PREFIX
                ),
                'supportedLinkType': [LINKSET_MEDIA_TYPE],
                'identifier': [
                    {
                        'id': 'osid',
                        'title': 'OS ID',
                        'description': (
                            'Open Supply Hub production location '
                            'identifier.'
                        ),
                    }
                ],
            },
            status=status.HTTP_200_OK,
        )
