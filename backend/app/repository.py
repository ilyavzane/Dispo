import asyncpg
import os
from dotenv import load_dotenv
from typing import Any

load_dotenv()

pool = None


async def create_pool():
    global pool
    DATABASE_URL = os.getenv("DATABASE_URL")
    pool = await asyncpg.create_pool(DATABASE_URL)


async def check_health():
    response = await pool.fetchval("SELECT 1")
    return response


# REGISTRATION & LOGIN


async def add_new_user(
    name: str, password_hash: str, email: str, role: str
) -> dict[str, Any]:
    record = await pool.fetchrow(
        "INSERT INTO users (name, password_hash, email, role) VALUES ($1, $2, $3, $4) RETURNING id, name, email, role, status, created_at",
        name,
        password_hash,
        email,
        role,
    )

    return dict(record)


async def get_user_by_email(email: str) -> dict[str, Any] | None:
    response = await pool.fetchrow(
        "SELECT id, status, name, email, password_hash, role FROM users WHERE email = $1",
        email,
    )

    if response is None:
        return None

    return dict(response)


# ADMIN PANEL
async def get_users(status: str) -> list[dict]:
    rows = await pool.fetch(
        "SELECT id, name, email, role, status, created_at FROM users WHERE status = $1",
        status,
    )

    return [dict(row) for row in rows]


async def update_user_status(user_id: int, new_status: str) -> dict[str, Any] | None:
    record = await pool.fetchrow(
        "UPDATE users SET status = $1 WHERE id = $2 RETURNING id, name, email, role, status, created_at",
        new_status,
        user_id,
    )

    if record is None:
        return None

    return dict(record)


# DEPENDECY


async def get_user_role(user_id: int):
    role = await pool.fetchval("SELECT role FROM users WHERE id = $1", user_id)

    return role
