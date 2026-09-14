# Dispo

Freight dispatch app — dispatchers create loads, assign them to drivers and track them through delivery.
German UI, two roles: **Disponent** (dispatcher) and **Fahrer** (driver).

Learning project. The backend is the finished part; the frontend covers the dispatcher's main screen.

## Tech Stack

FastAPI · PostgreSQL · asyncpg · JWT · vanilla JS (no framework, no build step)

## Getting Started

### Backend

```bash
git clone https://github.com/ilyavzane/Dispo.git
cd Dispo/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # fill in your database password and JWT secret
createdb dispo
psql -U <your_db_user> -d dispo -f migrations/001_create_users.sql
psql -U <your_db_user> -d dispo -f migrations/002_create_loads.sql
psql -U <your_db_user> -d dispo -f migrations/003_create_indexes.sql
uvicorn app.main:app --reload
```

Optional demo data: `python scripts/seed.py`

### Frontend

Static files, no build. Serve `frontend/` over HTTP — opening the files directly via
`file://` will not work, because the scripts are ES modules.

```bash
cd ../frontend
python -m http.server 5500
```

Then open http://127.0.0.1:5500/index.html

The API base URL is set in `frontend/js/app.js` (`API`). The origin you serve the
frontend from must be listed in `CORS_ORIGINS`.

## Environment Variables

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `JWT_SECRET` | Secret for signing tokens — required, app refuses to start without it |
| `JWT_ALGORITHM` | Signing algorithm, e.g. `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime, default `60` |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Credentials for the seeded admin account |

## Tests

```bash
cd backend
pytest
```

Tests refuse to run against the production database.

## API

Interactive docs: http://localhost:8000/docs

| Method | Path | Role |
|---|---|---|
| `GET` | `/health` | — |
| `POST` | `/auth/register` | — |
| `POST` | `/auth/login` | — |
| `GET` | `/me` | Disponent, Fahrer |
| `GET` | `/users?status=` | Admin |
| `PATCH` | `/users/{id}/status` | Admin |
| `GET` | `/drivers?available=` | Disponent |
| `GET` | `/loads?status=` | Disponent, Fahrer |
| `GET` | `/loads/{id}` | Disponent, Fahrer |
| `POST` | `/loads` | Disponent |
| `PATCH` | `/loads/{id}` | Disponent |
| `PATCH` | `/loads/{id}/assign` | Disponent |
| `PATCH` | `/loads/{id}/status` | Fahrer |

Admin passes every role check. Drivers only see loads assigned to them.

Load status flow: `new → assigned → in_transit → delivered`

New accounts start as `pending` and must be approved by an admin before they can log in.

## Status — v0.1

**Done**

- Backend: auth, roles, account approval, load CRUD, driver assignment, status transitions, tests
- Frontend: login, registration, pending screen
- Frontend: dispatcher's load board — table, KPIs, detail panel, status filters, edit dialog (`PATCH`)

**Deliberately out of scope for this version**

- Creating loads from the UI (the `POST /loads` endpoint exists and works via `/docs`)
- Driver assignment screen
- Driver's own screen for changing load status
- Admin screen for approving accounts

The backend supports all four; only the UI for them is missing. This was a backend-focused
project, and the remaining work is repetitive frontend wiring that adds nothing new.
