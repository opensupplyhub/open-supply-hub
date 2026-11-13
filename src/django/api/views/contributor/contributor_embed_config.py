from rest_framework.decorators import api_view, throttle_classes
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response

from ...models import Contributor
from ...serializers import EmbedConfigSerializer
from ...services.embed_spotlight import (
    DELUXE_EMBED_LEVEL,
    spotlight_for_settings,
    spotlight_for_visitors,
)
from .get_contributor import get_contributor
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
        # The Spotlight data the contributor has chosen to show, if any.
        embed_config['spotlight'] = spotlight_for_visitors(contributor)
        return Response(embed_config)
    except Contributor.DoesNotExist as exc:
        raise ValidationError('Contributor not found.') from exc


@api_view(['GET'])
def embed_spotlight_options(request):
    """
    Returns the Spotlight data a contributor could show on their embedded
    map: each partner field group and how many of their facilities have
    data in it. For the contributor's own Embed settings screen.
    """
    if not request.user.is_authenticated:
        raise NotAuthenticated()
    contributor = get_contributor(request)
    if contributor.embed_level != DELUXE_EMBED_LEVEL:
        raise PermissionDenied(
            'Spotlight on the embedded map is part of the Embed Deluxe '
            'package.'
        )
    return Response(spotlight_for_settings(contributor))


@api_view(['GET'])
def embed_field_values(request):
    """
    Returns the values the contributor's facilities have in one of their
    columns (`?column=<name>`), with how many facilities have each. For
    the contributor's own Embed settings screen, where they can explain
    what each value means.
    """
    if not request.user.is_authenticated:
        raise NotAuthenticated()
    contributor = get_contributor(request)
    column = request.query_params.get('column')
    if not column:
        raise ValidationError('A column is required.')
    return Response(field_value_options(contributor.id, column))


def getContributorTypeCount(value, counts):
    try:
        type = counts.get(contrib_type=value)
        return type['num_type']
    except Contributor.DoesNotExist:
        return 0
