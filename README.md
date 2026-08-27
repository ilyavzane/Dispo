# Dispo
Freight dispatch app — dispatchers assign loads to drivers and track them through delivery.

## Tech Stack
FastAPI · PostgreSQL · asyncpg · JWT · vanilla JS

## Getting started
```bash
git clone https://github.com/ilyavzane/Dispo.git
cd Dispo/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # to fill
python scripts/seed.py
uvicorn app.main:app --reload
```

## Environment Variables
DATABASE_URL — Postgres connection string
JWT_SECRET   — secret key for signing JWT tokens

## API
Documentation: http://localhost:8000/docs

🚧 In development