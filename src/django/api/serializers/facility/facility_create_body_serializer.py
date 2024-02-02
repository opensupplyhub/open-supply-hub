from rest_framework.serializers import (
    CharField,
    ListField,
    Serializer,
    URLField,
    ValidationError
)

from ...processing import get_country_code
from ..pipe_separated_field import PipeSeparatedField


class FacilityCreateBodySerializer(Serializer):
    sector = PipeSeparatedField(
        required=False,
        allow_empty=False,
        child=CharField(required=True, max_length=200))
    product_type = PipeSeparatedField(
        required=False,
        allow_empty=False,
        child=CharField(required=True, max_length=200))
    sector_product_type = PipeSeparatedField(
        required=False,
        allow_empty=False,
        child=CharField(required=True, max_length=200))

    country = CharField(required=True)
    name = CharField(required=True, max_length=200)
    address = CharField(required=True, max_length=200)
    ppe_product_types = ListField(
        required=False, child=CharField(required=True, max_length=50))
    ppe_contact_phone = CharField(required=False, max_length=20)
    ppe_contact_email = CharField(required=False)
    ppe_website = URLField(required=False)

    def validate_country(self, value):
        try:
            return get_country_code(value)
        except ValueError as exc:
            raise ValidationError(exc) from exc
