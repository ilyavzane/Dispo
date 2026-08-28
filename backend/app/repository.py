import asyncpg
import os
from dotenv import load_dotenv
from typing import Any

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

pool = None


async def create_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)


async def check_health():
    response = await pool.fetchval("SELECT 1")
    return response


async def add_new_user_to_db(
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
