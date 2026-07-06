"""Schema-only serializers for FacilityIndexDetailsSerializer.

These serializers exist solely to describe the shape of the data produced by
the ``SerializerMethodField`` getters on ``FacilityIndexDetailsSerializer``
(and its parent ``FacilityIndexSerializer``) so that ``drf-yasg`` can generate
an accurate Swagger/OpenAPI schema for ``GET /api/facilities/{id}/``.

They are wired up through ``@swagger_serializer_method`` on the corresponding
getters and are never used to actually serialize responses. Keeping the schema
derived from these typed serializers means the generated API documentation
stays in sync with the code instead of drifting from a hand-maintained sample.
"""
from rest_framework import serializers


class ContributorEntrySerializer(serializers.Serializer):
    """A single entry of the ``contributors`` array."""

    id = serializers.IntegerField(read_only=True, allow_null=True,
                                  required=False)
    name = serializers.CharField(read_only=True, allow_null=True)
    is_verified = serializers.BooleanField(read_only=True, required=False)
    contributor_name = serializers.CharField(
        read_only=True, allow_null=True, required=False
    )
    contributor_type = serializers.CharField(read_only=True, allow_null=True)
    list_name = serializers.CharField(
        read_only=True, allow_null=True, required=False
    )
    count = serializers.IntegerField(read_only=True)
    last_contributed_at = serializers.DateTimeField(
        read_only=True, allow_null=True
    )
    list_uploaded_at = serializers.DateTimeField(
        read_only=True, allow_null=True, required=False
    )


class SectorEntrySerializer(serializers.Serializer):
    """A single entry of the ``sector`` array."""

    updated_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, required=False)
    contributor_id = serializers.IntegerField(
        read_only=True, allow_null=True
    )
    contributor_name = serializers.CharField(
        read_only=True, allow_null=True
    )
    values = serializers.ListField(
        child=serializers.CharField(), read_only=True
    )
    is_from_claim = serializers.BooleanField(read_only=True)


class ExtendedFieldEntrySerializer(serializers.Serializer):
    """A single entry inside one of the ``extended_fields`` groups.

    Matches the output of ``FacilityIndexExtendedFieldListSerializer`` plus the
    extra keys added for the promoted ``name``/``address`` values.
    """

    id = serializers.IntegerField(
        read_only=True, allow_null=True, required=False
    )
    is_verified = serializers.BooleanField(read_only=True, required=False)
    value = serializers.JSONField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True, required=False)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    contributor_name = serializers.CharField(read_only=True, allow_null=True)
    contributor_id = serializers.IntegerField(read_only=True, allow_null=True)
    value_count = serializers.IntegerField(read_only=True, required=False)
    verified_count = serializers.IntegerField(read_only=True, required=False)
    is_from_claim = serializers.BooleanField(read_only=True, required=False)
    is_from_created_from = serializers.BooleanField(
        read_only=True, required=False
    )
    field_name = serializers.CharField(read_only=True)
    source_by = serializers.CharField(
        read_only=True, allow_null=True, allow_blank=True, required=False
    )
    unit = serializers.CharField(
        read_only=True, allow_blank=True, required=False
    )
    label = serializers.CharField(
        read_only=True, allow_blank=True, required=False
    )
    base_url = serializers.CharField(
        read_only=True, allow_blank=True, required=False
    )
    display_text = serializers.CharField(
        read_only=True, allow_blank=True, required=False
    )
    json_schema = serializers.JSONField(
        read_only=True, allow_null=True, required=False
    )


class ExtendedFieldsSerializer(serializers.Serializer):
    """The ``extended_fields`` object, keyed by extended field name.

    Keys mirror ``ExtendedField.FIELD_CHOICES``; each value is a list of
    ``ExtendedFieldEntrySerializer`` entries.
    """

    name = ExtendedFieldEntrySerializer(many=True, read_only=True)
    address = ExtendedFieldEntrySerializer(many=True, read_only=True)
    number_of_workers = ExtendedFieldEntrySerializer(
        many=True, read_only=True
    )
    native_language_name = ExtendedFieldEntrySerializer(
        many=True, read_only=True
    )
    facility_type = ExtendedFieldEntrySerializer(many=True, read_only=True)
    processing_type = ExtendedFieldEntrySerializer(many=True, read_only=True)
    product_type = ExtendedFieldEntrySerializer(many=True, read_only=True)
    parent_company = ExtendedFieldEntrySerializer(many=True, read_only=True)
    duns_id = ExtendedFieldEntrySerializer(many=True, read_only=True)
    lei_id = ExtendedFieldEntrySerializer(many=True, read_only=True)
    rba_id = ExtendedFieldEntrySerializer(many=True, read_only=True)
    isic_4 = ExtendedFieldEntrySerializer(many=True, read_only=True)


class OtherLocationSerializer(serializers.Serializer):
    """A single entry of the ``other_locations`` array."""

    lat = serializers.FloatField(read_only=True, allow_null=True)
    lng = serializers.FloatField(read_only=True, allow_null=True)
    contributor_id = serializers.IntegerField(read_only=True, allow_null=True)
    contributor_name = serializers.CharField(read_only=True, allow_null=True)
    notes = serializers.CharField(read_only=True, allow_null=True)
    is_from_claim = serializers.BooleanField(read_only=True, required=False)
    has_invalid_location = serializers.BooleanField(
        read_only=True, required=False
    )


