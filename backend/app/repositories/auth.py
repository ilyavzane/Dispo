from typing import Any

from app.repositories import db


async def add_new_user(
    name: str, password_hash: str, email: str, role: str
) -> dict[str, Any]:
    record = await db.pool.fetchrow(
        "INSERT INTO users (name, password_hash, email, role) VALUES ($1, $2, $3, $4) RETURNING id, name, email, role, status, created_at",
        name,
        password_hash,
        email,
        role,
    )

    return dict(record)


async def get_user_by_email(email: str) -> dict[str, Any] | None:
    response = await db.pool.fetchrow(
        "SELECT id, status, name, email, password_hash, role, created_at FROM users WHERE email = $1",
        email,
    )

    if response is None:
        return None

    return dict(response)
