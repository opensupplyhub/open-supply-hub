import os
from contextlib import contextmanager
from unittest.mock import Mock, patch

from django.contrib.gis.geos import Point
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import transaction
from django.test import RequestFactory, TestCase, override_settings

from api.admin import PartnerDataFileUploadAdmin, admin_site
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.partner_data_file_upload import PartnerDataFileUpload
from api.models.partner_field import PartnerField
from api.models.source import Source
from api.models.user import User
from api.partner_data_file_upload.batch import (
    submit_partner_data_file_upload_job,
    validate_aws_batch_prerequisites,
)
from api.partner_data_file_upload.errors import format_upload_processing_error
from api.partner_data_file_upload.parsing.parser import PartnerFieldSheetParser
from api.partner_data_file_upload.constants import (
    GOOGLE_SHEETS_HTTP_TIMEOUT_SECONDS,
)
from api.partner_data_file_upload.sheets.client import (
    GoogleSheetClient,
    SheetWorkbook,
)
from api.partner_data_file_upload.parsing.types import SheetProcessingContext
from api.partner_data_file_upload.processing.event_creator import (
    PartnerPatchModerationEventCreator,
)
from api.partner_data_file_upload.processing.processor import (
    PartnerDataFileUploadProcessor,
)

PARTNER_BATCH_SETTINGS = {
    "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_QUEUE_NAME": (
        "queueTestPartnerDataFileUpload"
    ),
    "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_DEF_NAME": (
        "jobTestPartnerDataFileUpload"
    ),
}


