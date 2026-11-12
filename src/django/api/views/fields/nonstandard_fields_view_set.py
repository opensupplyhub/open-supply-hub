
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import GenericViewSet

from ...models.extended_field import ExtendedField
from ...models.nonstandard_field import NonstandardField
from ..contributor.get_contributor import get_contributor


class NonstandardFieldsViewSet(ListModelMixin, GenericViewSet):
    """
    View the fields a contributor has data for and can therefore show on
    their embedded map: the nonstandard columns they have submitted, plus
    whichever of the standard extended fields they have contributed.
    """
    queryset = NonstandardField.objects.all()
    swagger_schema = None

    def list(self, request):
        if not request.user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)

        contributor = get_contributor(request)

        nonstandard_field_set = set(self.queryset.filter(
            contributor=contributor).values_list('column_name', flat=True))

        # A standard field is only offered when the contributor has data for
        # it; a field with nothing behind it would show up empty on the map.
        extended_field_set = set(
            ExtendedField.objects.filter(
                contributor=contributor,
                field_name__in=NonstandardField.EXTENDED_FIELDS.keys(),
            ).values_list('field_name', flat=True).distinct())

        field_list = sorted(extended_field_set | nonstandard_field_set)

        return Response(field_list)
