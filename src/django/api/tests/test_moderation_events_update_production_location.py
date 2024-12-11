import json
from unittest.mock import patch

from django.test import override_settings
from django.utils.timezone import now

from api.tests.base_moderation_events_production_location_test import (
    BaseModerationEventsProductionLocationTest,
)

from api.constants import APIV1MatchTypes
from api.models import ModerationEvent, User, Contributor
from api.models.extended_field import ExtendedField
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.nonstandard_field import NonstandardField
from api.models.source import Source
from django.contrib.gis.geos import Point


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

    def test_permission_denied(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertPermissionDenied(response)

        # self.assertEqual(403, response.status_code)
        # self.assertEqual(
        #     "Only the Moderator can perform this action.",
        #     response.data["detail"],
        # )

    def test_invalid_uuid_format(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                "invalid_uuid"
            ),
            # self.get_url().replace(self.moderation_event_id, "invalid_uuid"),
            data=json.dumps({}),
            content_type="application/json",
        )
        # self.assertEqual(400, response.status_code)
        # self.assertEqual(
        #     "The request path parameter is invalid.", response.data["detail"]
        # )
        # self.assertEqual("moderation_id", response.data["errors"][0]["field"])
        # self.assertEqual(
        #     "Invalid UUID format.", response.data["errors"][0]["detail"]
        # )
        self.assertInvalidUUIDError(response)

    def test_moderation_event_not_found(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                "f65ec710-f7b9-4f50-b960-135a7ab24ee7"
            ),
            # self.get_url().replace(
            #     self.moderation_event_id,
            #     "f65ec710-f7b9-4f50-b960-135a7ab24ee7",
            # ),
            data=json.dumps({}),
            content_type="application/json",
        )
        # self.assertEqual(404, response.status_code)
        # self.assertEqual(
        #     "The request path parameter is invalid.", response.data["detail"]
        # )
        # self.assertEqual("moderation_id", response.data["errors"][0]["field"])
        # self.assertEqual(
        #     "Moderation event not found.", response.data["errors"][0]["detail"]
        # )
        self.assertModerationEventNotFound(response)

    def test_moderation_event_not_pending(self):
        self.moderation_event.status = 'RESOLVED'
        self.moderation_event.save()

        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            # self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )
        # self.assertEqual(410, response.status_code)
        # self.assertEqual(
        #     "The moderation event should be in PENDING status.",
        #     response.data["detail"],
        # )
        self.assertModerationEventNotPending(response)

    def test_empty_request_body(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            # self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            "The request body contains invalid or missing fields.",
            response.data["detail"],
        )
        self.assertEqual("os_id", response.data["errors"][0]["field"])
        self.assertEqual(
            "This field is required.", response.data["errors"][0]["detail"]
        )

    def test_invalid_os_id_format(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            # self.get_url(),
            data=json.dumps({"os_id": "invalid_os_id"}),
            content_type="application/json",
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            "The request body contains invalid or missing fields.",
            response.data["detail"],
        )
        self.assertEqual("os_id", response.data["errors"][0]["field"])
        self.assertEqual(
            "The format of the os_id is invalid.",
            response.data["errors"][0]["detail"],
        )

    def test_no_production_location_found_with_os_id(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            # self.get_url(),
            data=json.dumps({"os_id": "UA2024341550R5D"}),
            content_type="application/json",
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            "The request body contains invalid or missing fields.",
            response.data["detail"],
        )
        self.assertEqual("os_id", response.data["errors"][0]["field"])
        self.assertEqual(
            "No production location found with the provided os_id.",
            response.data["errors"][0]["detail"],
        )

    def test_successful_update_production_location(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            # self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        # self.assertEqual(200, response.status_code)
        # self.assertIn("os_id", response.data)
        # self.assertEqual(self.os_id, response.data["os_id"])

        # moderation_event = ModerationEvent.objects.get(
        #     uuid=self.moderation_event_id
        # )
        # self.assertEqual(moderation_event.status, 'APPROVED')
        # self.assertEqual(moderation_event.os_id, response.data["os_id"])
        self.assert_success_response(response, 200)

    def test_successful_add_production_location_without_geocode_result(self):
        self.moderation_event.cleaned_data["fields"]["lat"] = self.latitude
        self.moderation_event.cleaned_data["fields"]["lng"] = self.longitude

        self.moderation_event.geocode_result = {}
        self.moderation_event.save()

        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event_id
            ),
            # self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.assertEqual(200, response.status_code)

    def test_creation_of_source(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            # self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

        sources = Source.objects.filter(contributor=self.contributor).order_by(
            "-created_at"
        )
        self.assertEqual(sources.count(), 2)

        source = sources.first()
        # self.assertIsNotNone(source)
        # self.assertEqual(source.source_type, Source.SINGLE)
        # self.assertEqual(source.is_active, True)
        # self.assertEqual(source.is_public, True)
        # self.assertEqual(source.create, True)
        self.assert_source_creation(source)

    def test_creation_of_nonstandard_fields(self):
        self.moderation_event.cleaned_data["raw_json"][
            "nonstandard_field_one"
        ] = "Nonstandard Field One"
        self.moderation_event.cleaned_data["raw_json"][
            "nonstandard_field_two"
        ] = "Nonstandard Field Two"

        self.moderation_event.save()

        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            # self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        # self.assertEqual(200, response.status_code)

        # nonstandard_fields = NonstandardField.objects.filter(
        #     contributor=self.contributor
        # )
        # created_fields = nonstandard_fields.values_list(
        #     'column_name', flat=True
        # )

        # self.assertIn('nonstandard_field_one', created_fields)
        # self.assertIn('nonstandard_field_two', created_fields)
        # self.assertNotIn('country', created_fields)
        # self.assertNotIn('name', created_fields)
        # self.assertNotIn('address', created_fields)
        self.assert_creation_of_nonstandard_fields(response, 200)

    def test_creation_of_facilitylistitem(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            # self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        # self.assertEqual(200, response.status_code)

        # facility_list_item = FacilityListItem.objects.get(
        #     facility_id=response.data["os_id"]
        # )
        # self.assertIsNotNone(facility_list_item)
        # self.assertEqual(facility_list_item.row_index, 0)
        # self.assertEqual(facility_list_item.status, FacilityListItem.MATCHED)
        # self.assertEqual(
        #     facility_list_item.name, self.moderation_event.cleaned_data["name"]
        # )
        # self.assertEqual(
        #     facility_list_item.address,
        #     self.moderation_event.cleaned_data["address"],
        # )
        # self.assertEqual(
        #     facility_list_item.country_code,
        #     self.moderation_event.cleaned_data["country_code"],
        # )
        # self.assertEqual(
        #     facility_list_item.clean_name,
        #     self.moderation_event.cleaned_data["clean_name"],
        # )
        # self.assertEqual(
        #     facility_list_item.clean_address,
        #     self.moderation_event.cleaned_data["clean_address"],
        # )
        self.assert_facilitylistitem_creation(response, 200)

    def test_creation_of_extended_fields(self):
        self.moderation_event.cleaned_data['fields'][
            'number_of_workers'
        ] = '100'
        self.moderation_event.cleaned_data['fields'][
            'native_language_name'
        ] = 'Native Language Name'
        self.moderation_event.cleaned_data['fields'][
            'parent_company'
        ] = 'Parent Company'
        self.moderation_event.cleaned_data['fields']['product_type'] = [
            "Product Type"
        ]
        self.moderation_event.cleaned_data['fields']['facility_type'] = {
            "raw_values": "Facility Type",
            "processed_values": ["Facility Type"],
        }
        self.moderation_event.cleaned_data['fields']['processing_type'] = {
            "raw_values": "Processing Type",
            "processed_values": ["Processing Type"],
        }

        self.moderation_event.save()

        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            # self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        # self.assertEqual(200, response.status_code)

        # item = FacilityListItem.objects.get(facility_id=response.data["os_id"])
        # extended_fields = ExtendedField.objects.filter(
        #     facility_list_item=item.id
        # )
        # self.assertEqual(6, extended_fields.count())

        # field_names = [field.field_name for field in extended_fields]
        # self.assertIn(ExtendedField.NUMBER_OF_WORKERS, field_names)
        # self.assertIn(ExtendedField.NATIVE_LANGUAGE_NAME, field_names)
        # self.assertIn(ExtendedField.PARENT_COMPANY, field_names)
        # self.assertIn(ExtendedField.PRODUCT_TYPE, field_names)
        # self.assertIn(ExtendedField.FACILITY_TYPE, field_names)
        # self.assertIn(ExtendedField.PROCESSING_TYPE, field_names)

        # for extended_field in extended_fields:
        #     self.assertEqual(extended_field.facility_id, item.facility_id)
        self.assert_extended_fields_creation(response, 200)

    def test_creation_of_facilitymatch(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            # self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        # self.assertEqual(200, response.status_code)

        # facility_list_item = FacilityListItem.objects.get(
        #     facility_id=response.data["os_id"]
        # )
        # facility_match = FacilityMatch.objects.get(
        #     facility_list_item=facility_list_item.id
        # )
        # self.assertIsNotNone(facility_match)
        # self.assertEqual(facility_match.status, FacilityMatch.AUTOMATIC)
        # self.assertEqual(
        #     facility_match.facility_id, facility_list_item.facility_id
        # )
        # self.assertEqual(facility_match.confidence, 1)
        # self.assertEqual(
        #     facility_match.results,
        #     {
        #         "match_type": APIV1MatchTypes.CONFIRMED_MATCH,
        #     },
        # )
        self.assert_facilitymatch_creation(
            response, 200, APIV1MatchTypes.CONFIRMED_MATCH, FacilityMatch
        )

    def test_creation_of_facilitymatchtemp(self):
        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()
        response = self.client.patch(
            "/api/v1/moderation-events/{}/production-locations/".format(
                self.moderation_event.uuid
            ),
            # self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )
        # self.assertEqual(200, response.status_code)

        # facility_list_item = FacilityListItem.objects.get(
        #     facility_id=response.data["os_id"]
        # )
        # facility_match_temp = FacilityMatchTemp.objects.get(
        #     facility_list_item=facility_list_item.id
        # )
        # self.assertIsNotNone(facility_match_temp)
        # self.assertEqual(facility_match_temp.status, FacilityMatch.AUTOMATIC)
        # self.assertEqual(
        #     facility_match_temp.facility_id, facility_list_item.facility_id
        # )
        # self.assertEqual(facility_match_temp.confidence, 1)
        # self.assertEqual(
        #     facility_match_temp.results,
        #     {
        #         "match_type": APIV1MatchTypes.CONFIRMED_MATCH,
        #     },
        # )
        self.assert_facilitymatch_creation(
            response, 200, APIV1MatchTypes.CONFIRMED_MATCH, FacilityMatchTemp
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

        # self.client.login(
        #     email=self.superuser_email, password=self.superuser_password
        # )
        self.login_as_superuser()

        response = self.client.patch(
            f"/api/v1/moderation-events/{self.moderation_event_id}/"
            "production-locations/",
            # self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        # self.assertEqual(response.status_code, 500)
        # self.assertEqual(
        #     response.data,
        #     {
        #         "detail": "An unexpected error occurred while processing the "
        #         "request."
        #     },
        # )
        # self.assertEqual(
        #     ModerationEvent.objects.get(uuid=self.moderation_event_id).status,
        #     ModerationEvent.Status.PENDING,
        # )
        self.assert_processing_error(response)
