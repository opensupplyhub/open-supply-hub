"""Unit tests for the ContriBot ``process_list`` handler."""

from __future__ import annotations

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


@patch("handler.GoogleDrive")
@patch("handler.ContriBot")
@patch("handler.S3Storage")
@patch("handler.ListsRepository")
def test_handler_happy_path(
    mock_repo_cls,
    mock_s3_cls,
    mock_bot_cls,
    mock_drive_cls,
    env,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(handler, "_error_codes_path", lambda: str(tmp_path / "cfg.xlsx"))
    (tmp_path / "cfg.xlsx").write_bytes(b"cfg")

    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {
        "list_id": "42",
        "file_name": "list.xlsx",
    }

    def fake_download(key, dest_path):
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        Path(dest_path).write_bytes(b"xlsx")
        return dest_path

    mock_s3_cls.return_value.download.side_effect = fake_download

    bot = MagicMock()
    bot.targetfilename = "list.~PROCESSED.xlsx"
    bot.save.return_value = {
        "num_lines": 10,
        "num_errors": 2,
        "error_ratio": 0.2,
    }
    mock_bot_cls.return_value = bot

    def fake_save(targetfolder="./out"):
        out = Path(targetfolder) / bot.targetfilename
        out.write_bytes(b"report")
        return bot.save.return_value

    bot.save.side_effect = fake_save
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
    mock_bot_cls.assert_called_once()
    bot.process.assert_called_once_with()
    mock_drive_cls.return_value.upload_file.assert_called_once()


@patch("handler.ListsRepository")
def test_handler_raises_for_missing_row(mock_repo_cls, env):
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = None

    with pytest.raises(ValueError, match="No DynamoDB row"):
        handler.handler({"list_id": "99"}, None)


@patch("handler.ListsRepository")
def test_handler_raises_for_non_xlsx(mock_repo_cls, env):
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.get_list.return_value = {
        "list_id": "99",
        "file_name": "list.csv",
    }

    with pytest.raises(ValueError, match="requires an .xlsx"):
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
