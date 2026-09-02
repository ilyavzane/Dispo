import pytest
from app.security import create_jwt_token


def test_admin_get_user_listing(client, admin_user):
    token = create_jwt_token(admin_user["user_id"])

    registration_response = client.post(
        "auth/register",
        json={
            "name": "ilya",
            "password": "12345678",
            "email": "ilyadog@gmail.com",
            "role": "dispatcher",
        },
    )

    assert registration_response.status_code == 201

    get_users_response = client.get(
        "/users",
        params={"status": "pending"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert get_users_response.status_code == 200
    assert get_users_response.json()[0]["email"] == "ilyadog@gmail.com"
    assert len(get_users_response.json()) == 1


def test_driver_get_user_listing(client, approved_user):
    token = create_jwt_token(approved_user["user_id"])

    get_users_response = client.get(
        "/users",
        params={"status": "pending"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert get_users_response.status_code == 403


def test_user_without_token_get_user_listing(client):

    get_users_response = client.get("/users", params={"status": "pending"})

    assert get_users_response.status_code == 401


@pytest.mark.parametrize("new_status", ["approved", "rejected"])
def test_patch_user_status(client, admin_user, new_status):
    token = create_jwt_token(admin_user["user_id"])

    registration_response = client.post(
        "auth/register",
        json={
            "name": "ilya",
            "password": "12345678",
            "email": "ilyadog@gmail.com",
            "role": "dispatcher",
        },
    )

    assert registration_response.status_code == 201

    register_user_id = registration_response.json()["id"]

    patch_response = client.patch(
        f"/users/{register_user_id}/status",
        json={"new_status": new_status},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == new_status


def test_not_admin_patch_user_status(client, approved_user):
    token = create_jwt_token(approved_user["user_id"])

    registration_response = client.post(
        "auth/register",
        json={
            "name": "ilya",
            "password": "12345678",
            "email": "ilyadog@gmail.com",
            "role": "dispatcher",
        },
    )

    assert registration_response.status_code == 201

    register_user_id = registration_response.json()["id"]

    patch_response = client.patch(
        f"/users/{register_user_id}/status",
        json={"new_status": "approved"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert patch_response.status_code == 403
