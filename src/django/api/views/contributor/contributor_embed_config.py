from rest_framework.decorators import api_view, throttle_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from ...models import Contributor
from ...serializers import EmbedConfigSerializer
from ...services.embed_supply_chains import published_supply_chains
from ...services.embed_field_filters import (
    embed_filter_options,
    field_value_options,
)


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
        # The values a visitor can pick for each field the contributor has
        # made filterable.
        embed_config['filter_options'] = embed_filter_options(contributor)
        # The values of the field that colors the map's markers, if any.
        color_by_field = contributor.embed_config.color_by_field
        embed_config['color_by_options'] = (
            field_value_options(contributor.id, color_by_field)
            if color_by_field
            else []
        )
        # The supply chains the contributor has published for visitors.
        embed_config['supply_chains'] = published_supply_chains(contributor)
        return Response(embed_config)
    except Contributor.DoesNotExist as exc:
        raise ValidationError('Contributor not found.') from exc


def getContributorTypeCount(value, counts):
    try:
        type = counts.get(contrib_type=value)
        return type['num_type']
    except Contributor.DoesNotExist:
        return 0
