from django.test import override_settings
from django.utils.timezone import now

from rest_framework.test import APITestCase

from api.constants import APIV1CommonErrorMessages
from api.models import Contributor, ModerationEvent, User
from api.models.extended_field import ExtendedField
from api.models.facility.facility_list_item import FacilityListItem
from api.models.nonstandard_field import NonstandardField
from api.models.source import Source


@override_settings(DEBUG=True)
class BaseModerationEventsProductionLocationTest(APITestCase):
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
        self.country = "United Kingdom"
        self.name = "Test Name"
        self.address = "Test Address, United Kingdom"
        self.moderation_event = ModerationEvent.objects.create(
            uuid=self.moderation_event_id,
            created_at=now(),
            updated_at=now(),
            request_type='UPDATE',
            raw_data={
                "country": self.country,
                "name": self.name,
                "address": self.address,
            },
            cleaned_data={
                "raw_json": {
                    "country": self.country,
                    "name": self.name,
                    "address": self.address,
                },
                "name": self.name,
                "clean_name": "test name",
                "address": self.address,
                "clean_address": "test address united kingdom",
                "country_code": "GB",
                "sector": ["Apparel"],
                "fields": {
                    "country": self.country,
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
                                    "long_name": "Long Geocoded Address",
                                    "short_name": "Short Geocoded Address",
                                    "types": ["street_address"],
                                },
                            ],
                            "formatted_address": "Formatted Geocoded Address",
                        }
                    ],
                },
            },
            status='PENDING',
            source='API',
            contributor=self.contributor,
        )

    def login_as_superuser(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

    def login_as_regular_user(self):
        self.client.login(email=self.email, password=self.password)

    def get_url(self):
        return "/api/v1/moderation-events/{}/production-locations/".format(
            self.moderation_event_id
        )

    def assertPermissionDenied(self, response):
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "Only the Moderator can perform this action.",
            response.data["detail"],
        )

    def assertInvalidUUIDError(self, response):
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            "The request path parameter is invalid.", response.data["detail"]
        )
        self.assertEqual("moderation_id", response.data["errors"][0]["field"])
        self.assertEqual(
            "Invalid UUID format.", response.data["errors"][0]["detail"]
        )

    def assertModerationEventNotFound(self, response):
        self.assertEqual(404, response.status_code)
        self.assertEqual(
            "The request path parameter is invalid.", response.data["detail"]
        )
        self.assertEqual("moderation_id", response.data["errors"][0]["field"])
        self.assertEqual(
            APIV1CommonErrorMessages.MODERATION_EVENT_NOT_FOUND,
            response.data["errors"][0]["detail"],
        )

    def assertModerationEventNotPending(self, response):
        self.assertEqual(410, response.status_code)
        self.assertEqual(
            "The moderation event should be in PENDING status.",
            response.data["detail"],
        )

    def assert_success_response(self, response, status_code):
        self.assertEqual(status_code, response.status_code)
        self.assertIn("os_id", response.data)

        moderation_event = ModerationEvent.objects.get(
            uuid=self.moderation_event_id
        )
        self.assertEqual(moderation_event.status, 'APPROVED')
        self.assertEqual(moderation_event.os_id, response.data["os_id"])

    def assert_source_creation(self, source):
        self.assertIsNotNone(source)
        self.assertEqual(source.source_type, Source.SINGLE)
        self.assertEqual(source.is_active, True)
        self.assertEqual(source.is_public, True)
        self.assertEqual(source.create, True)

    def add_nonstandard_fields_data(self):
        self.moderation_event.cleaned_data["raw_json"][
            "nonstandard_field_one"
        ] = "Nonstandard Field One"
        self.moderation_event.cleaned_data["raw_json"][
            "nonstandard_field_two"
        ] = "Nonstandard Field Two"

    def assert_creation_of_nonstandard_fields(self, response, status_code):
        self.assertEqual(status_code, response.status_code)

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

    def assert_facilitylistitem_creation(self, response, status_code):
        self.assertEqual(status_code, response.status_code)

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

    def add_extended_fields_data(self):
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

    def assert_extended_fields_creation(self, response, status_code):
        self.assertEqual(status_code, response.status_code)

        item = FacilityListItem.objects.get(facility_id=response.data["os_id"])
        extended_fields = ExtendedField.objects.filter(
            facility_list_item=item.id
        )
        self.assertEqual(6, extended_fields.count())

        field_names = [field.field_name for field in extended_fields]
        self.assertIn(ExtendedField.NUMBER_OF_WORKERS, field_names)
        self.assertIn(ExtendedField.NATIVE_LANGUAGE_NAME, field_names)
        self.assertIn(ExtendedField.PARENT_COMPANY, field_names)
        self.assertIn(ExtendedField.PRODUCT_TYPE, field_names)
        self.assertIn(ExtendedField.FACILITY_TYPE, field_names)
        self.assertIn(ExtendedField.PROCESSING_TYPE, field_names)

        for extended_field in extended_fields:
            self.assertEqual(extended_field.facility_id, item.facility_id)

    def assert_facilitymatch_creation(
        self, response, status_code, match_type, model
    ):
        self.assertEqual(status_code, response.status_code)

        facility_list_item = FacilityListItem.objects.get(
            facility_id=response.data["os_id"]
        )
        facility_match = model.objects.get(
            facility_list_item=facility_list_item.id
        )
        self.assertIsNotNone(facility_match)
        self.assertEqual(facility_match.status, model.AUTOMATIC)
        self.assertEqual(
            facility_match.facility_id, facility_list_item.facility_id
        )
        self.assertEqual(facility_match.confidence, 1)
        self.assertEqual(
            facility_match.results,
            {
                "match_type": match_type,
            },
        )

    def assert_processing_error(self, response):
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
