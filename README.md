# Mini Helpdesk

A small ticketing system (helpdesk) API built with FastAPI, SQLAlchemy and
JWT authentication. Built as a portfolio/reference project — it covers a
role-based REST API, an auditable status-history table, and a couple of
analytics endpoints with a lightweight dashboard on top.
http://mini-helpdesk-production-c3cb.up.railway.app/docs

## Features

- JWT authentication, three roles: `admin`, `agent`, `client`
- Ticket CRUD with filtering and pagination
- Every status change is written to `status_history` in the same
  transaction as the update — no drift between the ticket and its audit log
- Comments per ticket
- Reports: tickets by status, overdue tickets, average resolution time
- Streamlit dashboard on top of the report endpoints
- Tests covering auth, permissions, ticket flow and reports

## Schema

```
users            categories          tickets                  comments               status_history
---------------  ----------------    -----------------------  ---------------------  -----------------------
id (PK)          id (PK)             id (PK)                  id (PK)                id (PK)
email            name                title                    ticket_id (FK)         ticket_id (FK)
password_hash                        description              author_id (FK)         old_status
full_name                            status                   body                   new_status
role                                 priority                 created_at             changed_by (FK)
created_at                           category_id (FK)                                changed_at
                                      created_by (FK)
                                      assigned_to (FK)
                                      created_at / updated_at
```

`status`, `priority` and `role` are constrained at the database level
(`CHECK`), so an invalid value can't land in the table even from outside
the API.

## Running locally (without Docker)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate | macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env
# then edit .env and set your own SECRET_KEY

python -m scripts.seed_data       # optional: creates demo users + tickets
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

Demo accounts created by the seed script:

| Role   | Email                | Password  |
|--------|-----------------------|-----------|
| admin  | admin@example.com     | admin123  |
| agent  | agent@example.com     | agent123  |
| client | client@example.com    | client123 |

## Running with Docker

```bash
cp .env.example .env
docker compose up --build
```

## Running the dashboard

```bash
pip install -r requirements-dashboard.txt
streamlit run dashboard/app.py
```

Log in with the `agent` or `admin` demo account — clients don't have
access to reports.

## Running tests

```bash
pip install -r requirements-dev.txt
pytest --cov=app
```

## API overview

| Method | Endpoint                          | Who                  |
|--------|-------------------------------------|----------------------|
| POST   | `/auth/register`                    | anyone                |
| POST   | `/auth/login`                       | anyone                |
| POST   | `/tickets`                          | any authenticated user |
| GET    | `/tickets`                          | any (clients see only their own) |
| GET    | `/tickets/{id}`                     | owner, agent, admin   |
| PATCH  | `/tickets/{id}`                     | agent, admin          |
| POST   | `/tickets/{id}/comments`            | owner, agent, admin   |
| GET    | `/reports/tickets-by-status`        | agent, admin          |
| GET    | `/reports/overdue?hours=24`         | agent, admin          |
| GET    | `/reports/avg-resolution-time`      | agent, admin          |

## Notes on scope

This is a reference implementation, not a production system — a few
things are intentionally simplified so the project stays readable:

- Uses SQLite by default. Swap `DATABASE_URL` in `.env` for a Postgres
  connection string to run against Postgres — the SQLAlchemy models don't
  change.
- `app.main` calls `Base.metadata.create_all()` on startup instead of
  using Alembic migrations. `alembic` is included in `requirements.txt`
  as the natural next step if you want to practice migrations — run
  `alembic init alembic` and point `env.py` at `app.database.Base.metadata`.
- The report queries use plain Python loops instead of SQL `GROUP BY` /
  `AVG` over `status_history`, to keep the logic portable between SQLite
  and Postgres without dialect-specific date functions. Rewriting
  `avg_resolution_time` as a single aggregated SQL query is a good
  exercise once you're comfortable with the current version.
