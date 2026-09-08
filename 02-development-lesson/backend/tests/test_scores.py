"""Tests for POST /api/scores."""

import pytest


class TestSubmitScore:
    def test_submit_score_new_high(self, auth_client):
        client, _ = auth_client
        r = client.post("/api/scores", json={"score": 42})
        assert r.status_code == 200
        data = r.json()
        assert data["player"]["highScore"] == 42
        assert data["isNewHighScore"] is True

    def test_submit_score_not_new_high(self, auth_client):
        client, _ = auth_client
        client.post("/api/scores", json={"score": 50})
        r = client.post("/api/scores", json={"score": 30})
        assert r.status_code == 200
        data = r.json()
        assert data["player"]["highScore"] == 50
        assert data["isNewHighScore"] is False

    def test_submit_score_updates_high(self, auth_client):
        client, _ = auth_client
        client.post("/api/scores", json={"score": 10})
        r = client.post("/api/scores", json={"score": 99})
        assert r.status_code == 200
        assert r.json()["player"]["highScore"] == 99
        assert r.json()["isNewHighScore"] is True

    def test_submit_score_zero(self, auth_client):
        client, _ = auth_client
        r = client.post("/api/scores", json={"score": 0})
        assert r.status_code == 200

    def test_submit_score_unauthenticated(self, client):
        r = client.post("/api/scores", json={"score": 10})
        assert r.status_code == 401

    def test_submit_score_negative_rejected(self, auth_client):
        """Pydantic ge=0 constraint rejects negative scores."""
        client, _ = auth_client
        r = client.post("/api/scores", json={"score": -1})
        assert r.status_code == 422

    def test_submit_score_persists_to_me(self, auth_client):
        """After scoring, /api/auth/me should reflect updated highScore."""
        client, _ = auth_client
        client.post("/api/scores", json={"score": 77})
        r = client.get("/api/auth/me")
        assert r.json()["player"]["highScore"] == 77
