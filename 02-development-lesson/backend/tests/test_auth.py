"""Tests for auth endpoints: signup, signin, signout, me."""

import pytest


class TestSignUp:
    def test_signup_success(self, client):
        r = client.post("/api/auth/signup", json={"username": "newplayer", "password": "pass1"})
        assert r.status_code == 201
        data = r.json()
        assert data["player"]["username"] == "newplayer"
        assert data["player"]["highScore"] == 0
        assert "token" in data

    def test_signup_username_too_short(self, client):
        r = client.post("/api/auth/signup", json={"username": "ab", "password": "pass1"})
        assert r.status_code in (400, 422)

    def test_signup_password_too_short(self, client):
        r = client.post("/api/auth/signup", json={"username": "validname", "password": "abc"})
        assert r.status_code in (400, 422)

    def test_signup_duplicate_username(self, client):
        client.post("/api/auth/signup", json={"username": "dupuser", "password": "pass1"})
        r = client.post("/api/auth/signup", json={"username": "dupuser", "password": "pass1"})
        assert r.status_code == 409
        assert "error" in r.json()

    def test_signup_case_insensitive_duplicate(self, client):
        client.post("/api/auth/signup", json={"username": "CaseUser", "password": "pass1"})
        r = client.post("/api/auth/signup", json={"username": "caseuser", "password": "pass1"})
        assert r.status_code == 409


class TestSignIn:
    def test_signin_success(self, client):
        client.post("/api/auth/signup", json={"username": "alice", "password": "pass1"})
        r = client.post("/api/auth/signin", json={"username": "alice", "password": "pass1"})
        assert r.status_code == 200
        data = r.json()
        assert data["player"]["username"] == "alice"
        assert "token" in data

    def test_signin_wrong_password(self, client):
        client.post("/api/auth/signup", json={"username": "bob", "password": "pass1"})
        r = client.post("/api/auth/signin", json={"username": "bob", "password": "wrongpass"})
        assert r.status_code == 401
        assert r.json()["error"] == "Identifiants invalides."

    def test_signin_unknown_user(self, client):
        r = client.post("/api/auth/signin", json={"username": "ghost", "password": "pass1"})
        assert r.status_code == 401

    def test_signin_seeded_user(self, client):
        """Seeded demo users should be signable-in with the demo password."""
        r = client.post("/api/auth/signin", json={"username": "cobra_kai", "password": "demo1234"})
        assert r.status_code == 200


class TestSignOut:
    def test_signout_success(self, auth_client):
        client, token = auth_client
        r = client.post("/api/auth/signout")
        assert r.status_code == 200
        assert "message" in r.json()

    def test_signout_invalidates_token(self, auth_client):
        client, token = auth_client
        client.post("/api/auth/signout")
        # Token should no longer work
        r = client.get("/api/auth/me")
        assert r.status_code == 401

    def test_signout_without_token(self, client):
        r = client.post("/api/auth/signout")
        assert r.status_code == 401


class TestMe:
    def test_me_authenticated(self, auth_client):
        client, _ = auth_client
        r = client.get("/api/auth/me")
        assert r.status_code == 200
        assert r.json()["player"]["username"] == "tester"

    def test_me_unauthenticated(self, client):
        r = client.get("/api/auth/me")
        assert r.status_code == 401

    def test_me_invalid_token(self, client):
        client.headers["Authorization"] = "Bearer invalidtoken"
        r = client.get("/api/auth/me")
        assert r.status_code == 401
