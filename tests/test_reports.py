from tests.conftest import login_as, make_agent, register_and_login


def test_tickets_by_status_report(client, db_session):
    client_headers = register_and_login(client, email="r1@example.com")
    client.post(
        "/tickets", json={"title": "T1", "description": "d"}, headers=client_headers
    )
    client.post(
        "/tickets", json={"title": "T2", "description": "d"}, headers=client_headers
    )

    make_agent(db_session, email="ragent@example.com")
    agent_headers = login_as(client, "ragent@example.com")

    response = client.get("/reports/tickets-by-status", headers=agent_headers)
    assert response.status_code == 200
    statuses = {row["status"]: row["count"] for row in response.json()}
    assert statuses.get("open") == 2


def test_overdue_report_returns_empty_for_fresh_tickets(client, db_session):
    client_headers = register_and_login(client, email="r2@example.com")
    client.post(
        "/tickets", json={"title": "Fresh", "description": "d"}, headers=client_headers
    )

    make_agent(db_session, email="ragent2@example.com")
    agent_headers = login_as(client, "ragent2@example.com")

    response = client.get("/reports/overdue?hours=24", headers=agent_headers)
    assert response.status_code == 200
    assert response.json() == []
