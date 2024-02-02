from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)
from rest_framework.viewsets import GenericViewSet
from django.db import transaction

from ..models.embed_config import EmbedConfig
from ..models.embed_field import EmbedField
from ..serializers.embed_config import EmbedConfigSerializer

from .contributor.get_contributor import get_contributor
from .fields.create_embed_fields import create_embed_fields


class EmbedConfigViewSet(ListModelMixin,
                         RetrieveModelMixin,
                         UpdateModelMixin,
                         CreateModelMixin,
                         GenericViewSet):
    """
    View EmbedConfig.
    """
    queryset = EmbedConfig.objects.all()
    serializer_class = EmbedConfigSerializer
    swagger_schema = None

    @transaction.atomic
    def create(self, request):
        if not request.user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)

        contributor = get_contributor(request)
        if contributor.embed_config is not None:
            raise ValidationError(
                'Contributor has an existing embed configuration.')

        fields_data = request.data.pop('embed_fields', [])

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            embed_config = EmbedConfig.objects.get(id=serializer.data['id'])

            # Assign embed config to contributor
            contributor.embed_config = embed_config
            contributor.save()

            create_embed_fields(fields_data, embed_config)

            response_data = self.get_serializer(embed_config).data

            return Response(response_data)

    @transaction.atomic
    def update(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)

        contributor = get_contributor(request)

        embed_config = EmbedConfig.objects.get(id=pk)

        if embed_config.contributor.id != contributor.id:
            error_data = {'error': (
                f'Update failed because embed contributor ID '
                f'{embed_config.contributor.id} does not match the '
                f'contributor ID {contributor.id}')}
            return Response(error_data,
                            content_type='application/json',
                            status=HTTP_403_FORBIDDEN)

        fields_data = request.data.pop('embed_fields', [])

        # Update field data by deleting and recreating
        existing_fields = EmbedField.objects.filter(embed_config=embed_config)
        previously_searchable = [
            f.get('column_name')
            for f
            in existing_fields.values('column_name', 'searchable')
            if f.get('searchable', None)
        ]
        existing_fields.delete()
        create_embed_fields(fields_data, embed_config, previously_searchable)

        return super(EmbedConfigViewSet, self).update(request, pk=pk)
