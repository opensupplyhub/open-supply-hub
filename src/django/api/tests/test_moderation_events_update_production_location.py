import json
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.test import override_settings
from django.core import mail
from waffle.testutils import override_switch

from api.constants import (
    APIV1CommonErrorMessages,
    APIV1MatchTypes,
    FacilityClaimStatuses,
)
from api.moderation_event_actions.approval.event_approval_template import (
    ANONYMIZE_SLC_SOURCES_SWITCH,
)
from api.models.contributor.contributor import Contributor
from api.models.moderation_event import ModerationEvent
from api.models.user import User
from api.models.facility.facility import Facility
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.source import Source
from api.models.partner_field import PartnerField
from api.models.extended_field import ExtendedField
from api.tests.base_moderation_events_production_location_test import (
    BaseModerationEventsProductionLocationTest,
)


@override_settings(DEBUG=True)
class ModerationEventsUpdateProductionLocationTest(
    BaseModerationEventsProductionLocationTest
):
    def setUp(self):
        super().setUp()

        self.source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="GB",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=self.source,
        )

        self.os_id = "GB2024338H7FA8R"
        self.facility_one = Facility.objects.create(
            id=self.os_id,
            name="Name",
            address="Address",
            country_code="GB",
            location=Point(0, 0),
            created_from=self.list_item,
        )

    def get_url(self):
        return "/api/v1/moderation-events/{}/production-locations/{}/".format(
            self.moderation_event_id, self.os_id
        )

    def test_not_authenticated(self):
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_not_authenticated(response)

    def test_permission_denied(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_permission_denied(response)

    def test_invalid_uuid_format(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url().replace(self.moderation_event_id, "invalid_uuid"),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_invalid_uuid_error(response)

    def test_moderation_event_not_found(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url().replace(
                self.moderation_event_id,
                "f65ec710-f7b9-4f50-b960-135a7ab24ee7",
            ),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_moderation_event_not_found(response)

    def test_moderation_event_not_pending(self):
        self.moderation_event.status = 'RESOLVED'
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_moderation_event_not_pending(response)

    def test_invalid_os_id_format(self):
        self.login_as_superuser()
        invalid_ids = [
            "A1234567ABCDEF",    # Less than 15 characters
            "ABC1234567ABCDEF",  # More than 15 characters
            "AB1234567abcdef",   # Contains lowercase letters
            "AB1234567AB!DEF",   # Contains special character
            "AB12345X7ABCDEF",   # Letter in the digit section
            "1234567ABABCDEF",   # Starts with digits
            "ABCD56789012345",   # Too many letters at the start
            "AB12345678ABCDEF"   # Too many digits
        ]

        for invalid_id in invalid_ids:
            response = self.client.patch(
                self.get_url().replace(self.os_id, invalid_id),
                data=json.dumps({}),
                content_type="application/json",
            )

            self.assertEqual(400, response.status_code)
            self.assertEqual(
                "The request path parameter is invalid.",
                response.data["detail"]
            )
            self.assertEqual("os_id", response.data["errors"][0]["field"])
            self.assertEqual(
                APIV1CommonErrorMessages.LOCATION_ID_NOT_VALID,
                response.data["errors"][0]["detail"],
            )

    def test_no_production_location_found_with_os_id(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url().replace(self.os_id, "UA2024341550R5D"),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(404, response.status_code)
        self.assertEqual(
            "The request path parameter is invalid.", response.data["detail"]
        )
        self.assertEqual("os_id", response.data["errors"][0]["field"])
        self.assertEqual(
            APIV1CommonErrorMessages.LOCATION_NOT_FOUND,
            response.data["errors"][0]["detail"],
        )

    def test_successful_update_production_location(self):
        self.login_as_superuser()
        old_updated_at = self.facility_one.updated_at

        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.facility_one.refresh_from_db()
        new_updated_at = self.facility_one.updated_at
        self.assertGreater(new_updated_at, old_updated_at)

        email = mail.outbox[0]
        self.assertEqual(email.subject, "Great News: your OS ID is ready!")
        self.assert_success_response(response, 200, 'MATCHED')

    def test_successful_add_production_location_without_geocode_result(self):
        self.moderation_event.cleaned_data["fields"]["lat"] = self.latitude
        self.moderation_event.cleaned_data["fields"]["lng"] = self.longitude

        self.moderation_event.geocode_result = {}
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.assert_successful_add_production_location_without_geocode_result(
            response, 200
        )

    def test_creation_of_source(self):
        # The anonymize_slc_sources switch is active by default, so a source
        # created for an approved SLC event is anonymized: its data stays
        # public and active, but it is not attributed to the contributor.
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

        sources = Source.objects.filter(contributor=self.contributor).order_by(
            "-created_at"
        )
        self.assertEqual(sources.count(), 2)

        source = sources.first()

        self.assert_source_creation(source, is_anonymized=True)

    @override_switch(ANONYMIZE_SLC_SOURCES_SWITCH, active=False)
    def test_creation_of_source_with_anonymization_disabled(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

        sources = Source.objects.filter(contributor=self.contributor).order_by(
            "-created_at"
        )
        self.assertEqual(sources.count(), 2)

        source = sources.first()

        self.assert_source_creation(source)

    def test_anonymized_source_keeps_data_but_hides_attribution(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

        index_row = FacilityIndex.objects.get(id=self.os_id)

        # The contributed name stays in the index data, flagged as
        # anonymized so serializers hide its attribution.
        name_entry = next(
            (
                entry
                for entry in index_row.facility_names
                if entry.get("name") == self.name
            ),
            None,
        )
        self.assertIsNotNone(name_entry)
        self.assertTrue(name_entry.get("is_anonymized"))

        # The contributor is listed but not publicly associated.
        contributor_entry = next(
            (
                entry
                for entry in index_row.contributors
                if entry.get("id") == self.contributor.id
            ),
            None,
        )
        self.assertIsNotNone(contributor_entry)
        self.assertFalse(contributor_entry.get("should_display_associations"))

        # The facility is not findable by filtering on the contributor.
        self.assertNotIn(self.contributor.id, index_row.contributors_id)

    @override_switch(ANONYMIZE_SLC_SOURCES_SWITCH, active=False)
    def test_attribution_kept_when_anonymization_disabled(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

        index_row = FacilityIndex.objects.get(id=self.os_id)

        name_entry = next(
            (
                entry
                for entry in index_row.facility_names
                if entry.get("name") == self.name
            ),
            None,
        )
        self.assertIsNotNone(name_entry)
        self.assertFalse(name_entry.get("is_anonymized"))

        contributor_entry = next(
            (
                entry
                for entry in index_row.contributors
                if entry.get("id") == self.contributor.id
            ),
            None,
        )
        self.assertIsNotNone(contributor_entry)
        self.assertTrue(contributor_entry.get("should_display_associations"))

        self.assertIn(self.contributor.id, index_row.contributors_id)

    def test_approved_claimant_slc_is_not_anonymized(self):
        # An approved claimant is already publicly named on the location,
        # so their contributions stay attributed and keep the claim
        # promotion.
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility_one,
            contact_person="Test Person",
            status=FacilityClaimStatuses.APPROVED,
        )

        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

        source = (
            Source.objects.filter(contributor=self.contributor)
            .order_by("-created_at")
            .first()
        )
        self.assert_source_creation(source, is_anonymized=False)

    def test_unapproved_claim_does_not_exempt_from_anonymization(self):
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility_one,
            contact_person="Test Person",
            status=FacilityClaimStatuses.PENDING,
        )

        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

        source = (
            Source.objects.filter(contributor=self.contributor)
            .order_by("-created_at")
            .first()
        )
        self.assert_source_creation(source, is_anonymized=True)

    def test_other_contributor_claim_does_not_exempt_from_anonymization(self):
        other_user = User.objects.create(email="claimant@example.com")
        other_contributor = Contributor.objects.create(
            admin=other_user,
            name="other claimant contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        FacilityClaim.objects.create(
            contributor=other_contributor,
            facility=self.facility_one,
            contact_person="Test Person",
            status=FacilityClaimStatuses.APPROVED,
        )

        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

        source = (
            Source.objects.filter(contributor=self.contributor)
            .order_by("-created_at")
            .first()
        )
        self.assert_source_creation(source, is_anonymized=True)

    def test_creation_of_source_for_api_moderation_event(self):
        self.moderation_event.source = ModerationEvent.Source.API
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

        sources = Source.objects.filter(contributor=self.contributor).order_by(
            "-created_at"
        )
        self.assertEqual(sources.count(), 2)

        source = sources.first()

        self.assert_source_creation(source)

    def test_creation_of_nonstandard_fields(self):
        self.add_nonstandard_fields_data()
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.assert_creation_of_nonstandard_fields(response, 200)

    def test_creation_of_facilitylistitem(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.assert_facilitylistitem_creation(
            response, 200, FacilityListItem.CONFIRMED_MATCH
        )

    def test_creation_of_extended_fields(self):
        self.add_extended_fields_data()
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.assert_extended_fields_creation(response, 200)

    def test_creation_of_facilitymatch(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.assert_facilitymatch_creation(
            response,
            200,
            APIV1MatchTypes.CONFIRMED_MATCH,
            FacilityMatch.CONFIRMED,
            FacilityMatch,
        )

    def test_creation_of_facilitymatchtemp(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assert_facilitymatch_creation(
            response,
            200,
            APIV1MatchTypes.CONFIRMED_MATCH,
            FacilityMatch.CONFIRMED,
            FacilityMatchTemp,
        )

    @patch(
        'api.moderation_event_actions.approval.'
        'update_production_location.UpdateProductionLocation.'
        'process_moderation_event'
    )
    def test_error_handling_during_processing(
        self, mock_process_moderation_event
    ):
        mock_process_moderation_event.side_effect = Exception(
            "Mocked processing error"
        )

        self.login_as_superuser()

        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.assert_processing_error(response)

    def test_update_production_location_with_partner_fields(self):
        partner_field_1 = PartnerField.objects.create(
            name='estimated_emissions_activity',
            type='float',
            unit='kg CO2e',
            label='Estimated Emissions Activity'
        )
        partner_field_2 = PartnerField.objects.create(
            name='estimated_annual_energy_consumption',
            type='int',
            unit='kWh',
            label='Estimated Annual Energy Consumption'
        )

        self.contributor.partner_fields.add(
            partner_field_1,
            partner_field_2
        )

        key_one = 'estimated_emissions_activity'
        key_two = 'estimated_annual_energy_consumption'

        self.moderation_event.cleaned_data['fields'][key_one] = 200.75
        self.moderation_event.cleaned_data['fields'][key_two] = 1500
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.assert_success_response(response, 200, 'MATCHED')

        partner_extended_fields = ExtendedField.objects.filter(
            facility_list_item__source__contributor=self.contributor,
            field_name__in=[
                'estimated_emissions_activity',
                'estimated_annual_energy_consumption'
            ]
        )
        self.assertEqual(partner_extended_fields.count(), 2)

        emissions_field = partner_extended_fields.get(
            field_name='estimated_emissions_activity'
        )
        energy_field = partner_extended_fields.get(
            field_name='estimated_annual_energy_consumption'
        )

        self.assertEqual(
            emissions_field.value,
            {"raw_value": 200.75}
        )
        self.assertEqual(
            energy_field.value,
            {"raw_value": 1500}
        )
