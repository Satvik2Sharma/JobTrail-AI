from abc import ABC, abstractmethod
from typing import Optional

class BaseStorageService(ABC):
    """
    Abstract Base Class for file storage services in JobTrail-AI.
    Provides clean abstraction across cloud object storage (e.g. Supabase Storage)
    and local filesystem storage.
    """

    @abstractmethod
    def upload_file(
        self,
        file_bytes: bytes,
        storage_path: str,
        content_type: str = "application/pdf"
    ) -> str:
        """
        Uploads file bytes to storage at the given relative storage_path.
        Returns the resolved storage path or identifier.
        """
        pass

    @abstractmethod
    def download_file(self, storage_path: str) -> bytes:
        """
        Downloads and returns the binary content of the file.
        """
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """
        Deletes the file at storage_path.
        Returns True if deleted, False if not found.
        """
        pass

    @abstractmethod
    def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Generates a secure access URL (or signed temporary URL for private cloud buckets).
        """
        pass

    @abstractmethod
    def file_exists(self, storage_path: str) -> bool:
        """
        Checks if a file exists at the given storage_path.
        """
        pass
