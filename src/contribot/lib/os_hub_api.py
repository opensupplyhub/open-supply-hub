"""HTTP client for the Open Supply Hub admin facility lists API."""

from __future__ import annotations

import json
import os
import boto3
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


class OSHubAPI:
    """Fetch admin facility lists from the Open Supply Hub API."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        secret_arn: Optional[str] = None,
        secrets_client: Optional[Any] = None,
    ):
        self._api_url = api_url or os.environ["OS_HUB_API_URL"]
        self._secret_arn = secret_arn or os.environ["OS_HUB_API_TOKEN_SECRET_ARN"]
        self._secrets_client = secrets_client or boto3.client("secretsmanager")
        self._token = self._load_token()

    def _load_token(self) -> str:
        response = self._secrets_client.get_secret_value(SecretId=self._secret_arn)
        if "SecretString" in response:
            return response["SecretString"].strip()
        raise RuntimeError(f"Secret {self._secret_arn} has no SecretString")

    def fetch_lists(
        self,
        *,
        path: str = "/api/admin-facility-lists/",
        params: Optional[dict[str, Any]] = None,
        page_size: int = 50,
        max_results: int = 250,
    ) -> list[dict[str, Any]]:
        """Paginate a DRF list endpoint until empty or ``max_results``."""
        query = dict(params or {})
        query.setdefault("pageSize", page_size)
        results: list[dict[str, Any]] = []
        url: Optional[str] = self._build_url(path, query)

        while url and len(results) < max_results:
            payload = self._http_get_json(url, self._token)
            page = payload.get("results") or []
            remaining = max_results - len(results)
            results.extend(page[:remaining])
            if len(results) >= max_results:
                break
            next_url = payload.get("next")
            if not next_url:
                break
            # DRF may return an absolute URL; keep relative ones rooted on api_url.
            if next_url.startswith("http"):
                url = next_url
            else:
                url = urljoin(self._api_url.rstrip("/") + "/", next_url.lstrip("/"))

        return results

    def _build_url(self, path: str, params: dict[str, Any]) -> str:
        base = self._api_url.rstrip("/") + path
        return f"{base}?{urlencode(params)}"

    def _http_get_json(self, url: str, token: str) -> dict[str, Any]:
        request = Request(
            url,
            headers={
                "Authorization": f"Token {token}",
                "Accept": "application/json",
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"OS Hub API request failed ({exc.code}): {error_body}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"OS Hub API request failed: {exc}") from exc
        return json.loads(body)
