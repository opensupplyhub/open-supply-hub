from rest_framework import serializers

from api.serializers.facility.facility_claim_attachments_serializer import (
    FacilityClaimAttachmentsSerializer
)
from api.serializers.facility.facility_create_claim_serializer import (
    FacilityCreateClaimSerializer
)

# Maps the claim form's field names (as accepted by
# FacilityCreateClaimSerializer and submitted by the React claim flow)
# onto FacilityClaim model field names. Fields absent from this map use
# the same name on both sides. This is the single place the mapping
# lives — the create view, the pending-claim edit view and the
# claimant-facing read serializer all derive from it.
CLAIM_FORM_TO_MODEL_FIELDS = {
    'your_name': 'contact_person',
    'your_title': 'job_title',
    'your_business_website': 'website',
    'business_website': 'facility_website',
    'business_linkedin_profile': 'linkedin_profile',
    'local_language_name': 'facility_name_native_language',
    'number_of_workers': 'facility_workers_count',
    'sectors': 'sector',
}


def claim_model_field_for(form_field):
    return CLAIM_FORM_TO_MODEL_FIELDS.get(form_field, form_field)


class EditPendingClaimSerializer(FacilityCreateClaimSerializer):
    '''
    Serializer for a claimant editing their own PENDING claim.

    Derived from FacilityCreateClaimSerializer so every validation rule
    (URL formats, date-not-in-future, workers count, field lengths) is
    written exactly once and the create and edit paths cannot drift.
    Always used with partial=True, so only submitted fields are
    validated and applied. Attachments are managed through their own
    endpoints, not through this serializer.
    '''
    # Attachment files are sub-resource operations on pending claims.
    files = None

    def validate(self, data):
        # The parent validate() rejects facilities that already have a
        # PENDING or APPROVED claim — that is create-time protection
        # and would reject every edit, so it is deliberately not
        # inherited.
        return data

    def apply_to_claim(self, claim):
        '''
        Copy every validated, submitted field onto the claim instance
        (without saving), translating form field names to model field
        names. Returns the list of model field names that were changed.
        '''
        changed_fields = []
        for form_field, value in self.validated_data.items():
            model_field = claim_model_field_for(form_field)
            if getattr(claim, model_field) != value:
                setattr(claim, model_field, value)
                changed_fields.append(model_field)
        return changed_fields


class PendingClaimSerializer(serializers.Serializer):
    '''
    Claimant-facing read serializer for their own pending claim. Field
    names mirror the claim form (the create serializer's names) so the
    frontend can hydrate the edit form without a second mapping.

    Attachments are exposed as metadata only (id, file_name,
    uploaded_at) — never as storage URLs. Downloads go through the
    authorization-checked download endpoint.
    '''
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    os_id = serializers.CharField(source='facility_id', read_only=True)
    facility_name = serializers.SerializerMethodField()

    your_name = serializers.CharField(source='contact_person')
    your_title = serializers.CharField(source='job_title')
    your_business_website = serializers.CharField(source='website')
    business_website = serializers.CharField(source='facility_website')
    business_linkedin_profile = serializers.CharField(
        source='linkedin_profile'
    )
    local_language_name = serializers.CharField(
        source='facility_name_native_language'
    )
    number_of_workers = serializers.CharField(
        source='facility_workers_count'
    )
    sectors = serializers.ListField(source='sector')

    point_of_contact_person_name = serializers.CharField()
    point_of_contact_email = serializers.EmailField()
    point_of_contact_publicly_visible = serializers.BooleanField()
    opening_date = serializers.DateField()
    estimated_annual_throughput = serializers.IntegerField()
    energy_coal = serializers.IntegerField()
    energy_natural_gas = serializers.IntegerField()
    energy_diesel = serializers.IntegerField()
    energy_kerosene = serializers.IntegerField()
    energy_biomass = serializers.IntegerField()
    energy_charcoal = serializers.IntegerField()
    energy_animal_waste = serializers.IntegerField()
    energy_electricity = serializers.IntegerField()
    energy_other = serializers.IntegerField()
    claimant_location_relationship = serializers.CharField()
    claimant_employment_verification_method = serializers.CharField()
    location_address_verification_method = serializers.CharField()
    claimant_linkedin_profile_url = serializers.URLField()
    facility_phone_number = serializers.CharField()
    office_phone_number = serializers.CharField()
    facility_description = serializers.CharField()
    office_official_name = serializers.CharField()
    office_address = serializers.CharField()
    office_country_code = serializers.CharField()
    parent_company_name = serializers.CharField()
    facility_affiliations = serializers.ListField()
    facility_certifications = serializers.ListField()
    facility_female_workers_percentage = serializers.IntegerField()
    facility_minimum_order_quantity = serializers.CharField()
    facility_average_lead_time = serializers.CharField()
    facility_product_types = serializers.ListField()
    facility_production_types = serializers.ListField()
    facility_type = serializers.CharField()

    attachments = serializers.SerializerMethodField()

    def get_facility_name(self, claim):
        return claim.facility.name if claim.facility else None

    def get_attachments(self, claim):
        return FacilityClaimAttachmentsSerializer(
            claim.facilityclaimattachments_set.all().order_by('id'),
            many=True,
        ).data
