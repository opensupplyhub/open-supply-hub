"""Slack incoming-webhook client for ContriBot moderator notifications."""

from __future__ import annotations

import json
import os
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import boto3


class SlackWebhook:
    """Post messages to a Slack incoming webhook.

    The webhook URL is read from Secrets Manager (``SLACK_API_URL_SECRET_ARN``)
    unless passed directly.
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        secret_arn: Optional[str] = None,
        secrets_client: Optional[Any] = None,
    ):
        if webhook_url is not None:
            self._webhook_url = webhook_url
            return

        arn = secret_arn or os.environ["SLACK_API_URL_SECRET_ARN"]
        client = secrets_client or boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=arn)
        if "SecretString" not in response:
            raise RuntimeError(f"Secret {arn} has no SecretString")
        self._webhook_url = response["SecretString"].strip()

    def post(self, text: str) -> None:
        """Send ``text`` as a Slack message; raise RuntimeError on failure."""
        request = Request(
            self._webhook_url,
            data=json.dumps({"text": text}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                response.read()
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Slack webhook request failed ({exc.code}): {error_body}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Slack webhook request failed: {exc}") from exc
