"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.store import Store, store as global_store
from backend.auth import hash_password


@pytest.fixture()
def fresh_store(monkeypatch):
    """Replace the global store with a clean, seeded one for each test."""
    s = Store()
    seed = [
        ("cobra_kai", 87),
        ("viper", 74),
        ("mamba", 66),
    ]
    for username, score in seed:
        record = s.create_player(username, hash_password("demo1234"))
        record.high_score = score

    # Patch the store reference in every module that imports it
    import backend.store as store_module
    import backend.routers.auth as auth_router
    import backend.routers.scores as scores_router
    import backend.routers.leaderboard as lb_router
    import backend.dependencies as deps

    monkeypatch.setattr(store_module, "store", s)
    monkeypatch.setattr(auth_router, "store", s)
    monkeypatch.setattr(scores_router, "store", s)
    monkeypatch.setattr(lb_router, "store", s)
    monkeypatch.setattr(deps, "store", s)
    return s


@pytest.fixture()
def client(fresh_store):
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture()
def auth_client(client, fresh_store):
    """A client already signed in as a fresh test user; returns (client, token)."""
    r = client.post("/api/auth/signup", json={"username": "tester", "password": "pass1"})
    assert r.status_code == 201
    token = r.json()["token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client, token
