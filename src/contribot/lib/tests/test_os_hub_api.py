"""Unit tests for :class:`os_hub_api.OSHubAPI`."""
from __future__ import annotations

from io import BytesIO
from unittest.mock import MagicMock

import pytest
from urllib.error import HTTPError

from os_hub_api import OSHubAPI

TEST_SECRET_ARN = "arn:aws:secretsmanager:us-east-1:123:secret:token"


def test_constructor_loads_token_from_secret():
    secrets = MagicMock()
    secrets.get_secret_value.return_value = {"SecretString": " secret-token \n"}
    api = OSHubAPI(
        api_url="https://example.com",
        secret_arn="arn:aws:secretsmanager:us-east-1:123:secret:token",
        secrets_client=secrets,
    )
    assert api._token == "secret-token"
    secrets.get_secret_value.assert_called_once_with(
        SecretId="arn:aws:secretsmanager:us-east-1:123:secret:token"
    )


def test_fetch_lists_paginates_until_empty(monkeypatch):
    pages = [
        {
            "results": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
            "next": "https://example.com/api/admin-facility-lists/?page=2",
        },
        {
            "results": [{"id": 3, "name": "C"}],
            "next": None,
        },
    ]
    calls = []

    def fake_get(url, token):
        calls.append((url, token))
        return pages[len(calls) - 1]

    secrets = MagicMock()
    secrets.get_secret_value.return_value = {"SecretString": "tok"}
    api = OSHubAPI(
        api_url="https://example.com",
        secret_arn=TEST_SECRET_ARN,
        secrets_client=secrets,
    )
    monkeypatch.setattr(api, "_http_get_json", fake_get)
    results = api.fetch_lists(
        params={"id__gt": 0, "ordering": "id"},
        page_size=2,
    )
    assert [item["id"] for item in results] == [1, 2, 3]
    assert "id__gt=0" in calls[0][0]
    assert "ordering=id" in calls[0][0]
    assert calls[0][1] == "tok"
    assert calls[1][0].endswith("page=2")


def test_fetch_lists_respects_max_results(monkeypatch):
    def fake_get(url, token):
        return {
            "results": [{"id": i, "name": f"L{i}"} for i in range(1, 6)],
            "next": "https://example.com/next",
        }

    secrets = MagicMock()
    secrets.get_secret_value.return_value = {"SecretString": "tok"}
    api = OSHubAPI(
        api_url="https://example.com",
        secret_arn=TEST_SECRET_ARN,
        secrets_client=secrets,
    )
    monkeypatch.setattr(api, "_http_get_json", fake_get)
    results = api.fetch_lists(
        params={"id__gt": 0, "ordering": "id"},
        max_results=3,
    )
    assert [item["id"] for item in results] == [1, 2, 3]


def test_http_get_json_raises_on_http_error(monkeypatch):
    error = HTTPError(
        url="https://example.com/api/admin-facility-lists/",
        code=401,
        msg="Unauthorized",
        hdrs=None,
        fp=BytesIO(b'{"detail":"auth"}'),
    )

    class FakeOpener:
        def __enter__(self):
            raise error

        def __exit__(self, *args):
            return False

    secrets = MagicMock()
    secrets.get_secret_value.return_value = {"SecretString": "bad"}
    api = OSHubAPI(
        api_url="https://example.com",
        secret_arn=TEST_SECRET_ARN,
        secrets_client=secrets,
    )
    monkeypatch.setattr("os_hub_api.urlopen", lambda *a, **k: FakeOpener())
    with pytest.raises(RuntimeError, match="401"):
        api._http_get_json("https://example.com/api/admin-facility-lists/", "bad")
