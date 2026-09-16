def test_register_creates_client_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "pw123456", "full_name": "New User"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["role"] == "client"


def test_register_duplicate_email_fails(client):
    payload = {"email": "dup@example.com", "password": "pw123456", "full_name": "Dup"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "pw123456", "full_name": "Login"},
    )
    response = client.post(
        "/auth/login", data={"username": "login@example.com", "password": "pw123456"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_fails(client):
    client.post(
        "/auth/register",
        json={"email": "wrong@example.com", "password": "correct123", "full_name": "Wrong"},
    )
    response = client.post(
        "/auth/login", data={"username": "wrong@example.com", "password": "incorrect"}
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token_fails(client):
    response = client.get("/tickets")
    assert response.status_code == 401
