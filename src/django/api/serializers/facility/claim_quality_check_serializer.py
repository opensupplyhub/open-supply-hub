from rest_framework import serializers

from api.models.facility.facility_claim import FacilityClaim

_MAX_LENGTH = FacilityClaim._meta.get_field('facility_name_english').max_length


class ClaimQualityCheckSerializer(serializers.Serializer):
    '''
    Body of POST /api/facilities/{id}/claim/quality-check/: the name and
    address a claimant is about to assert. Same length limit as the
    claim columns; blank is allowed because the check compares against
    what the location lists and a blank simply asserts nothing.
    '''
    facility_name_english = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        max_length=_MAX_LENGTH,
    )
    facility_address = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        max_length=_MAX_LENGTH,
    )
