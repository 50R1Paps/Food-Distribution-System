def test_register_first_user(client):
    response = client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_blocked_when_user_exists(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={"username": "another", "password": "secret123"},
    )
    assert response.status_code == 403


def test_login_success(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "ghost", "password": "whatever"},
    )
    assert response.status_code == 401


def test_me_authenticated(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_me_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_invalid_token(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401
