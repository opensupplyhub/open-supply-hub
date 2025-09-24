import json
from unittest.mock import patch

from django.test import override_settings
from django.core import mail

from api.constants import APIV1MatchTypes
from api.models.facility.facility import Facility
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
class ModerationEventsAddProductionLocationTest(
    BaseModerationEventsProductionLocationTest
):
    def get_url(self):
        return "/api/v1/moderation-events/{}/production-locations/".format(
            self.moderation_event_id
        )

    def test_not_authenticated(self):
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_not_authenticated(response)

    def test_permission_denied(self):
        self.login_as_regular_user()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_permission_denied(response)

    def test_invalid_uuid_format(self):
        self.login_as_superuser()
        response = self.client.post(
            self.get_url().replace(self.moderation_event_id, "invalid_uuid"),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_invalid_uuid_error(response)

    def test_moderation_event_not_found(self):
        self.login_as_superuser()
        response = self.client.post(
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
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_moderation_event_not_pending(response)

    def test_successful_add_production_location(self):
        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_success_response(response, 201, 'NEW_LOCATION')

    def test_successful_email_sending_for_new_location_created_from_slc_source(
            self):
        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_success_response(response, 201, 'NEW_LOCATION')

        # The moderation event is created inside the base class's setUp
        # method, and by default, its source is set to SLC.
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(
            email.subject,
            "Great News: your OS ID is ready! You can now claim your profile."
        )

    def test_no_email_sent_for_new_location_created_from_api_source(self):
        self.moderation_event.source = 'API'
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_success_response(response, 201, 'NEW_LOCATION')
        self.assertEqual(len(mail.outbox), 0)

    def test_successful_add_production_location_without_geocode_result(self):
        self.moderation_event.cleaned_data["fields"]["lat"] = self.latitude
        self.moderation_event.cleaned_data["fields"]["lng"] = self.longitude

        self.moderation_event.geocode_result = {}
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_successful_add_production_location_without_geocode_result(
            response, 201
        )

    def test_creation_of_source(self):
        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(201, response.status_code)

        source = Source.objects.get(contributor=self.contributor)

        self.assert_source_creation(source)

    def test_creation_of_nonstandard_fields(self):
        self.add_nonstandard_fields_data()
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_creation_of_nonstandard_fields(response, 201)

    def test_creation_of_facilitylistitem(self):
        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_facilitylistitem_creation(
            response, 201, FacilityListItem.MATCHED
        )

    def test_creation_of_facility(self):
        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(201, response.status_code)

        facility = Facility.objects.get(id=response.data["os_id"])

        self.assertIsNotNone(facility)
        self.assertEqual(
            facility.name, self.moderation_event.cleaned_data["name"]
        )
        self.assertEqual(
            facility.address, self.moderation_event.cleaned_data["address"]
        )
        self.assertEqual(
            facility.country_code,
            self.moderation_event.cleaned_data["country_code"],
        )

    def test_creation_of_extended_fields(self):
        self.add_extended_fields_data()
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_extended_fields_creation(response, 201)

    def test_creation_of_facilitymatch(self):
        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_facilitymatch_creation(
            response,
            201,
            APIV1MatchTypes.NEW_PRODUCTION_LOCATION,
            FacilityMatch.AUTOMATIC,
            FacilityMatch,
        )

    def test_creation_of_facilitymatchtemp(self):
        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_facilitymatch_creation(
            response,
            201,
            APIV1MatchTypes.NEW_PRODUCTION_LOCATION,
            FacilityMatch.AUTOMATIC,
            FacilityMatchTemp,
        )

    @patch(
        'api.moderation_event_actions.approval.'
        'add_production_location.AddProductionLocation.'
        'process_moderation_event'
    )
    def test_error_handling_during_processing(
        self, mock_process_moderation_event
    ):
        mock_process_moderation_event.side_effect = Exception(
            "Mocked processing error"
        )

        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_processing_error(response)

    def test_add_production_location_with_valid_partner_fields(self):
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

        self.moderation_event.cleaned_data['fields']\
            ['estimated_emissions_activity'] = 150.5
        self.moderation_event.cleaned_data['fields']\
            ['estimated_annual_energy_consumption'] = 1000
        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.post(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_success_response(response, 201, 'NEW_LOCATION')

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
            {"raw_value": 150.5}
        )
        self.assertEqual(
            energy_field.value,
            {"raw_value": 1000}
        )
