from app.core.config import settings
from app.storage.base import BaseStorageService
from app.storage.local_storage import LocalStorageService
from app.storage.supabase_storage import SupabaseStorageService

_storage_instance: BaseStorageService = None

def get_storage_service() -> BaseStorageService:
    """
    Factory function returning the configured storage service:
    Supabase Storage when credentials are provided in production,
    or LocalStorageService for local development and unit tests.
    """
    global _storage_instance
    if _storage_instance is None:
        if settings.is_supabase_storage_enabled:
            _storage_instance = SupabaseStorageService()
        else:
            _storage_instance = LocalStorageService()
    return _storage_instance

def reset_storage_service():
    """Reset the singleton instance (useful for testing)."""
    global _storage_instance
    _storage_instance = None
