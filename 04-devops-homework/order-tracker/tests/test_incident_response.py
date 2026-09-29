import json
import importlib.util
from types import SimpleNamespace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

main_path = Path(__file__).resolve().parents[1] / "incident-response" / "main.py"
main_spec = importlib.util.spec_from_file_location("incident_response_main", main_path)
main = importlib.util.module_from_spec(main_spec)
main_spec.loader.exec_module(main)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "INCIDENTS_DIR", tmp_path)
    with TestClient(main.app) as test_client:
        yield test_client


def alert_payload():
    return {
        "status": "firing",
        "alerts": [
            {
                "status": "firing",
                "fingerprint": "1234567890abcdef",
                "startsAt": "2026-09-29T16:00:00Z",
                "labels": {
                    "alertname": "Order Tracker 5xx responses",
                    "endpoint": "/api/orders/{order_id}",
                },
                "annotations": {"summary": "5xx response"},
            }
        ],
    }


def test_alert_is_persisted_and_processing_is_scheduled(client, monkeypatch):
    scheduled = []
    monkeypatch.setattr(main, "process_incident", scheduled.append)

    response = client.post("/alerts", json=alert_payload())

    assert response.status_code == 202
    incident_id = response.json()["incidents"][0]["incident_id"]
    assert scheduled == [incident_id]
    saved = json.loads((main.INCIDENTS_DIR / f"{incident_id}.json").read_text())
    assert saved["alert_context"]["endpoint"] == "/api/orders/{order_id}"


def test_duplicate_fingerprint_is_not_processed_twice(client, monkeypatch):
    scheduled = []
    monkeypatch.setattr(main, "process_incident", scheduled.append)
    payload = alert_payload()

    first = client.post("/alerts", json=payload)
    second = client.post("/alerts", json=payload)

    assert first.status_code == 202
    assert second.status_code == 202
    assert second.json()["incidents"][0]["duplicate"] is True
    assert len(scheduled) == 1


def test_unknown_endpoint_is_rejected(client):
    payload = alert_payload()
    payload["alerts"][0]["labels"]["endpoint"] = "http://example.invalid/"

    response = client.post("/alerts", json=payload)

    assert response.status_code == 422


def test_test_notification_without_endpoint_is_accepted(client, monkeypatch):
    scheduled = []
    monkeypatch.setattr(main, "process_incident", scheduled.append)
    payload = {
        "alerts": [
            {
                "status": "firing",
                "labels": {"alertname": "ResponderTest", "test": "true"},
                "annotations": {"summary": "Test notification; no incident to fix"},
            }
        ]
    }

    response = client.post("/alerts", json=payload)

    assert response.status_code == 202
    incident_id = response.json()["incidents"][0]["incident_id"]
    saved = main._read_incident(incident_id)
    assert scheduled == [incident_id]
    assert saved["alert_context"]["test"] is True
    assert saved["alert_context"]["endpoint"] is None


def test_processing_launches_copilot_headlessly(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "INCIDENTS_DIR", tmp_path)
    monkeypatch.setattr(main, "WORKSPACE_PATH", tmp_path)
    monkeypatch.setattr(main, "_collect_context", lambda endpoint, alert: {"logs": [], "traces": []})
    monkeypatch.setattr(main.shutil, "which", lambda _: "/usr/local/bin/copilot")
    monkeypatch.setenv("GH_TOKEN", "test-token")
    commands = []

    def fake_run(command, **_kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout="analysis complete", stderr="")

    monkeypatch.setattr(main.subprocess, "run", fake_run)
    record = {
        "incident_id": "a" * 32,
        "status": "queued",
        "alert": {"startsAt": "2026-09-29T16:00:00Z"},
        "alert_context": {
            "endpoint": "/api/orders/{order_id}",
            "name": "Order Tracker 5xx responses",
        },
    }
    main._write_incident(record["incident_id"], record)

    main.process_incident(record["incident_id"])

    saved = main._read_incident(record["incident_id"])
    assert saved["status"] == "completed"
    assert commands[0][:2] == ["copilot", "-p"]
    assert "--no-ask-user" in commands[0]
    assert "--allow-all-tools" in commands[0]
    assert "test-token" not in " ".join(commands[0])


def test_test_notification_runs_without_repository_permissions(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "INCIDENTS_DIR", tmp_path)
    monkeypatch.setattr(main, "WORKSPACE_PATH", tmp_path)
    monkeypatch.setattr(main.shutil, "which", lambda _: "/usr/local/bin/copilot")
    monkeypatch.setenv("GH_TOKEN", "test-token")
    commands = []

    def fake_run(command, **_kwargs):
        commands.append(command)
        return SimpleNamespace(
            returncode=0,
            stdout="Responder received the test.\nNo incident to fix; no code changes were made.",
            stderr="",
        )

    monkeypatch.setattr(main.subprocess, "run", fake_run)
    record = {
        "incident_id": "b" * 32,
        "status": "queued",
        "alert": {},
        "alert_context": {"test": True, "endpoint": None},
    }
    main._write_incident(record["incident_id"], record)

    main.process_incident(record["incident_id"])

    saved = main._read_incident(record["incident_id"])
    assert saved["status"] == "completed"
    assert "--no-ask-user" in commands[0]
    assert "--allow-all-tools" not in commands[0]