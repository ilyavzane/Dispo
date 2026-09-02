import os
from datetime import datetime
from decimal import Decimal
from typing import Any

import asyncpg
from dotenv import load_dotenv

load_dotenv()
pool = None


# POOL
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


# USERS
async def get_users(status: str) -> list[dict]:
    rows = await pool.fetch(
        "SELECT id, name, email, role, status, created_at FROM users WHERE status = $1 ORDER BY id",
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


async def get_drivers(available: bool | None = None) -> list[dict]:

    query = "SELECT id, name, email, role, status, created_at FROM users WHERE role = 'driver' AND status = 'approved'"

    if available is True:
        query += " AND NOT EXISTS (SELECT 1 FROM loads WHERE assigned_driver_id = users.id AND loads.status IN ('in_transit', 'assigned'))"
    elif available is False:
        query += " AND EXISTS (SELECT 1 FROM loads WHERE assigned_driver_id = users.id AND loads.status IN ('in_transit', 'assigned'))"

    drivers = await pool.fetch(query)

    return [dict(driver) for driver in drivers]


# LOADS
async def create_load(
    origin: str,
    destination: str,
    pickup_date: datetime,
    weight: Decimal,
    rate: Decimal,
    created_by: int,
) -> dict[str, Any]:
    new_load = await pool.fetchrow(
        """INSERT INTO loads (origin, destination, pickup_date, weight, rate, created_by)
         VALUES ($1, $2, $3, $4, $5, $6)
         RETURNING id, origin, destination, pickup_date, weight, status, assigned_driver_id ,rate, created_by, created_at""",
        origin,
        destination,
        pickup_date,
        weight,
        rate,
        created_by,
    )

    return dict(new_load)


async def get_loads(
    status: str | None = None, driver_id: int | None = None
) -> list[dict]:
    loads = await pool.fetch(
        """SELECT id, origin, destination, pickup_date, weight, status, assigned_driver_id ,rate, created_by, created_at, assigned_by
        FROM loads WHERE ($1::text IS NULL OR status = $1) AND ($2::BIGINT IS NULL OR assigned_driver_id = $2)
        ORDER BY pickup_date ASC""",
        status,
        driver_id,
    )

    return [dict(load) for load in loads]


async def get_load_by_id(load_id: int) -> dict[str, Any] | None:
    load = await pool.fetchrow(
        """SELECT id, origin, destination, pickup_date, weight, status, assigned_driver_id ,rate, created_by, created_at, assigned_by
        FROM loads WHERE id = $1""",
        load_id,
    )

    if load is None:
        return None

    return dict(load)


async def edit_load(load_id: int, loads_update) -> dict[str, Any] | None:
    set_clause = ", ".join(
        f"{column} = ${i}" for i, column in enumerate(loads_update, start=1)
    )

    values = list(loads_update.values())

    edited_load = await pool.fetchrow(
        f"""UPDATE loads SET {set_clause} WHERE id = ${len(values) + 1} 
        RETURNING id, origin, destination, pickup_date, weight, status, assigned_driver_id ,rate, created_by, created_at""",
        *values,
        load_id,
    )

    if edited_load is None:
        return None

    return dict(edited_load)


async def assign_driver(
    driver_id: int, assigned_by: int, load_id: int
) -> dict[str, Any] | None:
    updated_load = await pool.fetchrow(
        """UPDATE loads
      SET assigned_driver_id = $1, assigned_by = $2, status = 'assigned' WHERE id = $3
      RETURNING id, origin, destination, pickup_date, weight, status, assigned_driver_id ,rate, created_by, created_at, assigned_by""",
        driver_id,
        assigned_by,
        load_id,
    )

    if updated_load is None:
        return None

    return dict(updated_load)


async def update_load_status(load_id: int, new_status: str) -> dict[str, Any] | None:
    updated_load = await pool.fetchrow(
        """UPDATE loads SET status = $1 WHERE id = $2
          RETURNING id, origin, destination, pickup_date, weight, status, assigned_driver_id ,rate, created_by, created_at, assigned_by""",
        new_status,
        load_id,
    )

    if updated_load is None:
        return None

    return dict(updated_load)


# DEPENDENCY
async def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    user_data = await pool.fetchrow(
        "SELECT id, name, email, role, status FROM users WHERE id = $1", user_id
    )

    if user_data is None:
        return None

    return dict(user_data)
