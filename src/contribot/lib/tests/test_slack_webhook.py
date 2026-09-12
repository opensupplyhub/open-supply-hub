"""Unit tests for the ContriBot Slack webhook client."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

CONTRIBOT_DIR = Path(__file__).resolve().parents[2]
if str(CONTRIBOT_DIR) not in sys.path:
    sys.path.insert(0, str(CONTRIBOT_DIR))

from lib.slack_webhook import SlackWebhook  # noqa: E402


def test_loads_webhook_url_from_secrets_manager(monkeypatch):
    monkeypatch.setenv(
        "SLACK_API_URL_SECRET_ARN",
        "arn:aws:secretsmanager:us-east-1:123:secret:slack",
    )
    client = MagicMock()
    client.get_secret_value.return_value = {
        "SecretString": " https://hooks.slack.com/services/T/B/X \n"
    }

    webhook = SlackWebhook(secrets_client=client)

    assert webhook._webhook_url == "https://hooks.slack.com/services/T/B/X"
    client.get_secret_value.assert_called_once_with(
        SecretId="arn:aws:secretsmanager:us-east-1:123:secret:slack"
    )


def test_raises_when_secret_has_no_string():
    client = MagicMock()
    client.get_secret_value.return_value = {}

    with pytest.raises(RuntimeError, match="has no SecretString"):
        SlackWebhook(secret_arn="arn:example", secrets_client=client)


def test_post_sends_json_payload(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"ok"

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("lib.slack_webhook.urlopen", fake_urlopen)

    webhook = SlackWebhook(webhook_url="https://hooks.slack.com/services/T/B/X")
    webhook.post("hello moderators")

    request = captured["request"]
    assert request.full_url == "https://hooks.slack.com/services/T/B/X"
    assert json.loads(request.data.decode("utf-8")) == {"text": "hello moderators"}
    assert request.get_header("Content-type") == "application/json"


def test_post_wraps_url_errors(monkeypatch):
    from urllib.error import URLError

    def fake_urlopen(request, timeout):
        raise URLError("connection refused")

    monkeypatch.setattr("lib.slack_webhook.urlopen", fake_urlopen)

    webhook = SlackWebhook(webhook_url="https://hooks.slack.com/services/T/B/X")
    with pytest.raises(RuntimeError, match="Slack webhook request failed"):
        webhook.post("hello")
