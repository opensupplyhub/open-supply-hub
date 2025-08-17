import os

from rest_framework import serializers
from django.core.validators import URLValidator
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from ...exceptions import BadRequestException

from api.models import FacilityClaim
from api.constants import FacilityClaimStatuses
from api.helpers.helpers import validate_workers_count
from api.serializers.facility.utils import add_http_prefix_to_url
from oar.settings import (
    MAX_ATTACHMENT_SIZE_IN_BYTES,
    MAX_ATTACHMENT_AMOUNT,
    ALLOWED_ATTACHMENT_EXTENSIONS
)


def validate_workers(value):
    try:
        if not value or not validate_workers_count(value):
            return None
        return value
    except (ValueError, TypeError):
        return None


def validate_url_field(field_name, value):
    if value == "":
        return value

    value = add_http_prefix_to_url(value)
    validator = URLValidator()
    try:
        validator(value)
    except DjangoValidationError as err:
        raise DRFValidationError(
            f"Enter a valid URL for '{field_name}'."
        ) from err

    return value


def validate_files(files):
    if len(files) > MAX_ATTACHMENT_AMOUNT:
        raise DRFValidationError(
            f"Maximum {MAX_ATTACHMENT_AMOUNT} attachments allowed."
        )

    for file in files:
        extension = os.path.splitext(file.name)[-1].lower()
        if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
            raise DRFValidationError(
                f"{file.name} has an unsupported file type."
            )

        if file.size > MAX_ATTACHMENT_SIZE_IN_BYTES:
            raise DRFValidationError(
                f"{file.name} exceeds the 5MB size limit."
            )

    return files


class FacilityCreateClaimSerializer(serializers.Serializer):
    your_name = serializers.CharField(
        max_length=255,
        required=True,
        allow_blank=False,
    )
    your_title = serializers.CharField(
        max_length=255,
        required=True,
        allow_blank=False,
    )
    your_business_website = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    business_website = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    business_linkedin_profile = serializers.CharField(
        max_length=255,
        required=True,
        allow_blank=True,
    )
    sectors = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    number_of_workers = serializers.CharField(
        required=False,
        validators=[validate_workers]
    )
    local_language_name = serializers.CharField(
        required=False,
        allow_blank=True
    )
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        validators=[validate_files]
    )
    claim_reason = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    def validate_claim_reason(self, value):
        from api.models.facility.claims_reason import ClaimsReason
        
        if value and value.strip():
            value = value.strip()
            # Allow "Other" or any valid claim reason from the database
            if value != 'Other':
                if not ClaimsReason.objects.filter(text=value, is_active=True).exists():
                    raise serializers.ValidationError(
                        "Invalid claim reason. Please select from available options or use 'Other'."
                    )
        return value

    def validate_your_business_website(self, value):
        return validate_url_field("your_business_website", value)

    def validate_business_website(self, value):
        return validate_url_field("business_website", value)

    def validate_business_linkedin_profile(self, value):
        return validate_url_field("business_linkedin_profile", value)

    def validate(self, data):
        facility = self.context["facility"]

        existing_claim = FacilityClaim.objects.filter(
            facility=facility,
            status__in=[
                FacilityClaimStatuses.PENDING,
                FacilityClaimStatuses.APPROVED
            ]
        ).values_list("status", flat=True)

        if FacilityClaimStatuses.PENDING in existing_claim:
            raise BadRequestException(
                "There is already a pending claim on this facility."
            )
        if FacilityClaimStatuses.APPROVED in existing_claim:
            raise BadRequestException(
                "There is already an approved claim on this facility."
            )

        return data
