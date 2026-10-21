from django.http import Http404, HttpResponseRedirect, JsonResponse
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
from api.services.identity_record_retrieval import (
    get_live_association,
    has_live_record,
)
from api.services.os_id_presence import os_id_exists_here
from api.views.v1.resolver_site import resolution_is_open, site_root
from api.views.v1.link_type_vocabulary import (
    LINK_TYPES,
    link_type_uri,
    vocabulary_namespace,
)

LINKSET_MEDIA_TYPE = 'application/linkset+json'

# The identifier scheme this resolver answers for, and the first segment
# of its path. Ours rather than inherited: it is published as the
# identifier id in the resolver description, so the constant, the route
# and that document have to agree or a client that discovered the path
# builds URLs we do not serve.
RESOLVER_PATH_PREFIX = 'osid'

PRODUCTION_LOCATION_PAGE_SWITCH = 'enable_production_location_page'

# Worded to say only what this instance can answer for.
#
# It must not say the identifier is invalid, because it may be perfectly
# valid on another instance, and it must not hint that it exists elsewhere,
# because that would leak the existence of private-instance identifiers one
# probe at a time. The same wording is returned whether the
# identifier was never issued anywhere or was issued only on a private
# instance, so the two cases are not distinguishable from outside.
NOT_RESOLVABLE_HERE = (
    'This identifier is not resolvable here.'
)


class LinksetRenderer(JSONRenderer):
    """
    A link-set is JSON served under its own media type, so content
    negotiation can select it without a separate path. Without a renderer
    registered for that type, `Accept: application/linkset+json` is
    refused as not acceptable before the handler runs.
    """

    media_type = LINKSET_MEDIA_TYPE
    format = 'linkset'


class ResolverContentNegotiation(DefaultContentNegotiation):
    """
    An Accept header that is empty or names something we do not render
    falls back instead of returning 406. The view reads the header
    itself, so the selected renderer only matters for serializing a
    link-set.
    """

    def select_renderer(self, request, renderers, format_suffix=None):
        try:
            return super().select_renderer(
                request, renderers, format_suffix
            )
        except (exceptions.NotAcceptable, Http404):
            return renderers[0], renderers[0].media_type


def _error(detail, status_code):
    """
    An error body that stays JSON whatever the caller asked for.
    Rendering a detail dict through the HTML renderer would emit a Python
    repr rather than anything a client can read.
    """
    return JsonResponse({'detail': detail}, status=status_code)


def _header_safe(value):
    """
    Strip the characters that separate fields in a `Link` header.

    A resolver URI is supplied by a registrant and `URLValidator` accepts
    `<`, `>`, `"`, `;` and `,` in a path, so interpolating one unescaped
    would let a registrant add relations of their own to a public header.
    """
    return ''.join(
        character for character in str(value)
        if character not in '<>";,\r\n'
    )


def _production_location_url(request, os_id):
    """
    The ordinary page for an OS ID.

    Built from the identifier rather than from a Facility instance on
    purpose: an OS ID with no registered record must resolve to
    the ordinary page, so this must not depend on a lookup succeeding.
    """
    route_prefix = (
        'production-locations'
        if switch_is_active(PRODUCTION_LOCATION_PAGE_SWITCH)
        else 'facilities'
    )
    return '{}/{}/{}'.format(site_root(request), route_prefix, os_id)


# The record page is mounted at one route only, under `facilities`, and
# does not move with the production location page switch. Composing this
# from _production_location_url would follow that switch to a path the
# web app does not serve, and the visitor would silently land on the
# ordinary profile instead of the record they followed the identifier for.
IDENTITY_RECORD_ROUTE_PREFIX = 'facilities'


def _identity_record_url(request, os_id):
    """The page showing the registered record."""
    return '{}/{}/{}/identity-record'.format(
        site_root(request), IDENTITY_RECORD_ROUTE_PREFIX, os_id
    )


def _destination(request, os_id):
    """
    Where a browser holding this identifier should land: the record page
    when one is registered, the ordinary location page otherwise. The
    second is a normal answer rather than an error, which is why this is
    a branch and not a guard.
    """
    if has_live_record(os_id):
        return _identity_record_url(request, os_id)
    return _production_location_url(request, os_id)


def _wants_linkset(request):
    """
    True when the caller explicitly asked for a link-set, rather than
    whatever negotiation would select. A bare request, including the
    `*/*` command line clients send by default, redirects like a
    browser.
    """
    accept = request.headers.get('Accept', '')
    return LINKSET_MEDIA_TYPE in accept


