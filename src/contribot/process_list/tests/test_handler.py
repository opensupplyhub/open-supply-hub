"""Unit tests for the ContriBot ``process_list`` handler."""

from __future__ import annotations

import json
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
        "cleaning": None,
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

    assert repo.update_list.call_args_list[0].kwargs == {"status": "PROCESSING"}
    assert repo.update_list.call_args_list[1].kwargs == {"status": "FAILED"}


@patch("handler.ListsRepository")
def test_handler_raises_for_missing_row(mock_repo_cls, env):
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = None

    with pytest.raises(ValueError, match="No DynamoDB row"):
        handler.handler({"list_id": "99"}, None)

    repo.update_list.assert_not_called()


@patch("handler.ListsRepository")
def test_handler_raises_for_missing_file_name(mock_repo_cls, env):
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {"list_id": "99"}

    with pytest.raises(ValueError, match="missing file_name"):
        handler.handler({"list_id": "99"}, None)

    repo.update_list.assert_called_once_with("99", status="FAILED")


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

    assert repo.update_list.call_args_list[0].kwargs == {"status": "PROCESSING"}
    assert repo.update_list.call_args_list[1].kwargs == {"status": "FAILED"}


@patch("handler.ListsRepository")
def test_handler_requires_list_id(mock_repo_cls, env):
    with pytest.raises(ValueError, match="list_id is required"):
        handler.handler({}, None)

    mock_repo_cls.return_value.update_list.assert_not_called()


# -- OSDEV-3398: report on the post-review list ----------------------------


@pytest.fixture
def api_env(env, monkeypatch):
    monkeypatch.setenv("OS_HUB_API_URL", "https://example.com")
    monkeypatch.setenv(
        "OS_HUB_API_TOKEN_SECRET_ARN",
        "arn:aws:secretsmanager:us-east-1:123:secret:token",
    )


def _cleaning_payload(status="COMPLETE", window_open=False):
    return {
        "enabled": True,
        "window_open": window_open,
        "run": {"id": 7, "status": status, "review_until": "2026-11-16T11:00:00Z"},
        "summary": {},
        "breakdown": {},
        "rows": [],
    }


def _fake_cleaned_download(dest_path):
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    Path(dest_path).write_text("country,name\nBD,Acme\n", encoding="utf-8")
    return Path(dest_path)


@patch("handler.OSHubAPI")
@patch("handler.GoogleDrive")
@patch("handler.ContriBot")
@patch("handler.ContribotWorkbook")
@patch("handler.S3Storage")
@patch("handler.ListsRepository")
def test_handler_reports_on_the_post_review_list(
    mock_repo_cls,
    mock_s3_cls,
    mock_wb_cls,
    mock_bot_cls,
    mock_drive_cls,
    mock_api_cls,
    api_env,
    monkeypatch,
):
    _patch_error_codes(monkeypatch)
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {"list_id": "42", "file_name": "list.xlsx"}
    api = MagicMock()
    mock_api_cls.return_value = api
    payload = _cleaning_payload()
    api.fetch_cleaning.return_value = payload
    api.download_cleaned_list.side_effect = (
        lambda list_id, dest: _fake_cleaned_download(dest)
    )
    _stub_workbook(mock_wb_cls, "42")
    bot = _mock_bot_that_writes_report(mock_bot_cls, "42")
    bot.save.side_effect = None
    cleaning_counts = {
        "must_fix_unresolved": 2,
        "corrections_rejected": 1,
        "rows_removed": 1,
        "outcome": "submitted",
    }

    def fake_save(targetfolder="./out"):
        out = Path(targetfolder) / bot.targetfilename
        out.write_bytes(b"report")
        return {
            "num_lines": 9,
            "num_errors": 1,
            "error_ratio": 0.1,
            "cleaning": cleaning_counts,
        }

    bot.save.side_effect = fake_save
    mock_drive_cls.return_value.upload_file.return_value = "https://drive/x"

    result = handler.handler({"list_id": "42"}, None)

    api.fetch_cleaning.assert_called_once_with("42")
    mock_s3_cls.return_value.download.assert_not_called()
    assert api.download_cleaned_list.call_args.args[0] == "42"
    assert mock_wb_cls.call_args.kwargs["source_path"].name == "42-cleaned.csv"
    bot.attach_cleaning.assert_called_once_with(payload)
    assert result["cleaning"] == cleaning_counts
    assert result["num_lines"] == 9


