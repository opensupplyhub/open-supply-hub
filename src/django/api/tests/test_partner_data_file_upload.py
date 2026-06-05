from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings

from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.partner_field import PartnerField
from api.models.source import Source
from api.models.user import User
from api.partner_data_file_upload.batch import (
    submit_partner_data_file_upload_job,
    validate_aws_batch_prerequisites,
)
from api.partner_data_file_upload.errors import format_upload_processing_error
from api.partner_data_file_upload.parsing.parser import PartnerFieldSheetParser
from api.partner_data_file_upload.processing.event_creator import (
    PartnerPatchModerationEventCreator,
)

PARTNER_BATCH_SETTINGS = {
    "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_QUEUE_NAME": (
        "queueTestPartnerDataFileUpload"
    ),
    "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_DEF_NAME": (
        "jobTestPartnerDataFileUpload"
    ),
}


class PartnerDataFileUploadTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="partner-upload@test.com")
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="Test Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.string_field = PartnerField.objects.create(
            name="custom_partner_field",
            type=PartnerField.STRING,
            label="Custom Partner Field",
        )
        self.object_field = PartnerField.objects.create(
            name="partner_object_field",
            type=PartnerField.OBJECT,
            label="Partner Object Field",
            json_schema={
                "type": "object",
                "properties": {
                    "metric_group": {
                        "type": "object",
                        "properties": {
                            "reporting_year": {"type": "integer"},
                        },
                    },
                },
            },
        )
        self.contributor.partner_fields.add(self.string_field, self.object_field)

        facility_list = FacilityList.objects.create(
            header="header",
            file_name="one",
            name="Test Facility List",
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor,
        )
        list_item = FacilityListItem.objects.create(
            name="Test Facility",
            address="123 Example Street",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        self.facility = Facility.objects.create(
            name=list_item.name,
            address=list_item.address,
            country_code=list_item.country_code,
            location=Point(-75.158, 39.961),
            created_from=list_item,
        )

    @override_settings(
        BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_QUEUE_NAME=None,
        BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_DEF_NAME="jobTestPartnerDataFileUpload",
    )
    def test_batch_validate_requires_partner_queue_setting(self):
        with self.assertRaises(ValueError) as context:
            validate_aws_batch_prerequisites()

        self.assertIn(
            "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_QUEUE_NAME",
            str(context.exception),
        )

    @override_settings(**PARTNER_BATCH_SETTINGS)
    @patch("api.partner_data_file_upload.batch.boto3.client")
    @patch("api.partner_data_file_upload.batch.boto3.Session")
    def test_batch_submit_uses_partner_queue_and_parameter(
        self,
        mock_session,
        mock_client,
    ):
        mock_session.return_value.get_credentials.return_value = Mock(
            access_key="key",
            secret_key="secret",
        )
        mock_session.return_value.get_credentials.return_value.get_frozen_credentials.return_value = Mock(  # noqa: E501
            access_key="key",
            secret_key="secret",
        )
        mock_client.return_value.submit_job.return_value = {"jobId": "job-123"}

        job_id = submit_partner_data_file_upload_job(
            "00000000-0000-0000-0000-000000000001"
        )

        self.assertEqual(job_id, "job-123")
        submit_kwargs = mock_client.return_value.submit_job.call_args.kwargs
        self.assertEqual(
            submit_kwargs["jobQueue"],
            "queueTestPartnerDataFileUpload",
        )
        self.assertEqual(
            submit_kwargs["jobDefinition"],
            "jobTestPartnerDataFileUpload",
        )
        self.assertEqual(
            submit_kwargs["parameters"],
            {"queueentryuuid": "00000000-0000-0000-0000-000000000001"},
        )

    def test_format_upload_processing_error_prefixes_infrastructure_failures(self):
        message = format_upload_processing_error(
            ValueError("AWS credentials are not configured.")
        )
        self.assertTrue(message.startswith("Contact developers:"))

    def test_format_upload_processing_error_keeps_sheet_validation_plain(self):
        message = format_upload_processing_error(
            ValueError("Sheet contains duplicate headers: os_id")
        )
        self.assertFalse(message.startswith("Contact developers:"))

    def test_validate_headers_rejects_duplicate_and_invalid_headers(self):
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_header_map(["os_id", "os_id"])

        self.assertIn("duplicate headers", str(context.exception))

        header_map = PartnerFieldSheetParser.build_header_map(
            ["os_id", "Bad-Column"]
        )
        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.validate_headers(header_map)

        self.assertIn("snake_case", str(context.exception))

    def test_build_column_mappings_rejects_unauthorized_partner_field(self):
        unauthorized = PartnerField.objects.create(
            name="unauthorized_field",
            type=PartnerField.STRING,
            label="Unauthorized Field",
        )

        with self.assertRaises(ValueError) as context:
            PartnerFieldSheetParser.build_column_mappings(
                [unauthorized.name],
                self.contributor,
            )

        self.assertIn("not authorized", str(context.exception))

    def test_build_patch_raw_data_builds_scalar_and_nested_values(self):
        mappings, _ = PartnerFieldSheetParser.build_column_mappings(
            [
                "custom_partner_field",
                "partner_object_field_metric_group_reporting_year",
            ],
            self.contributor,
        )
        raw_data = PartnerFieldSheetParser.build_patch_raw_data(
            {
                "os_id": self.facility.id,
                "custom_partner_field": "test value",
                "partner_object_field_metric_group_reporting_year": "2024",
            },
            mappings,
        )

        self.assertEqual(raw_data["custom_partner_field"], "test value")
        self.assertEqual(
            raw_data["partner_object_field"],
            {"metric_group": {"reporting_year": 2024}},
        )

    def test_create_rejects_unknown_os_id(self):
        mappings, _ = PartnerFieldSheetParser.build_column_mappings(
            ["custom_partner_field"],
            self.contributor,
        )
        creator = PartnerPatchModerationEventCreator(Mock())

        with self.assertRaises(ValueError) as context:
            creator.create(
                self.contributor,
                {
                    "os_id": "US0000000UNKNOWN",
                    "custom_partner_field": "test value",
                },
                mappings,
            )

        self.assertIn("was not found", str(context.exception))
