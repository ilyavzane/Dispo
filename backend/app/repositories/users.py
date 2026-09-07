from typing import Any

from app.repositories import db


async def get_users(status: str) -> list[dict]:
    rows = await db.pool.fetch(
        "SELECT id, name, email, role, status, created_at FROM users WHERE ($1::text IS NULL OR status = $1) ORDER BY id",
        status,
    )

    return [dict(row) for row in rows]


async def update_user_status(user_id: int, new_status: str) -> dict[str, Any] | None:
    record = await db.pool.fetchrow(
        "UPDATE users SET status = $1 WHERE id = $2 RETURNING id, name, email, role, status, created_at",
        new_status,
        user_id,
    )

    if record is None:
        return None

    return dict(record)


async def get_drivers(available: bool | None = None) -> list[dict]:

    query = "SELECT id, name, email, role, status, created_at FROM users WHERE role = 'driver' AND status = 'approved'"

    if available is True:
        query += " AND NOT EXISTS (SELECT 1 FROM loads WHERE assigned_driver_id = users.id AND loads.status IN ('in_transit', 'assigned'))"
    elif available is False:
        query += " AND EXISTS (SELECT 1 FROM loads WHERE assigned_driver_id = users.id AND loads.status IN ('in_transit', 'assigned'))"

    drivers = await db.pool.fetch(query)

    return [dict(driver) for driver in drivers]


async def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    user_data = await db.pool.fetchrow(
        "SELECT id, name, email, role, status FROM users WHERE id = $1", user_id
    )

    if user_data is None:
        return None

    return dict(user_data)
