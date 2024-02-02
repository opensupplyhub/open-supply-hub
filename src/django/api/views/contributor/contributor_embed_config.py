from rest_framework.decorators import api_view, throttle_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from ...models import Contributor
from ...serializers import EmbedConfigSerializer


@api_view(['GET'])
@throttle_classes([])
def contributor_embed_config(_, pk=None):
    """
    Returns a contributor's embedded map configuration.
    """
    try:
        contributor = Contributor.objects.get(id=pk)
        if contributor.embed_level is None:
            raise PermissionDenied(
                'Embedded map is not configured for provided contributor.'
            )
        embed_config = EmbedConfigSerializer(contributor.embed_config).data
        return Response(embed_config)
    except Contributor.DoesNotExist as exc:
        raise ValidationError('Contributor not found.') from exc


def getContributorTypeCount(value, counts):
    try:
        type = counts.get(contrib_type=value)
        return type['num_type']
    except Contributor.DoesNotExist:
        return 0