@patch("handler.OSHubAPI")
@patch("handler.ContribotWorkbook")
@patch("handler.S3Storage")
@patch("handler.ListsRepository")
def test_handler_fails_while_the_review_window_is_open(
    mock_repo_cls, mock_s3_cls, mock_wb_cls, mock_api_cls, api_env, monkeypatch
):
    _patch_error_codes(monkeypatch)
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {"list_id": "42", "file_name": "list.xlsx"}
    api = MagicMock()
    mock_api_cls.return_value = api
    api.fetch_cleaning.return_value = _cleaning_payload(window_open=True)

    with pytest.raises(handler.ListUnderReview, match="still being reviewed"):
        handler.handler({"list_id": "42"}, None)

    mock_s3_cls.return_value.download.assert_not_called()
    api.download_cleaned_list.assert_not_called()
    # left for retry_failed_lists, and the wait costs no attempt
    assert repo.update_list.call_args_list[-1].kwargs == {
        "status": "FAILED",
        "attempt_count": 0,
    }


def test_state_machine_leaves_a_list_under_review_without_notifying():
    """The Catch by error name is what keeps the wait off the failures
    channel: the name must match the exception class, and come before
    States.ALL."""
    definition = json.loads(
        (
            Path(__file__).resolve().parents[4]
            / "deployment"
            / "terraform"
            / "step-functions"
            / "contribot.json"
        ).read_text()
    )
    states = definition["States"]["ProcessLists"]["Iterator"]["States"]
    catches = states["ProcessList"]["Catch"]
    assert catches[0]["ErrorEquals"] == [handler.ListUnderReview.__name__]
    assert catches[0]["Next"] != "Notify"
    assert states[catches[0]["Next"]]["Type"] == "Pass"
    assert catches[-1]["ErrorEquals"] == ["States.ALL"]
    assert catches[-1]["Next"] == "Notify"


@pytest.mark.parametrize("payload", [
    {"enabled": True, "run": None, "summary": None, "rows": []},
    _cleaning_payload(status="FAILED"),
])
@patch("handler.OSHubAPI")
@patch("handler.GoogleDrive")
@patch("handler.ContriBot")
@patch("handler.ContribotWorkbook")
@patch("handler.S3Storage")
@patch("handler.ListsRepository")
def test_handler_reports_on_the_upload_without_a_completed_run(
    mock_repo_cls,
    mock_s3_cls,
    mock_wb_cls,
    mock_bot_cls,
    mock_drive_cls,
    mock_api_cls,
    payload,
    api_env,
    monkeypatch,
):
    _patch_error_codes(monkeypatch)
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {"list_id": "42", "file_name": "list.xlsx"}
    api = MagicMock()
    mock_api_cls.return_value = api
    api.fetch_cleaning.return_value = payload
    mock_s3_cls.return_value.download.side_effect = _fake_download_bytes(b"xlsx")
    _stub_workbook(mock_wb_cls, "42")
    bot = _mock_bot_that_writes_report(mock_bot_cls, "42")
    mock_drive_cls.return_value.upload_file.return_value = "https://drive/x"

    result = handler.handler({"list_id": "42"}, None)

    mock_s3_cls.return_value.download.assert_called_once()
    api.download_cleaned_list.assert_not_called()
    bot.attach_cleaning.assert_not_called()
    assert result["cleaning"] is None


@patch("handler.GoogleDrive")
@patch("handler.ContriBot")
@patch("handler.ContribotWorkbook")
@patch("handler.S3Storage")
@patch("handler.ListsRepository")
def test_handler_without_api_access_reports_on_the_upload(
    mock_repo_cls, mock_s3_cls, mock_wb_cls, mock_bot_cls, mock_drive_cls, env, monkeypatch
):
    _patch_error_codes(monkeypatch)
    monkeypatch.delenv("OS_HUB_API_URL", raising=False)
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {"list_id": "42", "file_name": "list.xlsx"}
    mock_s3_cls.return_value.download.side_effect = _fake_download_bytes(b"xlsx")
    _stub_workbook(mock_wb_cls, "42")
    bot = _mock_bot_that_writes_report(mock_bot_cls, "42")
    mock_drive_cls.return_value.upload_file.return_value = "https://drive/x"

    result = handler.handler({"list_id": "42"}, None)

    mock_s3_cls.return_value.download.assert_called_once()
    bot.attach_cleaning.assert_not_called()
    assert result["cleaning"] is None
