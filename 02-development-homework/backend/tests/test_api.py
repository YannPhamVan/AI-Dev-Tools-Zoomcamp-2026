from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.store import DatabaseStore, store


@pytest.fixture(autouse=True)
def reset_store():
    store.configure("sqlite+pysqlite:///:memory:")
    store.reset()
    yield
    store.reset()


@pytest.fixture
def client():
    return TestClient(app)


def create_trip(client, name="Weekend à Rome"):
    response = client.post("/trips", json={"name": name})
    assert response.status_code == 201
    return response.json()


def add_member(client, trip_id, name):
    response = client.post(f"/trips/{trip_id}/members", json={"name": name})
    assert response.status_code == 201
    return response.json()


def test_create_and_get_trip(client):
    trip = create_trip(client)

    response = client.get(f"/trips/{trip['id']}")

    assert response.status_code == 200
    assert response.json() == {**trip, "members": [], "expenses": []}


def test_create_trip_requires_name(client):
    response = client.post("/trips", json={"name": " "})

    assert response.status_code == 422


def test_add_members_and_reject_duplicate_names(client):
    trip = create_trip(client)
    member = add_member(client, trip["id"], "Yann")

    duplicate = client.post(f"/trips/{trip['id']}/members", json={"name": "yann"})

    assert member["name"] == "Yann"
    assert duplicate.status_code == 409


def test_add_and_list_expenses(client):
    trip = create_trip(client)
    yann = add_member(client, trip["id"], "Yann")
    add_member(client, trip["id"], "Marc")

    response = client.post(
        f"/trips/{trip['id']}/expenses",
        json={"description": "Restaurant", "amount": 80, "paid_by": yann["id"]},
    )

    assert response.status_code == 201
    expense = response.json()
    assert expense["description"] == "Restaurant"
    assert expense["amount"] == 80
    assert expense["paid_by"] == yann["id"]

    listed = client.get(f"/trips/{trip['id']}/expenses")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == expense["id"]


def test_expense_requires_existing_payer_and_positive_amount(client):
    trip = create_trip(client)
    response = client.post(
        f"/trips/{trip['id']}/expenses",
        json={"description": "Taxi", "amount": 0, "paid_by": "missing"},
    )

    assert response.status_code == 422


def test_balances_are_paid_minus_equal_share(client):
    trip = create_trip(client)
    yann = add_member(client, trip["id"], "Yann")
    marc = add_member(client, trip["id"], "Marc")
    add_member(client, trip["id"], "Sarah")
    client.post(
        f"/trips/{trip['id']}/expenses",
        json={"description": "Train", "amount": 90, "paid_by": yann["id"]},
    )
    client.post(
        f"/trips/{trip['id']}/expenses",
        json={"description": "Lunch", "amount": 30, "paid_by": marc["id"]},
    )

    response = client.get(f"/trips/{trip['id']}/balances")

    assert response.status_code == 200
    balances = {entry["member_id"]: entry["balance"] for entry in response.json()}
    assert balances[yann["id"]] == 50
    assert balances[marc["id"]] == -10


def test_settlements_use_greedy_minimum_transfers(client):
    trip = create_trip(client)
    yann = add_member(client, trip["id"], "Yann")
    marc = add_member(client, trip["id"], "Marc")
    sarah = add_member(client, trip["id"], "Sarah")
    ines = add_member(client, trip["id"], "Inès")
    client.post(f"/trips/{trip['id']}/expenses", json={"description": "Train", "amount": 120, "paid_by": yann["id"]})
    client.post(f"/trips/{trip['id']}/expenses", json={"description": "Hotel", "amount": 80, "paid_by": marc["id"]})

    response = client.get(f"/trips/{trip['id']}/settlements")

    assert response.status_code == 200
    assert response.json() == [
        {"from_member_id": sarah["id"], "to_member_id": yann["id"], "amount": 50},
        {"from_member_id": ines["id"], "to_member_id": yann["id"], "amount": 20},
        {"from_member_id": ines["id"], "to_member_id": marc["id"], "amount": 30},
    ]


def test_delete_expense(client):
    trip = create_trip(client)
    yann = add_member(client, trip["id"], "Yann")
    expense = client.post(
        f"/trips/{trip['id']}/expenses",
        json={"description": "Coffee", "amount": 5, "paid_by": yann["id"]},
    ).json()

    response = client.delete(f"/trips/{trip['id']}/expenses/{expense['id']}")

    assert response.status_code == 204
    assert client.get(f"/trips/{trip['id']}/expenses").json() == []


def test_data_persists_when_a_new_store_uses_the_same_database(tmp_path):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'sharetrip.db'}"
    first_store = DatabaseStore(database_url)
    trip = first_store.create_trip("Persisted trip")

    second_store = DatabaseStore(database_url)

    persisted_trip = second_store.get_trip(trip.id)
    assert persisted_trip is not None
    assert persisted_trip.name == "Persisted trip"
