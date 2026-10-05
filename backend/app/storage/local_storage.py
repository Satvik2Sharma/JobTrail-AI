import os
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.storage.base import BaseStorageService

class LocalStorageService(BaseStorageService):
    """
    Local filesystem storage provider for offline development and testing.
    Mirrors the cloud object hierarchy safely under the local UPLOAD_DIR.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_absolute_path(self, storage_path: str) -> Path:
        # Sanitize path to prevent path traversal attacks
        clean_path = storage_path.lstrip("/\\")
        target_path = (self.base_dir / clean_path).resolve()
        if not str(target_path).startswith(str(self.base_dir)):
            raise ValueError("Path traversal attempt detected in storage_path.")
        return target_path

    def upload_file(
        self,
        file_bytes: bytes,
        storage_path: str,
        content_type: str = "application/pdf"
    ) -> str:
        target_path = self._get_absolute_path(storage_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(file_bytes)
        return storage_path

    def download_file(self, storage_path: str) -> bytes:
        target_path = self._get_absolute_path(storage_path)
        if not target_path.exists() or not target_path.is_file():
            raise FileNotFoundError(f"File not found in storage: {storage_path}")
        with open(target_path, "rb") as f:
            return f.read()

    def delete_file(self, storage_path: str) -> bool:
        target_path = self._get_absolute_path(storage_path)
        if target_path.exists() and target_path.is_file():
            target_path.unlink()
            return True
        return False

    def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        # Local representation URL
        return f"/api/resume/download/{storage_path.lstrip('/')}"

    def file_exists(self, storage_path: str) -> bool:
        target_path = self._get_absolute_path(storage_path)
        return target_path.exists() and target_path.is_file()
