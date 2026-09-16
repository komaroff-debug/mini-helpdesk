"""
A tiny Streamlit dashboard over the reports endpoints.

Run with:  streamlit run dashboard/app.py
Requires the API to be running (default http://localhost:8000) and an
agent or admin account to log in with.
"""
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Mini Helpdesk Dashboard", layout="centered")
st.title("Mini Helpdesk — Dashboard")

if "token" not in st.session_state:
    st.session_state.token = None

if st.session_state.token is None:
    st.subheader("Log in (agent or admin)")
    email = st.text_input("Email", value="agent@example.com")
    password = st.text_input("Password", type="password", value="agent123")
    if st.button("Log in"):
        response = requests.post(
            f"{API_URL}/auth/login", data={"username": email, "password": password}
        )
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.rerun()
        else:
            st.error("Login failed. Check the credentials or run scripts/seed_data.py first.")
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    st.subheader("Tickets by status")
    response = requests.get(f"{API_URL}/reports/tickets-by-status", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            st.bar_chart({row["status"]: row["count"] for row in data})
        else:
            st.info("No tickets yet.")
    else:
        st.error("Could not load report. Your session may have expired.")

    st.subheader("Overdue tickets (open > 24h)")
    response = requests.get(f"{API_URL}/reports/overdue?hours=24", headers=headers)
    if response.status_code == 200:
        overdue = response.json()
        if overdue:
            st.table(overdue)
        else:
            st.success("No overdue tickets.")

    st.subheader("Average resolution time by agent")
    response = requests.get(f"{API_URL}/reports/avg-resolution-time", headers=headers)
    if response.status_code == 200:
        avg = response.json()
        if avg:
            st.table(avg)
        else:
            st.info("No closed tickets yet.")

    if st.button("Log out"):
        st.session_state.token = None
        st.rerun()
