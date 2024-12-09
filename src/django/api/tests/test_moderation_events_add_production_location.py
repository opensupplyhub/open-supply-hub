import json
from unittest.mock import patch

from django.test import override_settings
from django.utils.timezone import now

from rest_framework.test import APITestCase

from api.constants import APIV1MatchTypes
from api.models import ModerationEvent, User, Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.nonstandard_field import NonstandardField
from api.models.source import Source


@override_settings(DEBUG=True)
class ModerationEventsAddProductionLocationTest(APITestCase):
    def setUp(self):
        super().setUp()

        self.email = "test@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.superuser_email = "admin@example.com"
        self.superuser_password = "example123"
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.superuser_password
        )

        self.moderation_event_id = 'f65ec710-f7b9-4f50-b960-135a7ab24ee6'
        self.latitude = -53
        self.longitude = 142
        self.moderation_event = ModerationEvent.objects.create(
            uuid=self.moderation_event_id,
            created_at=now(),
            updated_at=now(),
            request_type='UPDATE',
            raw_data={
                "country": "United Kingdom",
                "name": "Test Name",
                "address": "Test Address, United Kingdom",
            },
            cleaned_data={
                "raw_json": {
                    "country": "United Kingdom",
                    "name": "Test Name",
                    "address": "Test Address, United Kingdom",
                },
                "name": "Test Name",
                "clean_name": "test name",
                "address": "Test Address, United Kingdom",
                "clean_address": "test address united kingdom",
                "country_code": "GB",
                "sector": ["Apparel"],
                "fields": {
                    "country": "United Kingdom",
                },
                "errors": [],
            },
            geocode_result={
                "geocoded_point": {
                    "lat": self.latitude,
                    "lng": self.longitude,
                },
                "geocoded_address": "Geocoded Address",
                "full_response": {
                    "status": "OK",
                    "results": [
                        {
                            "address_components": [
                                {
                                    "long_name": "Geocoded Address",
                                    "short_name": "Geocoded Address",
                                    "types": ["street_address"],
                                },
                            ],
                            "formatted_address": "Geocoded Address",
                        }
                    ],
                },
            },
            status='PENDING',
            source='API',
            contributor=self.contributor,
        )

    def test_permission_denied(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(403, response.status_code)

    def test_invalid_uuid_format(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                "invalid_uuid"
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(400, response.status_code)

    def test_moderation_event_not_found(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                "f65ec710-f7b9-4f50-b960-135a7ab24ee7"
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(404, response.status_code)

    def test_moderation_event_not_pending(self):
        self.moderation_event.status = 'RESOLVED'
        self.moderation_event.save()

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(410, response.status_code)

    def test_successful_add_production_location(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(201, response.status_code)
        self.assertIn("os_id", response.data)

        moderation_event = ModerationEvent.objects.get(
            uuid=self.moderation_event_id
        )
        self.assertEqual(moderation_event.status, 'APPROVED')
        self.assertEqual(moderation_event.os_id, response.data["os_id"])

    def test_successful_add_production_location_without_geocode_result(self):
        self.moderation_event.cleaned_data["fields"]["lat"] = self.latitude
        self.moderation_event.cleaned_data["fields"]["lng"] = self.longitude

        self.moderation_event.geocode_result = {}
        self.moderation_event.save()

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(201, response.status_code)

    def test_creation_of_source(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(201, response.status_code)

        source = Source.objects.get(contributor=self.contributor)
        self.assertIsNotNone(source)
        self.assertEqual(source.source_type, Source.SINGLE)
        self.assertEqual(source.is_active, True)
        self.assertEqual(source.is_public, True)
        self.assertEqual(source.create, True)

    def test_creation_of_nonstandard_fields(self):
        self.moderation_event.cleaned_data["raw_json"][
            "nonstandard_field_one"
        ] = "Nonstandard Field One"
        self.moderation_event.cleaned_data["raw_json"][
            "nonstandard_field_two"
        ] = "Nonstandard Field Two"

        self.moderation_event.save()

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(201, response.status_code)

        nonstandard_fields = NonstandardField.objects.filter(
            contributor=self.contributor
        )
        created_fields = nonstandard_fields.values_list(
            'column_name', flat=True
        )

        self.assertIn('nonstandard_field_one', created_fields)
        self.assertIn('nonstandard_field_two', created_fields)
        self.assertNotIn('country', created_fields)
        self.assertNotIn('name', created_fields)
        self.assertNotIn('address', created_fields)

    def test_creation_of_facilitylistitem(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(201, response.status_code)

        facility_list_item = FacilityListItem.objects.get(
            facility_id=response.data["os_id"]
        )
        self.assertIsNotNone(facility_list_item)
        self.assertEqual(facility_list_item.row_index, 0)
        self.assertEqual(facility_list_item.status, FacilityListItem.MATCHED)
        self.assertEqual(
            facility_list_item.name, self.moderation_event.cleaned_data["name"]
        )
        self.assertEqual(
            facility_list_item.address,
            self.moderation_event.cleaned_data["address"],
        )
        self.assertEqual(
            facility_list_item.country_code,
            self.moderation_event.cleaned_data["country_code"],
        )
        self.assertEqual(
            facility_list_item.clean_name,
            self.moderation_event.cleaned_data["clean_name"],
        )
        self.assertEqual(
            facility_list_item.clean_address,
            self.moderation_event.cleaned_data["clean_address"],
        )

    def test_creation_of_facility(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
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

    def test_creation_of_facilitymatch(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(201, response.status_code)

        facility_list_item = FacilityListItem.objects.get(
            facility_id=response.data["os_id"]
        )
        facility_match = FacilityMatch.objects.get(
            facility_list_item=facility_list_item.id
        )
        self.assertIsNotNone(facility_match)
        self.assertEqual(facility_match.status, FacilityMatch.AUTOMATIC)
        self.assertEqual(
            facility_match.facility_id, facility_list_item.facility_id
        )
        self.assertEqual(facility_match.confidence, 1)
        self.assertEqual(
            facility_match.results,
            {
                "match_type": APIV1MatchTypes.NEW_PRODUCTION_LOCATION,
            },
        )

    def test_creation_of_facilitymatchtemp(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(201, response.status_code)

        facility_list_item = FacilityListItem.objects.get(
            facility_id=response.data["os_id"]
        )
        facility_match_temp = FacilityMatchTemp.objects.get(
            facility_list_item=facility_list_item.id
        )
        self.assertIsNotNone(facility_match_temp)
        self.assertEqual(facility_match_temp.status, FacilityMatch.AUTOMATIC)
        self.assertEqual(
            facility_match_temp.facility_id, facility_list_item.facility_id
        )
        self.assertEqual(facility_match_temp.confidence, 1)
        self.assertEqual(
            facility_match_temp.results,
            {
                "match_type": APIV1MatchTypes.NEW_PRODUCTION_LOCATION,
            },
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

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        response = self.client.post(
            f"/api/v1/moderation-events/{self.moderation_event_id}/"
            "production-locations/",
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.data,
            {
                "detail": "An unexpected error occurred while processing the "
                "request."
            },
        )
        self.assertEqual(
            ModerationEvent.objects.get(uuid=self.moderation_event_id).status,
            ModerationEvent.Status.PENDING,
        )
