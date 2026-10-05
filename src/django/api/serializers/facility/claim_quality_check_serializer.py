from rest_framework import serializers

from api.models.facility.facility_claim import FacilityClaim


def _max_length(field_name):
    return FacilityClaim._meta.get_field(field_name).max_length


class ClaimQualityCheckSerializer(serializers.Serializer):
    '''
    Body of POST /api/facilities/{id}/claim/quality-check/: the name and
    address a claimant is about to assert. Each field has the length
    limit of its own claim column; blank is allowed because a blank
    asserts nothing and stands for the value the location lists.
    '''
    facility_name_english = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        max_length=_max_length('facility_name_english'),
    )
    facility_address = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        max_length=_max_length('facility_address'),
    )
