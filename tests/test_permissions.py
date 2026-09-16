from tests.conftest import login_as, make_agent, register_and_login


def test_agent_can_see_all_tickets(client, db_session):
    client_headers = register_and_login(client, email="p1@example.com")
    client.post(
        "/tickets", json={"title": "T1", "description": "d"}, headers=client_headers
    )

    make_agent(db_session, email="pagent@example.com")
    agent_headers = login_as(client, "pagent@example.com")

    response = client.get("/tickets", headers=agent_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_client_cannot_comment_on_others_ticket(client):
    headers_a = register_and_login(client, email="p2@example.com")
    headers_b = register_and_login(client, email="p3@example.com")

    create = client.post(
        "/tickets", json={"title": "T", "description": "d"}, headers=headers_a
    )
    ticket_id = create.json()["id"]

    response = client.post(
        f"/tickets/{ticket_id}/comments", json={"body": "hi"}, headers=headers_b
    )
    assert response.status_code == 403


def test_reports_forbidden_for_client(client):
    headers = register_and_login(client, email="p4@example.com")
    response = client.get("/reports/tickets-by-status", headers=headers)
    assert response.status_code == 403
