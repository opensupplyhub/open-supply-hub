from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

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
VOCABULARY_PATH = 'api/v1/voc/'

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


def vocabulary_namespace(site_root):
    return '{}/{}'.format(site_root.rstrip('/'), VOCABULARY_PATH)


def link_type_uri(site_root, name):
    return '{}{}'.format(vocabulary_namespace(site_root), name)


class LinkTypeVocabularyView(APIView):
    """
    GET /api/v1/voc/
    GET /api/v1/voc/?show=linktypes

    The machine-readable description of our link relation types.

    Public and unauthenticated, because the whole point of publishing a
    vocabulary is that a stranger holding one of our link-sets can look up
    what its keys mean. A vocabulary nobody can read is not a vocabulary.

    The `show=linktypes` form exists because that is the shape the
    reference resolver implementation gives for a profile URL, and
    matching it means a client written against that convention can
    read ours.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        from api.views.v1.identity_resolver import site_root

        root = site_root(request)
        namespace = vocabulary_namespace(root)

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
