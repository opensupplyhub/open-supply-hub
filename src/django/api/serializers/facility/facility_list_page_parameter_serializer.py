from rest_framework.serializers import (
    IntegerField,
    Serializer
)

from api.constants import FacilitiesListSettings


class FacilityListPageParameterSerializer(Serializer):
    '''
    The serializer validates the page query parameter for the list action of
    the FacilitiesViewSet.
    '''
    page = IntegerField(
        required=False,
        max_value=FacilitiesListSettings.DEFAULT_PAGE_LIMIT,
        min_value=1,
        error_messages={
            'max_value': (
                'This value must be less or equal to '
                f'{FacilitiesListSettings.DEFAULT_PAGE_LIMIT}. If you need '
                'access to more data, please contact '
                'support@opensupplyhub.org.'),
        }
    )
