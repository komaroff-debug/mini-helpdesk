from tests.conftest import register_and_login


def test_client_can_create_ticket(client):
    headers = register_and_login(client, email="client1@example.com")
    response = client.post(
        "/tickets",
        json={"title": "Broken feature", "description": "It broke.", "priority": "high"},
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Broken feature"
    assert body["status"] == "open"


def test_client_only_sees_own_tickets(client):
    headers_a = register_and_login(client, email="a@example.com")
    headers_b = register_and_login(client, email="b@example.com")

    client.post(
        "/tickets",
        json={"title": "A's ticket", "description": "desc"},
        headers=headers_a,
    )
    response = client.get("/tickets", headers=headers_b)
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_get_nonexistent_ticket_returns_404(client):
    headers = register_and_login(client, email="c@example.com")
    response = client.get("/tickets/9999", headers=headers)
    assert response.status_code == 404


def test_client_cannot_update_ticket(client):
    headers = register_and_login(client, email="d@example.com")
    create = client.post(
        "/tickets",
        json={"title": "Ticket", "description": "desc"},
        headers=headers,
    )
    ticket_id = create.json()["id"]
    response = client.patch(
        f"/tickets/{ticket_id}", json={"status": "closed"}, headers=headers
    )
    assert response.status_code == 403


def test_update_status_writes_history(client, db_session):
    from tests.conftest import make_agent, login_as

    client_headers = register_and_login(client, email="e@example.com")
    create = client.post(
        "/tickets",
        json={"title": "Ticket", "description": "desc"},
        headers=client_headers,
    )
    ticket_id = create.json()["id"]

    make_agent(db_session, email="agent1@example.com")
    agent_headers = login_as(client, "agent1@example.com")

    response = client.patch(
        f"/tickets/{ticket_id}", json={"status": "in_progress"}, headers=agent_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

    from app.models.status_history import StatusHistory

    history = db_session.query(StatusHistory).filter_by(ticket_id=ticket_id).all()
    assert len(history) == 1
    assert history[0].old_status == "open"
    assert history[0].new_status == "in_progress"
