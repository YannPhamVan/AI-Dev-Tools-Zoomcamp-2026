"""Password hashing and bearer-token helpers.

Uses the `bcrypt` library directly (passlib is not compatible with bcrypt >= 4.x).
"""

import secrets

import bcrypt


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def generate_token() -> str:
    """Return a cryptographically-secure random bearer token (hex, 64 chars)."""
    return secrets.token_hex(32)
