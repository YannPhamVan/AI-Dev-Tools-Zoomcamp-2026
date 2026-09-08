"""Tests for GET /api/leaderboard."""

import pytest


class TestLeaderboard:
    def test_leaderboard_returns_list(self, client):
        r = client.get("/api/leaderboard")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_leaderboard_max_10(self, client):
        r = client.get("/api/leaderboard")
        assert len(r.json()) <= 10

    def test_leaderboard_sorted_desc(self, client):
        entries = client.get("/api/leaderboard").json()
        scores = [e["score"] for e in entries]
        assert scores == sorted(scores, reverse=True)

    def test_leaderboard_ranks_sequential(self, client):
        entries = client.get("/api/leaderboard").json()
        ranks = [e["rank"] for e in entries]
        assert ranks == list(range(1, len(ranks) + 1))

    def test_leaderboard_entry_schema(self, client):
        entries = client.get("/api/leaderboard").json()
        for entry in entries:
            assert "rank" in entry
            assert "username" in entry
            assert "score" in entry

    def test_leaderboard_reflects_new_score(self, auth_client):
        client, _ = auth_client
        # tester starts with score 0 — not in top 3 seeded players
        client.post("/api/scores", json={"score": 999})
        entries = client.get("/api/leaderboard").json()
        # 999 should be the new #1
        assert entries[0]["username"] == "tester"
        assert entries[0]["score"] == 999
        assert entries[0]["rank"] == 1

    def test_leaderboard_no_auth_required(self, client):
        """Leaderboard must be publicly accessible."""
        r = client.get("/api/leaderboard")
        assert r.status_code == 200
