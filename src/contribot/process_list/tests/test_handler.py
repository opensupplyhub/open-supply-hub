"""Unit tests for the ContriBot ``process_list`` handler."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Allow ``import handler`` and ``from lib...`` imports when tests run locally.
CONTRIBOT_DIR = Path(__file__).resolve().parents[2]
PROCESS_LIST_DIR = CONTRIBOT_DIR / "process_list"
for path in (str(CONTRIBOT_DIR), str(PROCESS_LIST_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

import handler  # noqa: E402


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("CONTRIBOT_STATE_TABLE_NAME", "contribot-state")
    monkeypatch.setenv("AWS_STORAGE_BUCKET_NAME", "files-bucket")
    monkeypatch.setenv("GOOGLE_DRIVE_SHARED_DIRECTORY_ID", "folder-1")
    monkeypatch.setenv(
        "GOOGLE_DRIVE_SERVICE_KEY_SECRET_ARN",
        "arn:aws:secretsmanager:us-east-1:123:secret:gdrive",
    )


def _patch_error_codes(monkeypatch):
    real_isfile = os.path.isfile

    def fake_isfile(path):
        if str(path).endswith("0000.error_codes.xlsx"):
            return True
        return real_isfile(path)

    monkeypatch.setattr(handler.os.path, "isfile", fake_isfile)


def _fake_download_bytes(payload: bytes):
    def fake_download(key, dest_path):
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        Path(dest_path).write_bytes(payload)
        return dest_path

    return fake_download


def _mock_bot_that_writes_report(mock_bot_cls, list_id: str):
    bot = MagicMock()
    bot.targetfilename = f"{list_id}.~PROCESSED.xlsx"
    summary = {
        "num_lines": 10,
        "num_errors": 2,
        "error_ratio": 0.2,
    }

    def fake_save(targetfolder="./out"):
        out = Path(targetfolder) / bot.targetfilename
        out.write_bytes(b"report")
        return summary

    bot.save.side_effect = fake_save
    mock_bot_cls.return_value = bot
    return bot


def _stub_workbook(mock_wb_cls, list_id: str) -> Path:
    workbook_path = Path("/tmp") / "contribot" / list_id / f"{list_id}.xlsx"
    mock_wb_cls.return_value.transform.return_value = workbook_path
    return workbook_path


@patch("handler.GoogleDrive")
@patch("handler.ContriBot")
@patch("handler.ContribotWorkbook")
@patch("handler.S3Storage")
@patch("handler.ListsRepository")
def test_handler_happy_path_xlsx_uses_list_id_report_name(
    mock_repo_cls,
    mock_s3_cls,
    mock_wb_cls,
    mock_bot_cls,
    mock_drive_cls,
    env,
    monkeypatch,
):
    _patch_error_codes(monkeypatch)

    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {
        "list_id": "42",
        "file_name": "list.xlsx",
    }
    mock_s3_cls.return_value.download.side_effect = _fake_download_bytes(b"xlsx")
    workbook_path = _stub_workbook(mock_wb_cls, "42")
    bot = _mock_bot_that_writes_report(mock_bot_cls, "42")
    mock_drive_cls.return_value.upload_file.return_value = (
        "https://drive.google.com/file/d/abc/view"
    )

    result = handler.handler({"list_id": "42"}, None)

    assert result == {
        "list_id": "42",
        "report_url": "https://drive.google.com/file/d/abc/view",
        "num_lines": 10,
        "num_errors": 2,
        "error_ratio": 0.2,
    }
    assert repo.update_list.call_args_list[0].args == ("42",)
    assert repo.update_list.call_args_list[0].kwargs == {
        "status": "PROCESSING",
    }
    assert repo.update_list.call_args_list[1].kwargs == {
        "report_url": "https://drive.google.com/file/d/abc/view",
        "num_lines": 10,
        "num_errors": 2,
        "error_ratio": 0.2,
    }
    assert mock_wb_cls.call_args.kwargs["list_id"] == "42"
    assert mock_wb_cls.call_args.kwargs["source_path"].name == "list.xlsx"
    mock_wb_cls.return_value.transform.assert_called_once_with()
    mock_bot_cls.assert_called_once()
    assert mock_bot_cls.call_args.args[0] == str(workbook_path)
    bot.process.assert_called_once_with()
    uploaded = mock_drive_cls.return_value.upload_file.call_args.args[0]
    assert Path(uploaded).name == "42.~PROCESSED.xlsx"


@patch("handler.GoogleDrive")
@patch("handler.ContriBot")
@patch("handler.ContribotWorkbook")
@patch("handler.S3Storage")
@patch("handler.ListsRepository")
def test_handler_happy_path_csv_passes_upload_to_workbook(
    mock_repo_cls,
    mock_s3_cls,
    mock_wb_cls,
    mock_bot_cls,
    mock_drive_cls,
    env,
    monkeypatch,
):
    _patch_error_codes(monkeypatch)

    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {
        "list_id": "101",
        "file_name": "Summer_2026_Suppliers_xYz1234.csv",
    }
    mock_s3_cls.return_value.download.side_effect = _fake_download_bytes(b"csv")
    workbook_path = _stub_workbook(mock_wb_cls, "101")
    _mock_bot_that_writes_report(mock_bot_cls, "101")
    mock_drive_cls.return_value.upload_file.return_value = (
        "https://drive.google.com/file/d/csv/view"
    )

    result = handler.handler({"list_id": "101"}, None)

    assert result["list_id"] == "101"
    assert mock_wb_cls.call_args.kwargs["list_id"] == "101"
    assert (
        mock_wb_cls.call_args.kwargs["source_path"].name
        == "Summer_2026_Suppliers_xYz1234.csv"
    )
    assert mock_bot_cls.call_args.args[0] == str(workbook_path)
    uploaded = mock_drive_cls.return_value.upload_file.call_args.args[0]
    assert Path(uploaded).name == "101.~PROCESSED.xlsx"


@patch("handler.ContribotWorkbook")
@patch("handler.S3Storage")
@patch("handler.ListsRepository")
def test_handler_raises_when_workbook_transform_fails(
    mock_repo_cls, mock_s3_cls, mock_wb_cls, env, monkeypatch
):
    _patch_error_codes(monkeypatch)
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {
        "list_id": "99",
        "file_name": "list.csv",
    }
    mock_s3_cls.return_value.download.side_effect = _fake_download_bytes(b"csv")
    mock_wb_cls.return_value.transform.side_effect = ValueError(
        "CSV file is empty: list.csv"
    )

    with pytest.raises(ValueError, match="CSV file is empty"):
        handler.handler({"list_id": "99"}, None)

    repo.update_list.assert_called_once_with("99", status="PROCESSING")


@patch("handler.ListsRepository")
def test_handler_raises_for_missing_row(mock_repo_cls, env):
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = None

    with pytest.raises(ValueError, match="No DynamoDB row"):
        handler.handler({"list_id": "99"}, None)


@patch("handler.ListsRepository")
def test_handler_raises_for_missing_file_name(mock_repo_cls, env):
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {"list_id": "99"}

    with pytest.raises(ValueError, match="missing file_name"):
        handler.handler({"list_id": "99"}, None)


@patch("handler.S3Storage")
@patch("handler.ListsRepository")
def test_handler_raises_when_s3_fails(mock_repo_cls, mock_s3_cls, env):
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {
        "list_id": "99",
        "file_name": "list.xlsx",
    }
    mock_s3_cls.return_value.download.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        handler.handler({"list_id": "99"}, None)

    repo.update_list.assert_called_once_with("99", status="PROCESSING")


def test_handler_requires_list_id(env):
    with pytest.raises(ValueError, match="list_id is required"):
        handler.handler({}, None)
