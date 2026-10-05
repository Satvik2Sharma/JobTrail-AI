import logging
from typing import Optional
import httpx
from app.core.config import settings
from app.storage.base import BaseStorageService

logger = logging.getLogger(__name__)

class SupabaseStorageService(BaseStorageService):
    """
    Production file storage service integrating directly with Supabase Storage REST API.
    Maintains a private bucket for candidate resume documents and manages signed download URLs.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        service_role_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
    ):
        self.supabase_url = (supabase_url or settings.SUPABASE_URL or "").rstrip("/")
        self.service_role_key = service_role_key or settings.SUPABASE_SERVICE_ROLE_KEY or ""
        self.bucket = bucket_name or settings.SUPABASE_STORAGE_BUCKET or "resume-files"

        if not self.supabase_url or not self.service_role_key:
            logger.warning(
                "Supabase credentials incomplete. SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing."
            )

        self.storage_base_url = f"{self.supabase_url}/storage/v1"
        self._bucket_checked = False

    def _get_headers(self, content_type: Optional[str] = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def ensure_bucket_exists(self):
        """Ensures the private resume-files bucket exists in Supabase."""
        if self._bucket_checked or not self.supabase_url or not self.service_role_key:
            return

        try:
            with httpx.Client(timeout=10.0) as client:
                # Check if bucket exists
                resp = client.get(
                    f"{self.storage_base_url}/bucket/{self.bucket}",
                    headers=self._get_headers(),
                )
                if resp.status_code == 200:
                    self._bucket_checked = True
                    return

                if resp.status_code == 404:
                    # Create private bucket
                    create_resp = client.post(
                        f"{self.storage_base_url}/bucket",
                        headers=self._get_headers("application/json"),
                        json={"id": self.bucket, "name": self.bucket, "public": False},
                    )
                    if create_resp.status_code in (200, 201):
                        logger.info(f"Created private Supabase Storage bucket: {self.bucket}")
                        self._bucket_checked = True
                    else:
                        logger.warning(
                            f"Could not create Supabase bucket {self.bucket}: {create_resp.status_code} {create_resp.text}"
                        )
        except Exception as e:
            logger.warning(f"Error checking Supabase bucket {self.bucket}: {e}")

    def upload_file(
        self,
        file_bytes: bytes,
        storage_path: str,
        content_type: str = "application/pdf"
    ) -> str:
        clean_path = storage_path.lstrip("/")
        self.ensure_bucket_exists()

        headers = self._get_headers(content_type)
        headers["x-upsert"] = "true"

        url = f"{self.storage_base_url}/object/{self.bucket}/{clean_path}"
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, headers=headers, content=file_bytes)
                if resp.status_code not in (200, 201):
                    raise RuntimeError(
                        f"Supabase Storage upload failed ({resp.status_code}): {resp.text}"
                    )
            return clean_path
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error while uploading to Supabase Storage: {str(e)}")

    def download_file(self, storage_path: str) -> bytes:
        clean_path = storage_path.lstrip("/")
        url = f"{self.storage_base_url}/object/{self.bucket}/{clean_path}"
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(url, headers=self._get_headers())
                if resp.status_code == 404:
                    raise FileNotFoundError(f"File not found in Supabase Storage: {clean_path}")
                if resp.status_code != 200:
                    raise RuntimeError(
                        f"Supabase Storage download failed ({resp.status_code}): {resp.text}"
                    )
                return resp.content
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error while downloading from Supabase Storage: {str(e)}")

    def delete_file(self, storage_path: str) -> bool:
        clean_path = storage_path.lstrip("/")
        url = f"{self.storage_base_url}/object/{self.bucket}/{clean_path}"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.delete(url, headers=self._get_headers())
                return resp.status_code in (200, 204)
        except Exception as e:
            logger.warning(f"Failed to delete file from Supabase Storage: {e}")
            return False

    def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Creates a signed URL for private bucket access that expires after `expires_in` seconds.
        """
        clean_path = storage_path.lstrip("/")
        url = f"{self.storage_base_url}/object/sign/{self.bucket}/{clean_path}"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    url,
                    headers=self._get_headers("application/json"),
                    json={"expiresIn": expires_in}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    signed_url = data.get("signedURL")
                    if signed_url:
                        # Full URL
                        return f"{self.supabase_url}/storage/v1{signed_url}"
                logger.warning(f"Could not generate signed URL: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.warning(f"Exception generating signed URL: {e}")

        # Fallback to direct authenticated API route
        return f"/api/resume/download/{clean_path}"

    def file_exists(self, storage_path: str) -> bool:
        clean_path = storage_path.lstrip("/")
        url = f"{self.storage_base_url}/object/info/{self.bucket}/{clean_path}"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url, headers=self._get_headers())
                return resp.status_code == 200
        except Exception:
            return False
