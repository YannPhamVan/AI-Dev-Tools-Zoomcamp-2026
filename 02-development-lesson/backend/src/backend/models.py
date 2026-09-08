"""Pydantic models matching the openapi.yaml spec."""

from pydantic import BaseModel, Field


# ── Request bodies ────────────────────────────────────────────────────────────

class SignUpRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=4, max_length=64)


class SignInRequest(BaseModel):
    username: str
    password: str


class SubmitScoreRequest(BaseModel):
    score: int = Field(..., ge=0)


# ── Response bodies ───────────────────────────────────────────────────────────

class Player(BaseModel):
    username: str
    highScore: int


class AuthResponse(BaseModel):
    player: Player
    token: str


class PlayerResponse(BaseModel):
    player: Player


class SubmitScoreResponse(BaseModel):
    player: Player
    isNewHighScore: bool


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    score: int


class ErrorResponse(BaseModel):
    error: str
