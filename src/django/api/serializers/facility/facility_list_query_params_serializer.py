from rest_framework.serializers import (
    IntegerField,
    ChoiceField,
    Serializer,
)
from api.constants import MatchResponsibility
from api.models import FacilityList


FACILITY_LIST_ORDERING_CHOICES = (
    'created_at',
    '-created_at',
    'id',
    '-id',
)


class FacilityListQueryParamsSerializer(Serializer):
    contributor = IntegerField(required=False)
    match_responsibility = ChoiceField(choices=MatchResponsibility.CHOICES,
                                       required=False)
    status = ChoiceField(choices=[FacilityList.MATCHED, FacilityList.APPROVED,
                                  FacilityList.REJECTED, FacilityList.PENDING,
                                  FacilityList.REPLACED],
                         required=False)
    ordering = ChoiceField(choices=FACILITY_LIST_ORDERING_CHOICES,
                           required=False,
                           default='created_at')
    id__gt = IntegerField(required=False, min_value=0)
