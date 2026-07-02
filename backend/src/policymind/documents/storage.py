"""Object storage — local filesystem and S3/MinIO implementations."""

from pathlib import Path
from typing import Any, Protocol


class ObjectStorage(Protocol):
    """Protocol for object storage adapters."""

    async def put(self, key: str, content: bytes, content_type: str) -> None: ...
    async def get(self, key: str) -> bytes: ...
    async def delete(self, key: str) -> None: ...


class LocalObjectStorage:
    """Stores objects on the local filesystem (dev and unit tests)."""

    def __init__(self, base_dir: str | Path = "./storage") -> None:
        self._base = Path(base_dir)

    async def put(self, key: str, content: bytes, content_type: str = "application/octet-stream") -> None:
        target = self._base / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    async def get(self, key: str) -> bytes:
        target = self._base / key
        if not target.is_file():
            raise FileNotFoundError(f"Object not found: {key}")
        return target.read_bytes()

    async def delete(self, key: str) -> None:
        target = self._base / key
        if target.is_file():
            target.unlink()


class S3ObjectStorage:
    """MinIO / S3-compatible object storage.

    Uses boto3. Requires S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET env vars.
    """

    def __init__(
        self,
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        bucket: str = "policymind",
        secure: bool = False,
    ) -> None:
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket
        self._secure = secure
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import boto3  # type: ignore[import-not-found]
                self._client = boto3.client(
                    "s3",
                    endpoint_url=f"{'https' if self._secure else 'http'}://{self._endpoint}",
                    aws_access_key_id=self._access_key,
                    aws_secret_access_key=self._secret_key,
                )
            except ImportError as exc:
                raise RuntimeError("boto3 required; install with: pip install boto3") from exc
        return self._client

    async def put(self, key: str, content: bytes, content_type: str = "application/octet-stream") -> None:
        self._get_client().put_object(Bucket=self._bucket, Key=key, Body=content, ContentType=content_type)

    async def get(self, key: str) -> bytes:
        resp = self._get_client().get_object(Bucket=self._bucket, Key=key)
        return resp["Body"].read()  # type: ignore[no-any-return]

    async def delete(self, key: str) -> None:
        self._get_client().delete_object(Bucket=self._bucket, Key=key)
