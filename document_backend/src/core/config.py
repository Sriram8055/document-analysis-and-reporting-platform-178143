"""
Configuration module for the backend service.

Reads environment variables with sensible defaults and ensures the storage
directory exists at import time. Provides a singleton accessor for use
across routes and background workers.

Environment variables:
- ALLOWED_ORIGINS: CSV of allowed CORS origins. Default: *
- MAX_UPLOAD_MB: Maximum upload size in MB (int). Default: 25
- STORAGE_DIR: Base directory for file storage. Default: ./storage
- GEMINI_API_KEY: API key for Gemini (if used)
- GEMINI_MODEL: Model name for Gemini. Default: gemini-2.5-flash
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


def _parse_allowed_origins(raw: str | None) -> List[str]:
    if not raw:
        return ["*"]
    parts = [p.strip() for p in raw.split(",")]
    # filter empties while keeping '*' if present
    return [p for p in parts if p]


@dataclass(frozen=True)
class Settings:
    """Immutable settings loaded from environment variables."""
    allowed_origins: List[str] = field(default_factory=lambda: _parse_allowed_origins(os.getenv("ALLOWED_ORIGINS")))
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "25"))
    storage_dir: str = os.getenv("STORAGE_DIR", "./storage")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# Ensure storage directory exists on import
def _ensure_storage(storage_dir: str) -> None:
    try:
        os.makedirs(storage_dir, exist_ok=True)
    except Exception as exc:
        # Do not raise at import time to avoid breaking the app; instead, log via print.
        # Actual apps can integrate a logger here.
        print(f"[config] Warning: failed to ensure storage dir '{storage_dir}': {exc}")


# Initialize singleton settings at import
_settings_singleton = Settings()
_ensure_storage(_settings_singleton.storage_dir)


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return the singleton settings instance for the application."""
    return _settings_singleton
