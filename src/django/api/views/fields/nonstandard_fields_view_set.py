
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import GenericViewSet

from ...models.extended_field import ExtendedField
from ...models.nonstandard_field import NonstandardField
from ..contributor.get_contributor import get_contributor


class NonstandardFieldsViewSet(ListModelMixin, GenericViewSet):
    """
    View the fields a contributor can show on their embedded map: the
    standard extended fields plus the nonstandard columns they have submitted.

    With `?detail=true` the response also says which of those fields the
    contributor has data for, so the settings screen can highlight them.
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

        if request.query_params.get('detail') != 'true':
            return Response(field_list)

        # A nonstandard column only exists because the contributor uploaded
        # it. A standard field has data when they have contributed it.
        extended_field_set = set(
            ExtendedField.objects.filter(
                contributor=contributor,
                field_name__in=NonstandardField.EXTENDED_FIELDS.keys(),
            ).values_list('field_name', flat=True).distinct())

        return Response({
            'fields': sorted(field_list),
            'with_data': sorted(extended_field_set | nonstandard_field_set),
        })
