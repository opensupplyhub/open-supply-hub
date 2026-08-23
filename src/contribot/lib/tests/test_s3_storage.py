"""Unit tests for :mod:`s3_storage`."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from s3_storage import S3Storage


def test_download_writes_to_dest(tmp_path, monkeypatch):
    monkeypatch.setenv("AWS_STORAGE_BUCKET_NAME", "files-bucket")
    client = MagicMock()
    storage = S3Storage(s3_client=client)
    dest = tmp_path / "nested" / "file.xlsx"

    result = storage.download("list.xlsx", str(dest))

    assert result == str(dest)
    client.download_file.assert_called_once_with(
        "files-bucket",
        "list.xlsx",
        str(dest),
    )
    assert dest.parent.is_dir()


def test_download_requires_key(monkeypatch):
    monkeypatch.setenv("AWS_STORAGE_BUCKET_NAME", "files-bucket")
    storage = S3Storage(s3_client=MagicMock())
    with pytest.raises(ValueError, match="key is required"):
        storage.download("", "/tmp/out.xlsx")
