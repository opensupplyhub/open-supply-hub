from datetime import date

from rest_framework import serializers
from contricleaner.lib.helpers.clean import clean
from django.core.validators import URLValidator
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from api.exceptions import BadRequestException

from api.models import FacilityClaim
from api.constants import FacilityClaimStatuses
from api.constants import JS_MAX_SAFE_INTEGER
from api.helpers.claim_attachments import validate_attachment_files
from api.helpers.helpers import validate_workers_count
from api.serializers.facility.utils import add_http_prefix_to_url


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
    return validate_attachment_files(files)


def validate_non_future_date(value):
    '''Validate that a date is not in the future.'''
    if value and value > date.today():
        raise DRFValidationError(
            'Please enter a valid date (not in the future).'
        )
    return value


def validate_claimed_name_or_address(field_name, value):
    '''
    Strip and normalize a claimed name or address: blank becomes None
    (the model columns are nullable and the tracked-change logic treats
    NULL and '' as equal), and a value that ContriCleaner's clean()
    reduces to nothing is rejected with ContriCleaner's wording, since
    that is the rule the value must pass when it is recorded as a
    contribution at approval. clean() only strips whitespace and a fixed
    set of characters (newlines, -, /, ', ,, : and surrounding quotes), so
    other punctuation-only values such as '...' pass here just as they
    would in a list upload.
    '''
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if not clean(value):
        raise serializers.ValidationError(
            f'{field_name} cannot consist solely of punctuation or '
            'whitespace.'
        )
    return value


class FacilityCreateClaimSerializer(serializers.Serializer):
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
    opening_date = serializers.DateField(
        required=False,
        validators=[validate_non_future_date]
    )
    estimated_annual_throughput = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
    )
    energy_coal = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
    )
    energy_natural_gas = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
    )
    energy_diesel = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
    )
    energy_kerosene = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
    )
    energy_biomass = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
    )
    energy_charcoal = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
    )
    energy_animal_waste = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
    )
    energy_electricity = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
    )
    energy_other = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=JS_MAX_SAFE_INTEGER
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
    # The name and address the claimant asserts for the production
    # location. Optional so the form can omit them while the
    # enable_claim_name_address_edit switch is off. Validated with the
    # same rule ContriCleaner applies, so recording them as a contribution
    # at approval cannot fail on them later. Blank is normalized to None.
    facility_name_english = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )
    facility_address = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )

    def validate_your_business_website(self, value):
        return validate_url_field("your_business_website", value)

    def validate_business_website(self, value):
        return validate_url_field("business_website", value)

    def validate_business_linkedin_profile(self, value):
        return validate_url_field("business_linkedin_profile", value)

    def validate_facility_name_english(self, value):
        return validate_claimed_name_or_address(
            'facility_name_english', value
        )

    def validate_facility_address(self, value):
        return validate_claimed_name_or_address('facility_address', value)

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
