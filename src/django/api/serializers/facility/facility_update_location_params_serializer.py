from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    CharField,
    IntegerField,
    DecimalField,
    Serializer,
)
from ...models import Contributor


class FacilityUpdateLocationParamsSerializer(Serializer):
    # The Google geocoder returns points with 7 decimals of precision, which is
    # "[the] practical limit of commercial surveying"
    # https://en.wikipedia.org/wiki/Decimal_degrees
    lat = DecimalField(max_digits=None, decimal_places=7, required=True)
    lng = DecimalField(max_digits=None, decimal_places=7, required=True)
    contributor_id = IntegerField(required=False)
    notes = CharField(required=False)

    def validate_lat(self, lat):
        if lat < -90 or lat > 90:
            raise ValidationError('lat must be between -90 and 90.')

    def validate_lng(self, lat):
        if lat < -180 or lat > 180:
            raise ValidationError('lng must be between -180 and 180.')

    def validate_contributor_id(self, contributor_id):
        if not Contributor.objects.filter(id=contributor_id).exists():
            raise ValidationError(
                f'Contributor {contributor_id} does not exist.')
