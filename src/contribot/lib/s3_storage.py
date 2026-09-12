"""S3 helpers for downloading facility-list uploads."""

from __future__ import annotations

import os
from typing import Any, Optional

import boto3


class S3Storage:
    """Download objects from the facility-list files bucket."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        s3_client: Optional[Any] = None,
    ):
        self._bucket = bucket_name or os.environ["AWS_STORAGE_BUCKET_NAME"]
        self._client = s3_client or boto3.client("s3")

    def download(self, key: str, dest_path: str) -> str:
        """Download ``key`` from the configured bucket to ``dest_path``.

        Returns ``dest_path``.
        """
        if not key:
            raise ValueError("S3 object key is required")
        parent = os.path.dirname(dest_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._client.download_file(self._bucket, key, dest_path)
        return dest_path