@contextmanager
def capture_on_commit_callbacks(*, execute=False):
    callbacks = []

    def capture(func, using=None, robust=False):
        callbacks.append(func)

    with patch.object(transaction, "on_commit", side_effect=capture):
        yield callbacks

    if execute:
        for callback in callbacks:
            callback()


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
        self.contributor.partner_fields.add(
            self.string_field,
            self.object_field,
        )

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

    def _admin_request(self):
        request = RequestFactory().get("/")
        request.user = self.user
        request.session = {}
        setattr(request, "_messages", FallbackStorage(request))
        return request

    @patch("api.partner_data_file_upload.sheets.client.build")
    @patch(
        "api.partner_data_file_upload.sheets.client."
        "google_auth_httplib2.AuthorizedHttp"
    )
    @patch("api.partner_data_file_upload.sheets.client.httplib2.Http")
    @patch(
        "api.partner_data_file_upload.sheets.client.service_account."
        "Credentials.from_service_account_info"
    )
    def test_google_sheet_client_from_env_uses_http_timeout(
        self,
        mock_from_service_account_info,
        mock_http,
        mock_authorized_http,
        mock_build,
    ):
        mock_from_service_account_info.return_value = Mock()
        mock_build.return_value = Mock()
        with patch.dict(
            os.environ,
            {"GOOGLE_SERVICE_ACCOUNT_CREDS_BASE64": "e30="},
        ):
            GoogleSheetClient.from_env()

        mock_http.assert_called_once_with(
            timeout=GOOGLE_SHEETS_HTTP_TIMEOUT_SECONDS,
        )
        mock_authorized_http.assert_called_once()
        mock_build.assert_called_once_with(
            "sheets",
            "v4",
            http=mock_authorized_http.return_value,
        )

    def test_column_letter_supports_multi_letter_columns(self):
        self.assertEqual(GoogleSheetClient._column_letter(0), "A")
        self.assertEqual(GoogleSheetClient._column_letter(25), "Z")
        self.assertEqual(GoogleSheetClient._column_letter(26), "AA")
        self.assertEqual(GoogleSheetClient._column_letter(27), "AB")
        self.assertEqual(GoogleSheetClient._column_letter(701), "ZZ")

    def test_load_workbook_uses_sheet_column_count_for_range(self):
        mock_service = Mock()
        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {  # noqa: E501
            "sheets": [
                {
                    "properties": {
                        "title": "Partner Data",
                        "sheetId": 0,
                        "gridProperties": {"columnCount": 30},
                    }
                }
            ]
        }
        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {  # noqa: E501
            "values": [["os_id", "custom_partner_field"]]
        }
        client = GoogleSheetClient(mock_service)
        link = "https://docs.google.com/spreadsheets/d/abc123/edit"

        client.load_workbook(link)

        get_values_kwargs = (
            mock_service.spreadsheets.return_value.values.return_value
            .get.call_args.kwargs
        )
        self.assertEqual(get_values_kwargs["range"], "Partner Data!A:AD")

    def test_ensure_tracking_columns_expands_grid_when_sheet_is_full(self):
        mock_service = Mock()
        headers = [f"field_{index}" for index in range(23)]
        workbook = SheetWorkbook(
            spreadsheet_id="sheet-123",
            sheet_name="90_valid_10000_rows",
            tab_id=7,
            column_count=23,
            headers=headers,
            rows=[],
        )
        client = GoogleSheetClient(mock_service)

        column_indexes = client.ensure_tracking_columns(workbook)

        batch_update_kwargs = (
            mock_service.spreadsheets.return_value.batchUpdate.call_args.kwargs
        )
        self.assertEqual(
            batch_update_kwargs["spreadsheetId"],
            "sheet-123",
        )
        self.assertEqual(
            batch_update_kwargs["body"]["requests"][0][
                "updateSheetProperties"
            ]["properties"]["gridProperties"]["columnCount"],
            25,
        )
        self.assertEqual(workbook.column_count, 25)
        self.assertEqual(column_indexes["error"], 23)
        self.assertEqual(column_indexes["moderation_id"], 24)
        update_calls = (
            mock_service.spreadsheets.return_value.values.return_value
            .update.call_args_list
        )
        self.assertEqual(len(update_calls), 2)
        self.assertEqual(
            update_calls[0].kwargs["range"],
            "90_valid_10000_rows!X1",
        )
        self.assertEqual(
            update_calls[1].kwargs["range"],
            "90_valid_10000_rows!Y1",
        )

    def test_ensure_tracking_columns_skips_grid_expand_when_room_exists(self):
        mock_service = Mock()
        workbook = SheetWorkbook(
            spreadsheet_id="sheet-123",
            sheet_name="Partner Data",
            tab_id=1,
            column_count=26,
            headers=["os_id", "custom_partner_field"],
            rows=[],
        )
        client = GoogleSheetClient(mock_service)

        column_indexes = client.ensure_tracking_columns(workbook)

        mock_service.spreadsheets.return_value.batchUpdate.assert_not_called()
        self.assertEqual(workbook.column_count, 26)
        self.assertEqual(column_indexes["error"], 2)
        self.assertEqual(column_indexes["moderation_id"], 3)

    def test_ensure_tracking_columns_skips_writes_for_existing_columns(
        self,
    ):
        mock_service = Mock()
        workbook = SheetWorkbook(
            spreadsheet_id="sheet-123",
            sheet_name="Partner Data",
            tab_id=1,
            column_count=26,
            headers=["os_id", "error", "moderation_id"],
            rows=[],
        )
        client = GoogleSheetClient(mock_service)

        column_indexes = client.ensure_tracking_columns(workbook)

        mock_service.spreadsheets.return_value.batchUpdate.assert_not_called()
        mock_service.spreadsheets.return_value.values.return_value.update.assert_not_called()  # noqa: E501
        self.assertEqual(column_indexes["error"], 1)
        self.assertEqual(column_indexes["moderation_id"], 2)

    @override_settings(
        BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_QUEUE_NAME=None,
        BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_DEF_NAME=(
            "jobTestPartnerDataFileUpload"
        ),
    )
    def test_batch_validate_requires_partner_queue_setting(self):
        with self.assertRaises(ValueError) as context:
            validate_aws_batch_prerequisites()

        self.assertIn(
            "BATCH_PARTNER_DATA_FILE_UPLOAD_JOB_QUEUE_NAME",
            str(context.exception),
        )

    @override_settings(**PARTNER_BATCH_SETTINGS)
    @patch("api.admin.submit_partner_data_file_upload_job")
    def test_admin_create_persists_processing_before_batch_submit(
        self,
        mock_submit_job,
    ):
        mock_submit_job.return_value = "job-456"
        request = self._admin_request()
        upload = PartnerDataFileUpload(
            google_drive_file_link=(
                "https://docs.google.com/spreadsheets/d/test-sheet"
            ),
            contributor=self.contributor,
        )
        admin = PartnerDataFileUploadAdmin(
            PartnerDataFileUpload,
            admin_site,
        )

        with capture_on_commit_callbacks(execute=True):
            admin.save_model(request, upload, Mock(), change=False)

        saved = PartnerDataFileUpload.objects.get(pk=upload.pk)
        self.assertEqual(
            saved.status,
            PartnerDataFileUpload.Status.PROCESSING,
        )
        self.assertEqual(saved.batch_job_id, "job-456")
        mock_submit_job.assert_called_once_with(upload.pk)

    @override_settings(**PARTNER_BATCH_SETTINGS)
    @patch("api.admin.submit_partner_data_file_upload_job")
    def test_admin_create_marks_failed_when_batch_submit_fails(
        self,
        mock_submit_job,
    ):
        mock_submit_job.side_effect = ValueError(
            "AWS credentials are not configured."
        )
        request = self._admin_request()
        upload = PartnerDataFileUpload(
            google_drive_file_link=(
                "https://docs.google.com/spreadsheets/d/test-sheet"
            ),
            contributor=self.contributor,
        )
        admin = PartnerDataFileUploadAdmin(
            PartnerDataFileUpload,
            admin_site,
        )

        with capture_on_commit_callbacks(execute=True):
            admin.save_model(request, upload, Mock(), change=False)

        saved = PartnerDataFileUpload.objects.get(pk=upload.pk)
        self.assertEqual(saved.status, PartnerDataFileUpload.Status.FAILED)
        self.assertTrue(
            saved.processing_error.startswith("Contact developers:")
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

    def test_format_upload_processing_error_prefixes_infrastructure(
        self,
    ):
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

    def test_row_has_existing_outcome_detects_moderation_id_or_error(self):
        self.assertTrue(
            PartnerFieldSheetParser.row_has_existing_outcome(
                {
                    "os_id": self.facility.id,
                    "moderation_id": "existing-moderation-id",
                }
            )
        )
        self.assertTrue(
            PartnerFieldSheetParser.row_has_existing_outcome(
                {
                    "os_id": self.facility.id,
                    "error": "existing error",
                }
            )
        )
        self.assertFalse(
            PartnerFieldSheetParser.row_has_existing_outcome(
                {
                    "os_id": self.facility.id,
                    "custom_partner_field": "value",
                }
            )
        )
        self.assertFalse(
            PartnerFieldSheetParser.row_has_existing_outcome(
                {
                    "os_id": self.facility.id,
                    "moderation_id": "",
                    "error": "   ",
                }
            )
        )

    def test_process_rows_skips_rows_with_existing_outcome(self):
        mock_sheets = Mock()
        processor = PartnerDataFileUploadProcessor(mock_sheets)
        processor.event_creator = Mock()
        processor.event_creator.create.return_value = "new-moderation-id"

        workbook = SheetWorkbook(
            spreadsheet_id="sheet-123",
            sheet_name="Partner Data",
            tab_id=1,
            column_count=5,
            headers=[
                "os_id",
                "custom_partner_field",
                "error",
                "moderation_id",
            ],
            rows=[
                ["", "", "", ""],
                [
                    self.facility.id,
                    "value1",
                    "",
                    "existing-moderation-id",
                ],
                [self.facility.id, "value2", "existing error", ""],
                [self.facility.id, "value3", "", ""],
            ],
        )
        header_map = PartnerFieldSheetParser.build_header_map(
            workbook.headers,
        )
        mappings, partner_fields = (
            PartnerFieldSheetParser.build_column_mappings(
                ["custom_partner_field"],
                self.contributor,
            )
        )
        context = SheetProcessingContext(
            workbook=workbook,
            data_columns=["custom_partner_field"],
            header_map=header_map,
            column_mappings=mappings,
            partner_fields_by_name=partner_fields,
            tracking_columns={"error": 2, "moderation_id": 3},
            cols_count=4,
        )
        upload = PartnerDataFileUpload.objects.create(
            google_drive_file_link=(
                "https://docs.google.com/spreadsheets/d/test-sheet"
            ),
            contributor=self.contributor,
            status=PartnerDataFileUpload.Status.PROCESSING,
        )

        stats = processor._process_rows(upload, context)

        self.assertEqual(stats["rows_skipped_empty"], 1)
        self.assertEqual(stats["rows_skipped_existing"], 2)
        self.assertEqual(stats["rows_succeeded"], 1)
        self.assertEqual(stats["rows_failed"], 0)
        processor.event_creator.create.assert_called_once()
        mock_sheets.mark_row.assert_called_once()
