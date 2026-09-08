"""Auth router: /api/auth/signup, /api/auth/signin, /api/auth/signout, /api/auth/me"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.auth import generate_token, hash_password, verify_password
from backend.dependencies import get_current_username
from backend.models import AuthResponse, ErrorResponse, Player, PlayerResponse, SignInRequest, SignUpRequest
from backend.store import store

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _to_player(record) -> Player:
    return Player(username=record.username, highScore=record.high_score)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def sign_up(body: SignUpRequest):
    username = body.username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail={"error": "Le pseudo doit faire au moins 3 caractères."})
    if len(body.password) < 4:
        raise HTTPException(status_code=400, detail={"error": "Le mot de passe doit faire au moins 4 caractères."})
    if store.username_exists(username):
        raise HTTPException(status_code=409, detail={"error": "Ce pseudo est déjà utilisé."})

    record = store.create_player(username, hash_password(body.password))
    token = generate_token()
    store.save_token(token, record.username)
    return AuthResponse(player=_to_player(record), token=token)


@router.post(
    "/signin",
    response_model=AuthResponse,
    responses={401: {"model": ErrorResponse}},
)
def sign_in(body: SignInRequest):
    record = store.get_player(body.username.strip())
    if not record or not verify_password(body.password, record.hashed_password):
        raise HTTPException(status_code=401, detail={"error": "Identifiants invalides."})

    token = generate_token()
    store.save_token(token, record.username)
    return AuthResponse(player=_to_player(record), token=token)


@router.post(
    "/signout",
    responses={401: {"model": ErrorResponse}},
)
def sign_out(request: Request, username: str = Depends(get_current_username)):
    # Extract raw token to revoke it
    auth_header = request.headers.get("authorization", "")
    token = auth_header.removeprefix("Bearer ").removeprefix("bearer ").strip()
    store.revoke_token(token)
    return {"message": "Déconnexion réussie."}


@router.get(
    "/me",
    response_model=PlayerResponse,
    responses={401: {"model": ErrorResponse}},
)
def current_player(username: str = Depends(get_current_username)):
    record = store.get_player(username)
    if not record:
        raise HTTPException(status_code=401, detail={"error": "Player not found."})
    return PlayerResponse(player=_to_player(record))