class IdentityResolverView(APIView):
    """
    GET /osid/{os_id}, serving two behaviors on one path chosen by the
    Accept header: `text/html` redirects to the production location
    page, `application/linkset+json` returns an RFC 9264 link-set.
    Public by design, since an identifier is only useful if anyone
    holding it can resolve it, with throttling inherited from
    DEFAULT_THROTTLE_CLASSES.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    renderer_classes = (JSONRenderer, LinksetRenderer, StaticHTMLRenderer)
    content_negotiation_class = ResolverContentNegotiation

    def get(self, request, os_id):
        # Pilot gate. For a well-formed identifier this is byte for byte
        # the answer a running resolver gives for one it cannot resolve,
        # which is true while the switch is off and says nothing about
        # the feature existing.
        #
        # It is not a general secret. A malformed identifier is a 400
        # once the resolver is live and a 404 while it is dark, so one
        # probe shows the switch state. The 400 is the routing contract
        # and is not worth trading away: the switch keeps the pilot out
        # of casual discovery rather than acting as an access control.
        if not resolution_is_open():
            return _error(
                NOT_RESOLVABLE_HERE, status.HTTP_404_NOT_FOUND
            )

        # validate_os_id accepts the hyphenated spelling, and Crockford
        # base 32 is case-insensitive on decode, so normalize to the
        # stored form before validating or looking anything up. Without
        # the case fold a lower-case country code passes validation (the
        # checksum is unchanged by it) and then misses every lookup,
        # answering not-resolvable-here for a location we hold.
        os_id = os_id.replace('-', '').replace(' ', '').upper()

        # Checked before anything touches the database, so a malformed
        # identifier costs a string comparison rather than a query.
        if not validate_os_id(os_id, raise_on_invalid=False):
            return _error(
                'The identifier is not a well-formed OS ID.',
                status.HTTP_400_BAD_REQUEST,
            )

        # An identifier issued only on a private instance is
        # indistinguishable from a public one without this lookup, so the
        # answer has to be careful about what it implies: not resolvable
        # here, which is true, rather than invalid or nonexistent, which we
        # cannot know and which would be false for the private-instance case
        if not os_id_exists_here(os_id):
            return _error(
                NOT_RESOLVABLE_HERE, status.HTTP_404_NOT_FOUND
            )

        if _wants_linkset(request):
            linkset = self._linkset(request, os_id)
            response = Response(
                linkset,
                status=status.HTTP_200_OK,
                content_type=LINKSET_MEDIA_TYPE,
            )
            # The branch above is chosen from the raw Accept header while
            # DRF picks a renderer independently, and the two can
            # disagree: an Accept naming a parameterized HTML type
            # outranks the bare link-set type and selects
            # StaticHTMLRenderer, which hands the dict to Django to
            # iterate, emitting the bare key under a JSON media type.
            # Set on the request rather than the response, because
            # finalize_response copies these across unconditionally.
            request.accepted_renderer = LinksetRenderer()
            request.accepted_media_type = LINKSET_MEDIA_TYPE
            response['Link'] = self._link_header(linkset)
            return response

        return HttpResponseRedirect(_destination(request, os_id))

    def _linkset(self, request, os_id):
        """
        The RFC 9264 link-set for an identifier, keyed by link relation
        types from our own published vocabulary. UNTP defines `linkType`
        as a plain string and enumerates no values, so each resolver
        publishes its own terms at a resolvable namespace and every key
        here dereferences to a definition.
        """
        root = site_root(request)
        anchor = '{}/{}/{}'.format(root, RESOLVER_PATH_PREFIX, os_id)

        # Always the ordinary location page, which is what the published
        # vocabulary says this relation points at. Using the redirect
        # destination here would silently retarget it at the record page
        # once a record was registered, leaving the link-set with no link
        # to the location itself.
        entries = {
            link_type_uri(root, 'productionLocation'): [
                {
                    'href': _production_location_url(request, os_id),
                    'type': 'text/html',
                    'title': 'Open Supply Hub production location',
                }
            ]
        }

        association = get_live_association(os_id)
        if association is not None:
            entries[link_type_uri(root, 'registeredRecord')] = [
                {
                    'href': association.resolver_uri,
                    'type': 'application/json',
                    'title': 'Registered record (current version)',
                }
            ]

        return {'linkset': [dict(anchor=anchor, **entries)]}

    @staticmethod
    def _link_header(linkset):
        """
        The same links as an HTTP `Link` header (RFC 8288).

        The issuer's resolver serves the link-set
        both ways and commits us to matching, so a client that reads headers
        rather than bodies sees the same thing.
        """
        entry = linkset['linkset'][0]
        parts = []
        for relation, links in entry.items():
            if relation == 'anchor':
                continue
            for link in links:
                parts.append(
                    '<{}>; rel="{}"; type="{}"; anchor="{}"'.format(
                        _header_safe(link['href']),
                        _header_safe(relation),
                        _header_safe(link['type']),
                        _header_safe(entry['anchor']),
                    )
                )
        return ', '.join(parts)


class ResolverDescriptionView(APIView):
    """
    GET /.well-known/resolver, describing what this resolver answers for
    so a client can discover the identifier path rather than hard-coding
    it. Minimal on purpose: the full ISO 18975 vocabulary is the
    issuer's to settle.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    renderer_classes = (JSONRenderer,)
    content_negotiation_class = ResolverContentNegotiation

    def get(self, request):
        # Nothing to describe while the resolver does not answer.
        if not resolution_is_open():
            return _error(
                'No resolver is published here.',
                status.HTTP_404_NOT_FOUND,
            )

        root = site_root(request)
        return Response(
            {
                'name': 'Open Supply Hub identity resolver',
                'resolverRoot': '{}/{}/'.format(
                    root, RESOLVER_PATH_PREFIX
                ),
                # The namespace a client dereferences to find out what
                # our link relation types mean, and the profile URL giving
                # the same thing in the shape the reference resolver
                # implementation documents.
                # Publishing these is the obligation that comes with
                # minting our own vocabulary rather than using a registry.
                'namespaceURI': vocabulary_namespace(root),
                'profileUrl': '{}?show=linktypes'.format(
                    vocabulary_namespace(root)
                ),
                # The relation types this resolver emits, which is what
                # the field is for. The link-set media type is advertised
                # through content negotiation, not here.
                'supportedLinkType': [
                    link_type_uri(root, entry['name'])
                    for entry in LINK_TYPES
                ],
                'identifier': [
                    {
                        'id': RESOLVER_PATH_PREFIX,
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
