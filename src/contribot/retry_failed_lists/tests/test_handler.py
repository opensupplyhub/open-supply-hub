"""Unit tests for the ContriBot ``retry_failed_lists`` handler."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

CONTRIBOT_DIR = Path(__file__).resolve().parents[2]
RETRY_DIR = CONTRIBOT_DIR / "retry_failed_lists"
for path in (str(CONTRIBOT_DIR), str(RETRY_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

import handler  # noqa: E402


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("CONTRIBOT_STATE_TABLE_NAME", "contribot-state")
    monkeypatch.setenv(
        "CONTRIBOT_STATE_MACHINE_ARN",
        "arn:aws:states:us-east-1:123:stateMachine:contribot",
    )
    monkeypatch.setenv("CONTRIBOT_MAX_ATTEMPTS", "3")


@patch("handler.boto3.client")
@patch("handler.ListsRepository")
def test_handler_starts_execution_for_failed_lists(
    mock_repo_cls, mock_boto_client, env
):
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.scan.return_value = [
        {"list_id": "10", "status": "FAILED", "attempt_count": 0},
        {"list_id": "11", "status": "FAILED", "attempt_count": 1},
    ]
    sfn = MagicMock()
    mock_boto_client.return_value = sfn
    sfn.start_execution.return_value = {"executionArn": "arn:aws:states:exec:1"}

    result = handler.handler({}, None)

    repo.scan.assert_called_once_with(status="FAILED", max_attempts=3)
    assert repo.update_list.call_count == 2
    first = repo.update_list.call_args_list[0]
    assert first.args == ("10",)
    assert first.kwargs["status"] == "PENDING"
    assert first.kwargs["attempt_count"] == 1
    assert first.kwargs["finished_at"] == ""
    assert first.kwargs["started_at"]
    second = repo.update_list.call_args_list[1]
    assert second.args == ("11",)
    assert second.kwargs["attempt_count"] == 2
    mock_boto_client.assert_called_once_with("stepfunctions")
    sfn.start_execution.assert_called_once()
    kwargs = sfn.start_execution.call_args.kwargs
    assert kwargs["stateMachineArn"] == (
        "arn:aws:states:us-east-1:123:stateMachine:contribot"
    )
    assert json.loads(kwargs["input"]) == {
        "lists": [{"list_id": "10"}, {"list_id": "11"}],
    }
    assert result == {"executionArn": "arn:aws:states:exec:1"}


@patch("handler.boto3.client")
@patch("handler.ListsRepository")
def test_handler_does_not_start_execution_when_empty(
    mock_repo_cls, mock_boto_client, env
):
    repo = MagicMock()
    mock_repo_cls.return_value = repo
    repo.scan.return_value = []

    handler.handler({}, None)

    repo.update_list.assert_not_called()
    mock_boto_client.assert_not_called()
