from datetime import datetime, timedelta, timezone

from app.security import create_jwt_token


# POST
def test_dispatcher_creates_load(client, dispatcher_user):
    token = create_jwt_token(dispatcher_user["user_id"])

    load = client.post(
        "/loads",
        json={
            "origin": "Hamburg",
            "destination": "Berlin",
            "pickup_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "rate": 1.5,
            "weight": 1600,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert load.status_code == 201


def test_driver_creates_load(client, approved_user):
    token = create_jwt_token(approved_user["user_id"])

    load = client.post(
        "/loads",
        json={
            "origin": "Hamburg",
            "destination": "Berlin",
            "pickup_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "rate": 1.5,
            "weight": 1600,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert load.status_code == 403


def test_dispacther_creates_load_with_invalid_data(client, dispatcher_user):
    token = create_jwt_token(dispatcher_user["user_id"])

    load = client.post(
        "/loads",
        json={
            "origin": "Hamburg",
            "destination": 1,
            "pickup_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "rate": 1.5,
            "weight": 1600,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert load.status_code == 422


def test_dispacther_gets_loads(client, dispatcher_user):
    token = create_jwt_token(dispatcher_user["user_id"])

    create_load = client.post(
        "/loads",
        json={
            "origin": "Hamburg",
            "destination": "Berlin",
            "pickup_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "rate": 1.5,
            "weight": 1600,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert create_load.status_code == 201

    all_loads = client.get(
        "/loads",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert all_loads.status_code == 200
    assert len(all_loads.json()) == 1
    assert all_loads.json()[0]["origin"] == "Hamburg"


# GET


# PATCH
def test_dispatcher_edits_load(client, dispatcher_user):
    token = create_jwt_token(dispatcher_user["user_id"])

    load = client.post(
        "/loads",
        json={
            "origin": "Hamburg",
            "destination": "Berlin",
            "pickup_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "rate": 1.5,
            "weight": 1600,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert load.status_code == 201
    assert load.json()["origin"] == "Hamburg"

    edited_load = client.patch(
        f"/loads/{load.json()['id']}",
        json={"origin": "Duseldorf", "destination": "Leipzig"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert edited_load.status_code == 200
    assert edited_load.json()["origin"] == "Duseldorf"


def test_driver_edits_load(client, approved_user, dispatcher_user):
    driver_token = create_jwt_token(approved_user["user_id"])
    dispatcher_token = create_jwt_token(dispatcher_user["user_id"])

    load = client.post(
        "/loads",
        json={
            "origin": "Hamburg",
            "destination": "Berlin",
            "pickup_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "rate": 1.5,
            "weight": 1600,
        },
        headers={"Authorization": f"Bearer {dispatcher_token}"},
    )

    assert load.status_code == 201
    assert load.json()["origin"] == "Hamburg"

    edited_load = client.patch(
        f"/loads/{load.json()['id']}",
        json={"origin": "Duseldorf", "destination": "Leipzig"},
        headers={"Authorization": f"Bearer {driver_token}"},
    )

    assert edited_load.status_code == 403


def test_dispatcher_edits_not_existing_load(client, dispatcher_user):
    token = create_jwt_token(dispatcher_user["user_id"])

    edited_load = client.patch(
        "/loads/100",
        json={"origin": "Duseldorf", "destination": "Leipzig"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert edited_load.status_code == 404
