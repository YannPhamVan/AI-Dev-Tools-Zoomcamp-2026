"""Leaderboard router: GET /api/leaderboard"""

from fastapi import APIRouter

from backend.models import LeaderboardEntry
from backend.store import store

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=list[LeaderboardEntry])
def leaderboard():
    entries = store.leaderboard(limit=10)
    return [
        LeaderboardEntry(rank=i + 1, username=p.username, score=p.high_score)
        for i, p in enumerate(entries)
    ]
