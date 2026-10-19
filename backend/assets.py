"""Private artifact storage with authenticated API delivery."""

from pathlib import Path
from urllib.parse import urlparse

from vercel.blob import get_blob, put_blob

from .settings import Settings


class Assets:
    """Store identical lesson/video bytes locally or in Vercel's private Blob store."""

    def __init__(self, settings: Settings) -> None:
        """Bind storage; production must not pretend ephemeral files are durable."""
        self.settings = settings
        self.root = settings.data_dir / "assets"
        self.root.mkdir(parents=True, exist_ok=True)

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        """Return an internal asset key, never a credential-bearing URL."""
        self._validate_key(key)
        if self.settings.blob_token:
            result = await put_blob(
                key, data, access="private", content_type=content_type, allow_overwrite=True
            )
            return result.url
        if self.settings.production:
            raise RuntimeError("Durable artifact storage has not been configured")
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    async def read(self, location: str) -> bytes:
        """Read server-selected locations only; never accept arbitrary user URLs."""
        if location.startswith("https://"):
            host = urlparse(location).hostname or ""
            if not host.endswith(".private.blob.vercel-storage.com"):
                raise ValueError("Unexpected artifact host")
            response = await get_blob(location, access="private")
            return response.body
        self._validate_key(location)
        return (self.root / location).read_bytes()

    @staticmethod
    def _validate_key(key: str) -> None:
        if not key or key.startswith("/") or ".." in Path(key).parts or "\\" in key:
            raise ValueError("Invalid asset key")
