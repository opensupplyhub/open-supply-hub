from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from api.partner_data_file_upload.batch import (
    submit_partner_data_file_upload_job,
    validate_aws_batch_prerequisites,
)
from api.partner_data_file_upload.errors import format_upload_processing_error


class PartnerDataFileUploadBatchTest(TestCase):
    @override_settings(BATCH_JOB_QUEUE_NAME=None, BATCH_JOB_DEF_NAME="jobTestDefault")
    def test_validate_requires_batch_job_queue_name(self):
        with self.assertRaises(ValueError) as context:
            validate_aws_batch_prerequisites()

        self.assertIn("BATCH_JOB_QUEUE_NAME", str(context.exception))

    @override_settings(
        BATCH_JOB_QUEUE_NAME="queueTestPartnerDataFileUpload",
        BATCH_JOB_DEF_NAME=None,
    )
    def test_validate_requires_batch_job_def_name(self):
        with self.assertRaises(ValueError) as context:
            validate_aws_batch_prerequisites()

        self.assertIn("BATCH_JOB_DEF_NAME", str(context.exception))

    @override_settings(
        BATCH_JOB_QUEUE_NAME="queueTestPartnerDataFileUpload",
        BATCH_JOB_DEF_NAME="jobTestPartnerDataFileUpload",
    )
    @patch("api.partner_data_file_upload.batch.boto3.Session")
    def test_validate_requires_aws_credentials(self, mock_session):
        mock_session.return_value.get_credentials.return_value = None

        with self.assertRaises(ValueError) as context:
            validate_aws_batch_prerequisites()

        self.assertIn("AWS credentials", str(context.exception))

    @override_settings(
        BATCH_JOB_QUEUE_NAME="queueTestPartnerDataFileUpload",
        BATCH_JOB_DEF_NAME="jobTestPartnerDataFileUpload",
    )
    @patch("api.partner_data_file_upload.batch.boto3.client")
    @patch("api.partner_data_file_upload.batch.boto3.Session")
    def test_submit_job_checks_credentials_before_client_call(
        self,
        mock_session,
        mock_client,
    ):
        mock_session.return_value.get_credentials.return_value = None

        with self.assertRaises(ValueError) as context:
            submit_partner_data_file_upload_job("00000000-0000-0000-0000-000000000001")

        self.assertIn("AWS credentials", str(context.exception))
        mock_client.assert_not_called()

    @override_settings(
        BATCH_JOB_QUEUE_NAME="queueTestPartnerDataFileUpload",
        BATCH_JOB_DEF_NAME="jobTestPartnerDataFileUpload",
    )
    @patch("api.partner_data_file_upload.batch.boto3.client")
    @patch("api.partner_data_file_upload.batch.boto3.Session")
    def test_submit_job_returns_job_id(self, mock_session, mock_client):
        mock_session.return_value.get_credentials.return_value = Mock(
            access_key="key",
            secret_key="secret",
        )
        mock_session.return_value.get_credentials.return_value.get_frozen_credentials.return_value = Mock(  # noqa: E501
            access_key="key",
            secret_key="secret",
        )
        mock_client.return_value.submit_job.return_value = {
            "jobId": "job-123",
        }

        job_id = submit_partner_data_file_upload_job(
            "00000000-0000-0000-0000-000000000001"
        )

        self.assertEqual(job_id, "job-123")
        mock_client.assert_called_once()
        submit_kwargs = mock_client.return_value.submit_job.call_args.kwargs
        self.assertEqual(
            submit_kwargs["jobQueue"],
            "queueTestPartnerDataFileUpload",
        )
        self.assertEqual(
            submit_kwargs["jobDefinition"],
            "jobTestPartnerDataFileUpload",
        )

    def test_format_upload_processing_error_prefixes_system_failures(self):
        message = format_upload_processing_error(
            RuntimeError("unexpected failure")
        )

        self.assertTrue(message.startswith("Contact developers:"))

    def test_format_upload_processing_error_keeps_sheet_validation_plain(self):
        message = format_upload_processing_error(
            ValueError("Sheet contains duplicate headers: os_id")
        )

        self.assertFalse(message.startswith("Contact developers:"))

    def test_format_upload_processing_error_prefixes_infrastructure_value_errors(
        self,
    ):
        message = format_upload_processing_error(
            ValueError("AWS credentials are not configured.")
        )

        self.assertTrue(message.startswith("Contact developers:"))
