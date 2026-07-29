"""Unit tests for the ContriBot ``notify`` handler."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Allow ``from lib...`` imports when tests run locally.
CONTRIBOT_DIR = Path(__file__).resolve().parents[2]
if str(CONTRIBOT_DIR) not in sys.path:
    sys.path.insert(0, str(CONTRIBOT_DIR))

from lib.lists_repository import STATUS_FAILED, STATUS_PROCESSED  # noqa: E402

# Load the notify handler under a unique module name so it never collides
# with the ``fetch_lists`` handler when both suites run in one session.
_SPEC = importlib.util.spec_from_file_location(
    "notify_handler", CONTRIBOT_DIR / "notify" / "handler.py"
)
handler = importlib.util.module_from_spec(_SPEC)
sys.modules["notify_handler"] = handler
_SPEC.loader.exec_module(handler)


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("CONTRIBOT_STATE_TABLE_NAME", "contribot-state")
    monkeypatch.setenv("OS_HUB_API_URL", "https://example.com")
    monkeypatch.setenv(
        "SLACK_API_URL_SECRET_ARN",
        "arn:aws:secretsmanager:us-east-1:123:secret:slack",
    )
    monkeypatch.setenv(
        "SLACK_FAILURES_API_URL_SECRET_ARN",
        "arn:aws:secretsmanager:us-east-1:123:secret:slack-failures",
    )


LIST_ITEM = {
    "list_id": "101",
    "list_name": "Spring Facilities",
    "contributor_id": "5",
    "contributor_name": "Example Brand",
    "contributor_email": "brand@example.com",
    "file_name": "spring.xlsx",
}


def _mocks(list_item=LIST_ITEM):
    repo = MagicMock()
    repo.get_list.return_value = dict(list_item) if list_item else None
    slack = MagicMock()
    return repo, slack


@pytest.fixture
def repo_and_slack(env):
    repo, slack = _mocks()
    with patch.object(handler, "ListsRepository", return_value=repo), patch.object(
        handler, "SlackWebhook", return_value=slack
    ) as slack_cls:
        slack.cls = slack_cls
        yield repo, slack


def test_handler_posts_success_message(repo_and_slack):
    repo, slack = repo_and_slack

    result = handler.handler({"list_id": "101", "status": "processed"}, None)

    assert result == {"list_id": "101", "notified": True}
    slack.cls.assert_called_once_with(
        secret_arn="arn:aws:secretsmanager:us-east-1:123:secret:slack"
    )
    message = slack.post.call_args[0][0]
    assert "New list <https://example.com/lists/101|#101 Spring Facilities>" in message
    assert (
        "<https://example.com/admin/api/contributor/5/change/"
        "|Contributor Example Brand> email brand@example.com" in message
    )
    assert "File spring.xlsx" in message
    assert ":rotating_light:" not in message
    repo.finish_list.assert_called_once_with("101", status=STATUS_PROCESSED)


def test_handler_posts_failure_message(repo_and_slack):
    repo, slack = repo_and_slack

    event = {
        "list_id": "101",
        "error": {"Error": "States.TaskFailed", "Cause": "boom"},
    }
    result = handler.handler(event, None)

    assert result == {"list_id": "101", "notified": True}
    assert slack.post.call_count == 2
    assert [call.kwargs["secret_arn"] for call in slack.cls.call_args_list] == [
        "arn:aws:secretsmanager:us-east-1:123:secret:slack",
        "arn:aws:secretsmanager:us-east-1:123:secret:slack-failures",
    ]
    message = slack.post.call_args[0][0]
    assert ":rotating_light: ContriBot failed to process list" in message
    assert "Error: boom" in message
    repo.finish_list.assert_called_once_with("101", status=STATUS_FAILED)


def test_failure_skips_failures_channel_when_unconfigured(
    repo_and_slack, monkeypatch
):
    repo, slack = repo_and_slack
    monkeypatch.delenv("SLACK_FAILURES_API_URL_SECRET_ARN")

    event = {
        "list_id": "101",
        "error": {"Error": "States.TaskFailed", "Cause": "boom"},
    }
    result = handler.handler(event, None)

    assert result == {"list_id": "101", "notified": True}
    slack.post.assert_called_once()
    repo.finish_list.assert_called_once_with("101", status=STATUS_FAILED)


def test_success_does_not_post_to_failures_channel(repo_and_slack):
    repo, slack = repo_and_slack

    handler.handler({"list_id": "101"}, None)

    slack.post.assert_called_once()
    slack.cls.assert_called_once_with(
        secret_arn="arn:aws:secretsmanager:us-east-1:123:secret:slack"
    )


def test_handler_includes_report_stats_when_present(repo_and_slack):
    repo, slack = repo_and_slack

    event = {
        "list_id": "101",
        "num_lines": 200,
        "num_errors": 20,
        "error_ratio": 0.1,
        "report_url": "https://docs.google.com/spreadsheets/d/abc",
    }
    handler.handler(event, None)

    message = slack.post.call_args[0][0]
    assert "<https://docs.google.com/spreadsheets/d/abc|Checked report>" in message
    assert "(200/20) Error ratio: 10.0% :confused:" in message


@pytest.mark.parametrize(
    "error_ratio,emoji",
    [
        (0.01, ":simple_smile:"),
        (0.1, ":confused:"),
        (0.5, ":disappointed:"),
    ],
)
def test_error_ratio_emoji_thresholds(error_ratio, emoji):
    line = handler._error_ratio_line(
        {"num_lines": 100, "num_errors": 1, "error_ratio": error_ratio}
    )
    assert emoji in line


def test_handler_tolerates_missing_dynamodb_row(env):
    repo, slack = _mocks(list_item=None)
    with patch.object(handler, "ListsRepository", return_value=repo), patch.object(
        handler, "SlackWebhook", return_value=slack
    ):
        result = handler.handler({"list_id": "999"}, None)

    assert result == {"list_id": "999", "notified": True}
    message = slack.post.call_args[0][0]
    assert "New list <https://example.com/lists/999|#999>" in message
    repo.finish_list.assert_called_once_with("999", status=STATUS_PROCESSED)


def test_handler_survives_slack_failure(repo_and_slack):
    repo, slack = repo_and_slack
    slack.post.side_effect = RuntimeError("Slack webhook request failed")

    result = handler.handler({"list_id": "101"}, None)

    assert result == {"list_id": "101", "notified": False}
    repo.finish_list.assert_called_once_with("101", status=STATUS_PROCESSED)
