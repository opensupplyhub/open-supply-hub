import os
from datetime import date

from rest_framework import serializers
from django.core.validators import URLValidator
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from api.exceptions import BadRequestException

from api.models import FacilityClaim
from api.constants import FacilityClaimStatuses
from api.constants import JS_MAX_SAFE_INTEGER
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


def validate_non_future_date(value):
    '''Validate that a date is not in the future.'''
    if value and value > date.today():
        raise DRFValidationError(
            'Please enter a valid date (not in the future).'
        )
    return value


def validate_date_range(opening_date, closing_date):
    '''Validate that opening date is before or equal to closing date.'''
    if opening_date and closing_date and opening_date > closing_date:
        raise DRFValidationError({
            'opening_date': (
                'Opening date must be before or equal to closing date.'
            ),
            'closing_date': (
                'Closing date must be after or equal to opening date.'
            )
        })


class EmissionsFieldsMixin(serializers.Serializer):
    MIN_VALUE = 1
    MAX_VALUE = JS_MAX_SAFE_INTEGER
    EMISSION_INT_FIELDS = (
        'estimated_annual_throughput',
        'energy_coal',
        'energy_natural_gas',
        'energy_diesel',
        'energy_kerosene',
        'energy_biomass',
        'energy_charcoal',
        'energy_animal_waste',
        'energy_electricity',
        'energy_other',
    )

    def get_fields(self):
        fields = super().get_fields()
        min_value = getattr(self, 'MIN_VALUE', EmissionsFieldsMixin.MIN_VALUE)
        max_value = getattr(self, 'MAX_VALUE', JS_MAX_SAFE_INTEGER)

        fields['opening_date'] = serializers.DateField(
            required=False,
            allow_null=True,
            validators=[validate_non_future_date],
        )
        fields['closing_date'] = serializers.DateField(
            required=False,
            allow_null=True,
            validators=[validate_non_future_date],
        )

        for field_name in self.EMISSION_INT_FIELDS:
            fields[field_name] = serializers.IntegerField(
                required=False,
                allow_null=True,
                min_value=min_value,
                max_value=max_value,
            )

        return fields

    def validate(self, attrs):
        validate_date_range(
            attrs.get('opening_date'),
            attrs.get('closing_date'),
        )
        return attrs


class FacilityCreateClaimSerializer(
    EmissionsFieldsMixin,
    serializers.Serializer,
):
    your_name = serializers.CharField(
        max_length=200,
        required=True,
        allow_blank=False,
    )
    your_title = serializers.CharField(
        max_length=200,
        required=True,
        allow_blank=False,
    )
    your_business_website = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
    )
    point_of_contact_person_name = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
    )
    point_of_contact_email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    point_of_contact_publicly_visible = serializers.BooleanField(
        required=False,
        default=False,
        allow_null=False,
    )
    business_website = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
    )
    business_linkedin_profile = serializers.CharField(
        max_length=200,
        required=True,
        allow_blank=True,
    )
    sectors = serializers.ListField(
        child=serializers.CharField(
            max_length=50,
            allow_blank=False,
            allow_null=False,
        ),
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


class FacilityUpdateClaimEmissionsSerializer(EmissionsFieldsMixin):
    MIN_VALUE = 0
    facility_name_english = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=300,
    )
    facility_address = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )
    facility_website = serializers.URLField(
        required=False,
        allow_blank=True,
        max_length=200,
    )
    facility_minimum_order_quantity = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
    )
    facility_average_lead_time = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
    )
    point_of_contact_person_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
    )
    point_of_contact_email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    claimant_location_relationship = serializers.CharField(
        allow_blank=True,
        required=False,
        max_length=250
    )
    claimant_employment_verification_method = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=250
    )
    location_address_verification_method = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=250
    )
    claimant_linkedin_profile_url = serializers.URLField(
        required=False,
        allow_blank=True,
        max_length=200
    )
    facility_phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )
    office_phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )
    facility_description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )
    office_official_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )
    office_address = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )
    office_country_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2
    )
    parent_company_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )
    facility_affiliations = serializers.ListField(
        child=serializers.ChoiceField(
            choices=FacilityClaim.AFFILIATION_CHOICES,
        ),
        required=False
    )
    facility_certifications = serializers.ListField(
        child=serializers.ChoiceField(
            choices=FacilityClaim.CERTIFICATION_CHOICES,
        ),
        required=False
    )
    facility_female_workers_percentage = serializers.IntegerField(
        required=False,
        max_value=100,
        min_value=0
    )
    facility_minimum_order_quantity = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )
    facility_average_lead_time = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )
    facility_product_types = serializers.ListField(
        child=serializers.CharField(
            max_length=50,
            allow_blank=False,
            allow_null=False,
        ),
        required=False
    )
    facility_production_types = serializers.ListField(
        child=serializers.CharField(
            max_length=50,
            allow_blank=False,
            allow_null=False,
        ),
        required=False
    )
    facility_type = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=300
    )
    claimant_location_relationship = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=250,
    )
    claimant_employment_verification_method = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=250,
    )
    location_address_verification_method = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=250,
    )
    claimant_linkedin_profile_url = serializers.URLField(
        required=False,
        allow_blank=True,
        max_length=200,
    )
    facility_phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
    )
    office_phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
    )

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

        # Validate date relationships for free emissions estimate.
        validate_date_range(
            data.get('opening_date'),
            data.get('closing_date')
        )

        return data
