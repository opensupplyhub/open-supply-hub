from rest_framework import serializers
from django.core.validators import URLValidator
from django.core.serializers import (
    CharField,
    FileField,
    ListField,
    Serializer,
    ValidationError
)
from django.utils.text import slugify
from datetime import datetime
import os

from api.models import FacilityClaim
from api.constants import FacilityClaimStatuses

# TODO: reuse number of workers validator
def validate_workers_count(value):
    if value and not value.isdigit():
        raise ValidationError("Number of workers must be a number.")
    return value

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

class FacilityCreateClaimSerializer(Serializer):
    your_name = CharField(max_length=255)
    your_title = CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    your_business_website = CharField(
        max_length=255,
        required=False,
        allow_blank=True, 
        validators=[URLValidator()]
    )
    business_website = CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        validators=[URLValidator()]
    )
    business_linkedin_profile = CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        validators=[URLValidator()]
    )
    sectors = ListField(
        child=CharField(),
        required=False
    )
    number_of_workers = CharField(
        required=False,
        validators=[validate_workers_count]
    )
    local_language_name = CharField(
        required=False,
        allow_blank=True
    )
    files = ListField(
        child=FileField(),
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