class CreatedFromSerializer(serializers.Serializer):
    """The ``created_from`` object."""

    created_at = serializers.DateTimeField(read_only=True, allow_null=True)
    contributor = serializers.CharField(read_only=True, allow_null=True)


class ActivityReportEntrySerializer(serializers.Serializer):
    """A single entry of the ``activity_reports`` array."""

    id = serializers.IntegerField(read_only=True, allow_null=True)
    facility = serializers.CharField(read_only=True, allow_null=True)
    facility_name = serializers.CharField(read_only=True, allow_null=True)
    reported_by_contributor = serializers.CharField(
        read_only=True, allow_null=True
    )
    reason_for_report = serializers.CharField(read_only=True, allow_null=True)
    closure_state = serializers.CharField(read_only=True, allow_null=True)
    status = serializers.CharField(read_only=True, allow_null=True)
    status_change_reason = serializers.CharField(
        read_only=True, allow_null=True
    )
    status_change_by = serializers.CharField(read_only=True, allow_null=True)
    status_change_date = serializers.DateTimeField(
        read_only=True, allow_null=True
    )
    approved_at = serializers.DateTimeField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)


class ContributorFieldEntrySerializer(serializers.Serializer):
    """A single entry of the ``contributor_fields`` array (embed mode)."""

    value = serializers.CharField(read_only=True, allow_null=True)
    label = serializers.CharField(read_only=True)
    fieldName = serializers.CharField(read_only=True)


class ClaimInfoParentCompanySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, allow_null=True)
    name = serializers.CharField(read_only=True, allow_null=True)


class ClaimInfoEnergyConsumptionSerializer(serializers.Serializer):
    coal = serializers.FloatField(read_only=True, allow_null=True)
    natural_gas = serializers.FloatField(read_only=True, allow_null=True)
    diesel = serializers.FloatField(read_only=True, allow_null=True)
    kerosene = serializers.FloatField(read_only=True, allow_null=True)
    biomass = serializers.FloatField(read_only=True, allow_null=True)
    charcoal = serializers.FloatField(read_only=True, allow_null=True)
    animal_waste = serializers.FloatField(read_only=True, allow_null=True)
    electricity = serializers.FloatField(read_only=True, allow_null=True)
    other = serializers.FloatField(read_only=True, allow_null=True)


class ClaimInfoFacilitySerializer(serializers.Serializer):
    description = serializers.CharField(read_only=True, allow_null=True)
    name_english = serializers.CharField(read_only=True, allow_null=True)
    name_native_language = serializers.CharField(
        read_only=True, allow_null=True
    )
    address = serializers.CharField(read_only=True, allow_null=True)
    website = serializers.CharField(read_only=True, allow_null=True)
    parent_company = ClaimInfoParentCompanySerializer(
        read_only=True, allow_null=True
    )
    phone_number = serializers.CharField(read_only=True, allow_null=True)
    minimum_order = serializers.CharField(read_only=True, allow_null=True)
    average_lead_time = serializers.CharField(read_only=True, allow_null=True)
    workers_count = serializers.CharField(read_only=True, allow_null=True)
    female_workers_percentage = serializers.CharField(
        read_only=True, allow_null=True
    )
    facility_type = serializers.JSONField(read_only=True, allow_null=True)
    other_facility_type = serializers.CharField(
        read_only=True, allow_null=True
    )
    affiliations = serializers.JSONField(read_only=True, allow_null=True)
    certifications = serializers.JSONField(read_only=True, allow_null=True)
    product_types = serializers.JSONField(read_only=True, allow_null=True)
    production_types = serializers.JSONField(read_only=True, allow_null=True)
    sector = serializers.JSONField(read_only=True, allow_null=True)
    location = serializers.JSONField(read_only=True, allow_null=True)
    opening_date = serializers.CharField(read_only=True, allow_null=True)
    closing_date = serializers.CharField(read_only=True, allow_null=True)
    estimated_annual_throughput = serializers.CharField(
        read_only=True, allow_null=True
    )
    actual_annual_energy_consumption = ClaimInfoEnergyConsumptionSerializer(
        read_only=True, required=False
    )


class ClaimInfoContactSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True, allow_null=True)
    email = serializers.CharField(read_only=True, allow_null=True)


class ClaimInfoOfficeSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True, allow_null=True)
    address = serializers.CharField(read_only=True, allow_null=True)
    country = serializers.CharField(read_only=True, allow_null=True)
    phone_number = serializers.CharField(read_only=True, allow_null=True)


class ClaimInfoSerializer(serializers.Serializer):
    """The ``claim_info`` object returned for an approved (or pending) claim.

    ``null`` when the facility has no claim to display. For a pending claim
    only ``status`` is populated.
    """

    id = serializers.IntegerField(read_only=True, required=False)
    created_at = serializers.DateTimeField(read_only=True, required=False)
    status = serializers.CharField(read_only=True, required=False)
    contributor = serializers.CharField(
        read_only=True, allow_null=True, required=False
    )
    user_id = serializers.IntegerField(
        read_only=True, allow_null=True, required=False
    )
    facility = ClaimInfoFacilitySerializer(read_only=True, required=False)
    contact = ClaimInfoContactSerializer(
        read_only=True, allow_null=True, required=False
    )
    office = ClaimInfoOfficeSerializer(
        read_only=True, allow_null=True, required=False
    )
