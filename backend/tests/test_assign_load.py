from datetime import datetime, timedelta, timezone

from app.security import create_jwt_token


def test_dispatcher_assigns_load_to_driver(client, dispatcher_user, approved_user):
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

    assigning_driver = client.patch(
        f"/loads/{load.json()['id']}/assign",
        json={"driver_id": approved_user["user_id"]},
        headers={"Authorization": f"Bearer {dispatcher_token}"},
    )

    assert assigning_driver.status_code == 200
    assert assigning_driver.json()["status"] == "assigned"
    assert assigning_driver.json()["assigned_driver_id"] == approved_user["user_id"]
    assert assigning_driver.json()["assigned_by"] == dispatcher_user["user_id"]


def test_dispatcher_assigns_not_a_driver(client, dispatcher_user, admin_user):
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

    assigning_driver = client.patch(
        f"/loads/{load.json()['id']}/assign",
        json={"driver_id": admin_user["user_id"]},
        headers={"Authorization": f"Bearer {dispatcher_token}"},
    )

    assert assigning_driver.status_code == 400


def test_driver_assigns(client, approved_user, dispatcher_user):
    dispatcher_token = create_jwt_token(dispatcher_user["user_id"])
    driver_token = create_jwt_token(approved_user["user_id"])

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

    assigning_driver = client.patch(
        f"/loads/{load.json()['id']}/assign",
        json={"driver_id": approved_user["user_id"]},
        headers={"Authorization": f"Bearer {driver_token}"},
    )

    assert assigning_driver.status_code == 403


def test_driver_updates_status(client, dispatcher_user, approved_user):
    dispatcher_token = create_jwt_token(dispatcher_user["user_id"])
    driver_token = create_jwt_token(approved_user["user_id"])

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

    assigning_driver = client.patch(
        f"/loads/{load.json()['id']}/assign",
        json={"driver_id": approved_user["user_id"]},
        headers={"Authorization": f"Bearer {dispatcher_token}"},
    )

    assert assigning_driver.status_code == 200

    load_in_transit = client.patch(
        f"loads/{load.json()['id']}/status",
        json={"new_status": "in_transit"},
        headers={"Authorization": f"Bearer {driver_token}"},
    )

    assert load_in_transit.status_code == 200
    assert load_in_transit.json()["status"] == "in_transit"

    load_delivered = client.patch(
        f"loads/{load_in_transit.json()['id']}/status",
        json={"new_status": "delivered"},
        headers={"Authorization": f"Bearer {driver_token}"},
    )

    assert load_delivered.status_code == 200
    assert load_delivered.json()["status"] == "delivered"


def test_driver_updates_someones_status(
    client, dispatcher_user, approved_user, second_driver
):
    dispatcher_token = create_jwt_token(dispatcher_user["user_id"])
    second_driver_token = create_jwt_token(second_driver["user_id"])

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

    assigning_driver = client.patch(
        f"/loads/{load.json()['id']}/assign",
        json={"driver_id": approved_user["user_id"]},
        headers={"Authorization": f"Bearer {dispatcher_token}"},
    )

    assert assigning_driver.status_code == 200

    load_in_transit = client.patch(
        f"loads/{load.json()['id']}/status",
        json={"new_status": "in_transit"},
        headers={"Authorization": f"Bearer {second_driver_token}"},
    )

    assert load_in_transit.status_code == 403


def test_driver_updates_invalid_status(client, dispatcher_user, approved_user):
    dispatcher_token = create_jwt_token(dispatcher_user["user_id"])
    driver_token = create_jwt_token(approved_user["user_id"])

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

    assigning_driver = client.patch(
        f"/loads/{load.json()['id']}/assign",
        json={"driver_id": approved_user["user_id"]},
        headers={"Authorization": f"Bearer {dispatcher_token}"},
    )

    assert assigning_driver.status_code == 200

    load_in_transit = client.patch(
        f"loads/{load.json()['id']}/status",
        json={"new_status": "in_transit"},
        headers={"Authorization": f"Bearer {driver_token}"},
    )

    assert load_in_transit.status_code == 200
    assert load_in_transit.json()["status"] == "in_transit"

    load_delivered = client.patch(
        f"loads/{load_in_transit.json()['id']}/status",
        json={"new_status": "delivered"},
        headers={"Authorization": f"Bearer {driver_token}"},
    )

    assert load_delivered.status_code == 200
    assert load_delivered.json()["status"] == "delivered"

    load_in_transit_repeat = client.patch(
        f"loads/{load_delivered.json()['id']}/status",
        json={"new_status": "in_transit"},
        headers={"Authorization": f"Bearer {driver_token}"},
    )

    assert load_in_transit_repeat.status_code == 400
