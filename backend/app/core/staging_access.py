"""Explicit access mode; authentication and usage limits remain independent."""
from fastapi import HTTPException
from app.core.config import settings


def require_staging_tester(email: str) -> None:
    if (settings.staging_enabled and settings.staging_access_mode == "invite_only"
        and email.strip().lower() not in settings.staging_allowed_emails):
        raise HTTPException(403, "Private staging access is restricted.")


def require_registration(email: str) -> None:
    if settings.staging_enabled:
        require_staging_tester(email)
        if not settings.staging_registration_enabled:
            raise HTTPException(403, "Registration is temporarily closed.")
