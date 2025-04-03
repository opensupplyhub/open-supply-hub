from rest_framework import serializers
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from datetime import datetime
import os

from api.models import FacilityClaim
from api.constants import FacilityClaimStatuses
from api.helpers.helpers import validate_workers_count
from api.serializers.facility.utils import add_http_prefix_to_url


def validate_your_business_website(self, value):
    return add_http_prefix_to_url(value)

def validate_business_website(self, value):
    return add_http_prefix_to_url(value)

def validate_business_linkedin_profile(self, value):
    return add_http_prefix_to_url(value)

def validate_workers(value):
    try:
        if not value or not validate_workers_count(value):
            return None
        return value
    except (ValueError, TypeError):
        return None

def validate_files(files):
    ALLOWED_ATTACHMENT_EXTENSIONS = {".jpg", ".png", ".pdf"}
    MAX_ATTACHMENT_SIZE_IN_BYTES = 5 * 1024 * 1024
    MAX_ATTACHMENT_AMOUNT = 3

    if len(files) > MAX_ATTACHMENT_AMOUNT:
        raise ValidationError(f"Maximum {MAX_ATTACHMENT_AMOUNT} attachments allowed.")

    for file in files:
        extension = os.path.splitext(file.name)[-1].lower()
        if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
            raise ValidationError(f"{file.name} has an unsupported file type.")

        if file.size > MAX_ATTACHMENT_SIZE_IN_BYTES:
            raise ValidationError(f"{file.name} exceeds the 5MB size limit.")
    
    return files

class FacilityCreateClaimSerializer(serializers.Serializer):
    your_name = serializers.CharField(max_length=255)
    your_title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    your_business_website = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True, 
        validators=[URLValidator()]
    )
    business_website = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        validators=[URLValidator()]
    )
    business_linkedin_profile = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        validators=[URLValidator()]
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
            raise ValidationError("There is already a pending claim on this facility.")
        if FacilityClaimStatuses.APPROVED in existing_claim:
            raise ValidationError("There is already an approved claim on this facility.")
        
        return data
