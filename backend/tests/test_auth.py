def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "ilya",
            "password": "12345678",
            "email": "ilyadog@gmail.com",
            "role": "driver",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_is_password_not_in_response(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "ilya",
            "password": "12345678",
            "email": "ilyadog@gmail.com",
            "role": "driver",
        },
    )
    assert "password" not in response.json() and "password_hash" not in response.json()


def test_repeated_email(client):
    response1 = client.post(
        "/auth/register",
        json={
            "name": "ilya",
            "password": "12345678",
            "email": "ilyadog@gmail.com",
            "role": "driver",
        },
    )

    response2 = client.post(
        "/auth/register",
        json={
            "name": "ilya",
            "password": "12345678",
            "email": "ilyadog@gmail.com",
            "role": "driver",
        },
    )

    assert response1.status_code == 201
    assert response2.status_code == 409


def test_register_rejects_admin_role(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "ilya",
            "password": "12345678",
            "email": "ilyadog@gmail.com",
            "role": "admin",
        },
    )

    assert response.status_code == 422


# login


def test_successfull_login(client, approved_user):

    login_response = client.post(
        "auth/login",
        json={"email": approved_user["email"], "password": approved_user["password"]},
    )

    assert login_response.status_code == 200
    assert login_response.json()["access_token"]


def test_rejected_login(client, rejected_user):

    login_response = client.post(
        "auth/login",
        json={"email": rejected_user["email"], "password": rejected_user["password"]},
    )

    assert login_response.status_code == 403


def test_login_pending(client):

    client.post(
        "auth/register",
        json={
            "name": "ilya",
            "password": "12345678",
            "email": "ilyadog@gmail.com",
            "role": "dispatcher",
        },
    )

    login_response = client.post(
        "auth/login",
        json={"email": "ilyadog@gmail.com", "password": "12345678"},
    )

    assert login_response.status_code == 403


def test_wrong_password(client, approved_user):
    login_response = client.post(
        "auth/login",
        json={"email": approved_user["email"], "password": "wrongpassword"},
    )

    assert login_response.status_code == 401


def test_is_password_hash_not_in_json(client, approved_user):
    login_response = client.post(
        "auth/login",
        json={"email": approved_user["email"], "password": approved_user["password"]},
    )

    assert "password_hash" not in login_response.text
