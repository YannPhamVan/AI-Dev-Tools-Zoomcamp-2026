"""In-memory data store with seed data matching the openapi.yaml example leaderboard."""

import threading
from dataclasses import dataclass, field


@dataclass
class PlayerRecord:
    username: str
    hashed_password: str
    high_score: int = 0


class Store:
    """Thread-safe in-memory store for players and active tokens."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # username (lowercase) -> PlayerRecord
        self._players: dict[str, PlayerRecord] = {}
        # token -> username
        self._tokens: dict[str, str] = {}

    # ── Players ───────────────────────────────────────────────────────────────

    def get_player(self, username: str) -> PlayerRecord | None:
        with self._lock:
            return self._players.get(username.lower())

    def username_exists(self, username: str) -> bool:
        with self._lock:
            return username.lower() in self._players

    def create_player(self, username: str, hashed_password: str) -> PlayerRecord:
        record = PlayerRecord(username=username, hashed_password=hashed_password)
        with self._lock:
            self._players[username.lower()] = record
        return record

    def update_high_score(self, username: str, score: int) -> tuple[PlayerRecord, bool]:
        """Returns (updated_record, is_new_high_score)."""
        with self._lock:
            record = self._players[username.lower()]
            if score > record.high_score:
                record.high_score = score
                return record, True
            return record, False

    def leaderboard(self, limit: int = 10) -> list[PlayerRecord]:
        with self._lock:
            sorted_players = sorted(
                self._players.values(), key=lambda p: p.high_score, reverse=True
            )
            return sorted_players[:limit]

    # ── Tokens ────────────────────────────────────────────────────────────────

    def save_token(self, token: str, username: str) -> None:
        with self._lock:
            self._tokens[token] = username

    def revoke_token(self, token: str) -> None:
        with self._lock:
            self._tokens.pop(token, None)

    def get_username_for_token(self, token: str) -> str | None:
        with self._lock:
            return self._tokens.get(token)


def _make_store() -> Store:
    """Build the singleton store and seed it with demo data."""
    from backend.auth import hash_password  # local import to avoid circular

    store = Store()
    seed_data = [
        ("cobra_kai", 87),
        ("viper", 74),
        ("mamba", 66),
        ("python42", 58),
        ("slither", 51),
        ("anaconda", 44),
        ("boa", 37),
        ("adder", 29),
        ("rattler", 22),
        ("garter", 15),
        ("newbie", 8),
    ]
    for username, score in seed_data:
        record = store.create_player(username, hash_password("demo1234"))
        record.high_score = score

    return store


# Module-level singleton
store: Store = _make_store()
