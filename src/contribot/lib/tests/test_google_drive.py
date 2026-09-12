"""Unit tests for :mod:`google_drive`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from google_drive import GoogleDrive


def test_constructor_loads_secret_and_builds_service(monkeypatch):
    monkeypatch.setenv("GOOGLE_DRIVE_SHARED_DIRECTORY_ID", "folder-1")
    secrets = MagicMock()
    secrets.get_secret_value.return_value = {
        "SecretString": '{"type": "service_account", "client_email": "a@b.c"}'
    }

    with (
        patch("google_drive.service_account.Credentials") as mock_creds,
        patch("google_drive.build") as mock_build,
    ):
        mock_creds.from_service_account_info.return_value = MagicMock()
        mock_build.return_value = MagicMock(name="drive")
        drive = GoogleDrive(
            secret_arn="arn:aws:secretsmanager:us-east-1:123:secret:gdrive",
            secrets_client=secrets,
        )

    secrets.get_secret_value.assert_called_once_with(
        SecretId="arn:aws:secretsmanager:us-east-1:123:secret:gdrive"
    )
    mock_build.assert_called_once_with(
        "drive",
        "v3",
        credentials=mock_creds.from_service_account_info.return_value,
        cache_discovery=False,
        static_discovery=True,
    )
    assert drive._folder_id == "folder-1"


def test_upload_file_returns_webview_link(tmp_path, monkeypatch):
    monkeypatch.setenv("GOOGLE_DRIVE_SHARED_DIRECTORY_ID", "folder-1")
    path = tmp_path / "report.xlsx"
    path.write_bytes(b"xlsx")

    files = MagicMock()
    files.create.return_value.execute.return_value = {
        "id": "file-123",
        "webViewLink": "https://drive.google.com/file/d/file-123/view",
    }
    service = MagicMock()
    service.files.return_value = files

    drive = GoogleDrive(drive_service=service, folder_id="folder-1")
    url = drive.upload_file(str(path))

    assert url == "https://drive.google.com/file/d/file-123/view"
    create_kwargs = files.create.call_args.kwargs
    assert create_kwargs["body"]["name"] == "report.xlsx"
    assert create_kwargs["body"]["parents"] == ["folder-1"]
    assert create_kwargs["supportsAllDrives"] is True


def test_upload_file_falls_back_to_constructed_url(tmp_path, monkeypatch):
    monkeypatch.setenv("GOOGLE_DRIVE_SHARED_DIRECTORY_ID", "folder-1")
    path = tmp_path / "report.xlsx"
    path.write_bytes(b"xlsx")

    files = MagicMock()
    files.create.return_value.execute.return_value = {"id": "file-456"}
    service = MagicMock()
    service.files.return_value = files

    drive = GoogleDrive(drive_service=service)
    assert drive.upload_file(str(path)) == "https://drive.google.com/file/d/file-456/view"
