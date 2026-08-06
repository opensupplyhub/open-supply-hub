"""Google Drive client for uploading ContriBot validation reports."""

from __future__ import annotations

import json
import logging
import mimetypes
import os
from typing import Any, Optional

import boto3
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]


class GoogleDrive:
    """Upload files to a shared Google Drive folder via a service account."""

    def __init__(
        self,
        *,
        folder_id: Optional[str] = None,
        secret_arn: Optional[str] = None,
        secrets_client: Optional[Any] = None,
        drive_service: Optional[Any] = None,
    ):
        self._folder_id = folder_id or os.environ["GOOGLE_DRIVE_SHARED_DIRECTORY_ID"]
        if drive_service is not None:
            self._service = drive_service
            return

        arn = secret_arn or os.environ["GOOGLE_DRIVE_SERVICE_KEY_SECRET_ARN"]
        client = secrets_client or boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=arn)
        if "SecretString" not in response:
            raise RuntimeError(f"Secret {arn} has no SecretString")

        info = json.loads(response["SecretString"])
        credentials = service_account.Credentials.from_service_account_info(
            info,
            scopes=SCOPES,
        )
        self._service = build("drive", "v3", credentials=credentials, cache_discovery=False)

    def upload_file(self, path: str, *, name: Optional[str] = None) -> str:
        """Upload ``path`` into the shared directory and return a view URL."""
        filename = name or os.path.basename(path)
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        file_metadata = {
            "name": filename,
            "parents": [self._folder_id],
        }
        media = MediaFileUpload(path, mimetype=mime_type, resumable=True)

        logger.info("Uploading %s to Google Drive folder %s", filename, self._folder_id)
        uploaded = (
            self._service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )

        file_id = uploaded.get("id")
        report_url = uploaded.get("webViewLink") or (
            f"https://drive.google.com/file/d/{file_id}/view" if file_id else ""
        )
        if not report_url:
            raise RuntimeError("Google Drive upload did not return a file id or link")

        logger.info("Uploaded report to Google Drive: %s", report_url)
        return report_url
