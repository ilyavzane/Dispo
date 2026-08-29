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

    print(response.json())
    assert response.status_code == 422
