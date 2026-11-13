from rest_framework.serializers import ModelSerializer

from ..models.embed_supply_chain import EmbedSupplyChain
from ..services.embed_supply_chains import validate_chain


class EmbedSupplyChainSerializer(ModelSerializer):
    """
    A contributor's supply chain. The view passes the contributor in the
    serializer context so the locations can be checked against their own
    facilities.
    """

    class Meta:
        model = EmbedSupplyChain
        fields = ('id', 'name', 'description', 'product_url', 'color',
                  'is_published', 'order', 'nodes', 'links')

    def validate(self, attrs):
        instance = self.instance
        nodes = attrs.get('nodes', instance.nodes if instance else [])
        links = attrs.get('links', instance.links if instance else [])
        if 'nodes' in attrs or 'links' in attrs:
            attrs['nodes'], attrs['links'] = validate_chain(
                self.context['contributor'].id, nodes, links
            )
        return attrs
