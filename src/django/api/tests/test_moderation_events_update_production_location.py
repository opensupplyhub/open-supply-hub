import json
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.test import override_settings

from api.constants import APIV1CommonErrorMessages, APIV1MatchTypes
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.source import Source
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

    def test_empty_request_body(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual(
            APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
            response.data["detail"],
        )
        self.assertEqual("os_id", response.data["errors"][0]["field"])
        self.assertEqual(
            "This field is required.", response.data["errors"][0]["detail"]
        )

    def test_invalid_os_id_format(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": "invalid_os_id"}),
            content_type="application/json",
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual(
            APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
            response.data["detail"],
        )
        self.assertEqual("os_id", response.data["errors"][0]["field"])
        self.assertEqual(
            "The format of the os_id is invalid.",
            response.data["errors"][0]["detail"],
        )

    def test_no_production_location_found_with_os_id(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": "UA2024341550R5D"}),
            content_type="application/json",
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual(
            APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
            response.data["detail"],
        )
        self.assertEqual("os_id", response.data["errors"][0]["field"])
        self.assertEqual(
            "No production location found with the provided os_id.",
            response.data["errors"][0]["detail"],
        )

    def test_successful_update_production_location(self):
        self.login_as_superuser()
        response = self.client.patch(
            self.get_url(),
            data=json.dumps({"os_id": self.os_id}),
            content_type="application/json",
        )

        self.assert_success_response(response, 200)

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
