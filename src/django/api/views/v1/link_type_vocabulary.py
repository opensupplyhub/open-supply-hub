from django.http import Http404
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api.views.v1.resolver_site import resolution_is_open, site_root

# Our own link type vocabulary (OSDEV-3582).
#
# There is no central registry of link relation types to draw these from.
# The UNTP 0.7.0 context defines `linkType` as a plain string and
# enumerates no values, and the reference resolver implementation's
# documentation is explicit that an implementation ships defaults based on
# GS1 and otherwise declares its own vocabulary at a resolvable namespace.
# The issuer in this pilot has done exactly that, publishing terms under a
# `/voc/` path of its own. These are ours, published the same way.
#
# Two obligations come with minting a vocabulary, both from that
# documentation: the namespace must resolve to a machine-readable
# description of the terms, and each term needs a clear definition saying
# what relationship it represents. This view is how we meet both.

LINK_TYPES = [
    {
        'name': 'productionLocation',
        'title': 'Open Supply Hub production location',
        'description': (
            'The Open Supply Hub page for the production location this '
            'identifier names. Always present, whether or not any external '
            'record is registered against the identifier.'
        ),
    },
    {
        'name': 'registeredRecord',
        'title': 'Registered record',
        'description': (
            'A record about this production location, published by another '
            'organization and registered against this identifier by its '
            'issuer. The link is the issuer\'s resolver address rather than '
            'a link to one version of the record, so it continues to '
            'resolve to whichever version is current without being '
            're-registered.'
        ),
    },
]


def vocabulary_namespace(root):
    """
    The namespace every link type is minted under.

    Reversed from the route rather than spelled out, because these URIs
    are the keys of every link-set we serve. A second copy of the path
    would let the route move while the published keys kept pointing at
    where it used to be.
    """
    return '{}{}'.format(
        root.rstrip('/'), reverse('link-type-vocabulary')
    )


def link_type_uri(root, name):
    return '{}{}'.format(vocabulary_namespace(root), name)


class JSONLDRenderer(JSONRenderer):
    """
    The same JSON under the media type a linked-data client asks for.

    These URIs are published for dereferencing, and a client told to
    dereference them sends `Accept: application/ld+json`. Without a
    renderer registered for that type, negotiation refuses the request
    before the view runs.
    """

    media_type = 'application/ld+json'


class LinkTypeVocabularyView(APIView):
    """
    GET /api/v1/voc/ and /api/v1/voc/{term}, the machine-readable
    description of our link relation types, public because a stranger
    holding one of our link-sets has to be able to look up what its keys
    mean. A term that is not ours is a 404 rather than the whole
    vocabulary, so a client can tell the difference.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    renderer_classes = (JSONRenderer, JSONLDRenderer)

    def get(self, request, term=None):
        # Gated with the resolver rather than on its own. The vocabulary
        # only ever explains link-sets this instance serves, so publishing
        # it while the resolver is dark would describe a thing that does
        # not answer.
        if not resolution_is_open():
            raise Http404()

        root = site_root(request)
        namespace = vocabulary_namespace(root)

        if term is not None:
            definition = next(
                (entry for entry in LINK_TYPES if entry['name'] == term),
                None,
            )
            if definition is None:
                raise Http404()
            return Response(
                {
                    'linkType': '{}{}'.format(namespace, definition['name']),
                    'name': definition['name'],
                    'title': definition['title'],
                    'description': definition['description'],
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                'namespace': namespace,
                'title': 'Open Supply Hub link types',
                'description': (
                    'Link relation types used in link-sets served by the '
                    'Open Supply Hub identity resolver.'
                ),
                'linkTypes': [
                    {
                        'linkType': '{}{}'.format(namespace, entry['name']),
                        'name': entry['name'],
                        'title': entry['title'],
                        'description': entry['description'],
                    }
                    for entry in LINK_TYPES
                ],
            },
            status=status.HTTP_200_OK,
        )
