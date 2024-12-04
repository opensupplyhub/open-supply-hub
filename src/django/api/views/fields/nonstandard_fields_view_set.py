
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import GenericViewSet

from ...models.nonstandard_field import NonstandardField
from ..contributor.get_contributor import get_contributor


class NonstandardFieldsViewSet(ListModelMixin, GenericViewSet):
    """
    View nonstandard fields submitted by a contributor.
    """
    queryset = NonstandardField.objects.all()
    swagger_schema = None

    def list(self, request):
        if not request.user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)

        contributor = get_contributor(request)

        nonstandard_field_set = set(self.queryset.filter(
            contributor=contributor).values_list('column_name', flat=True))

        field_list = list(
            NonstandardField.EXTENDED_FIELDS.keys() | nonstandard_field_set)

        return Response(field_list)
