from api.models.facility.facility_index import FacilityIndex
from rest_framework.serializers import (
  ModelSerializer,
  SerializerMethodField,
)

from countries.lib.countries import COUNTRY_CHOICES
from ...facility_type_processing_type import (
    ALL_FACILITY_TYPE_CHOICES,
    ALL_PROCESSING_TYPE_CHOICES
)
from ...models import Contributor, FacilityClaim
from .facility_index_details_serializer import FacilityIndexDetailsSerializer
from .utils import _get_parent_company


class ApprovedFacilityClaimSerializer(ModelSerializer):
    facility = SerializerMethodField()
    countries = SerializerMethodField()
    contributors = SerializerMethodField()
    facility_types = SerializerMethodField()
    facility_parent_company = SerializerMethodField()
    affiliation_choices = SerializerMethodField()
    certification_choices = SerializerMethodField()
    production_type_choices = SerializerMethodField()

    class Meta:
        model = FacilityClaim
        fields = ('id', 'facility_description',
                  'facility_name_english', 'facility_name_native_language',
                  'facility_address', 'facility_location',
                  'facility_phone_number',
                  'facility_phone_number_publicly_visible',
                  'facility_website', 'facility_minimum_order_quantity',
                  'facility_average_lead_time', 'point_of_contact_person_name',
                  'point_of_contact_email', 'facility_workers_count',
                  'facility_female_workers_percentage',
                  'point_of_contact_publicly_visible',
                  'office_official_name', 'office_address',
                  'office_country_code', 'office_phone_number',
                  'office_info_publicly_visible',
                  'opening_date', 'closing_date',
                  'estimated_annual_throughput', 'energy_coal',
                  'energy_natural_gas', 'energy_diesel', 'energy_kerosene',
                  'energy_biomass', 'energy_charcoal',
                  'energy_animal_waste', 'energy_electricity', 'energy_other',
                  'facility', 'countries', 'facility_parent_company',
                  'contributors', 'facility_website_publicly_visible',
                  'facility_types', 'facility_type', 'other_facility_type',
                  'affiliation_choices', 'certification_choices',
                  'facility_affiliations', 'facility_certifications',
                  'facility_product_types', 'facility_production_types',
                  'production_type_choices', 'sector')

    def get_facility(self, claim):
        facility_index = FacilityIndex.objects.get(id=claim.facility.id)
        return FacilityIndexDetailsSerializer(
            facility_index, context=self.context).data

    def get_countries(self, _):
        return COUNTRY_CHOICES

    def get_contributors(self, _):
        return [
            (contributor.id, contributor.name)
            for contributor
            in Contributor.objects.all().order_by('name')
        ]

    def get_facility_types(self, _):
        return ALL_FACILITY_TYPE_CHOICES

    def get_facility_parent_company(self, claim):
        return _get_parent_company(claim)

    def get_affiliation_choices(self, _):
        return FacilityClaim.AFFILIATION_CHOICES

    def get_certification_choices(self, _):
        return FacilityClaim.CERTIFICATION_CHOICES

    def get_production_type_choices(self, _):
        return ALL_PROCESSING_TYPE_CHOICES
