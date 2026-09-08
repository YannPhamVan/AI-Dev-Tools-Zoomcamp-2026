"""Shared FastAPI dependency: extract and validate the bearer token."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.store import store

_bearer = HTTPBearer(auto_error=False)


def get_current_username(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """Return the username associated with the bearer token, or raise 401."""
    token: str | None = None

    if creds and creds.scheme.lower() == "bearer":
        token = creds.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Not authenticated"},
        )

    username = store.get_username_for_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"},
        )

    return username
