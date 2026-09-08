"""Scores router: POST /api/scores"""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.dependencies import get_current_username
from backend.models import ErrorResponse, Player, SubmitScoreRequest, SubmitScoreResponse
from backend.store import store

router = APIRouter(prefix="/api/scores", tags=["Scores"])


def _to_player(record) -> Player:
    return Player(username=record.username, highScore=record.high_score)


@router.post(
    "",
    response_model=SubmitScoreResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
)
def submit_score(body: SubmitScoreRequest, username: str = Depends(get_current_username)):
    if body.score < 0:
        raise HTTPException(status_code=400, detail={"error": "Score must be non-negative."})

    record, is_new_high = store.update_high_score(username, body.score)
    return SubmitScoreResponse(player=_to_player(record), isNewHighScore=is_new_high)
