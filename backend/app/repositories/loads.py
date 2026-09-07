from datetime import datetime
from decimal import Decimal
from typing import Any

from app.repositories import db

LOAD_COLUMNS = "id, origin, destination, pickup_date, weight, status, assigned_driver_id, rate, created_by, updated_at, created_at, assigned_by"


async def create_load(
    origin: str,
    destination: str,
    pickup_date: datetime,
    weight: Decimal,
    rate: Decimal,
    created_by: int,
) -> dict[str, Any]:
    new_load = await db.pool.fetchrow(
        f"""INSERT INTO loads (origin, destination, pickup_date, weight, rate, created_by)
         VALUES ($1, $2, $3, $4, $5, $6)
         RETURNING {LOAD_COLUMNS}""",
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
    loads = await db.pool.fetch(
        f"""SELECT {LOAD_COLUMNS}
        FROM loads WHERE ($1::text IS NULL OR status = $1) AND ($2::BIGINT IS NULL OR assigned_driver_id = $2)
        ORDER BY pickup_date ASC, id ASC""",
        status,
        driver_id,
    )

    return [dict(load) for load in loads]


async def get_load_by_id(load_id: int) -> dict[str, Any] | None:
    load = await db.pool.fetchrow(
        f"""SELECT {LOAD_COLUMNS}
        FROM loads WHERE id = $1""",
        load_id,
    )

    if load is None:
        return None

    return dict(load)


ALLOWED_UPDATE_COLUMNS = {"origin", "destination", "pickup_date", "weight", "rate"}


async def edit_load(load_id: int, loads_update) -> dict[str, Any] | None:

    if set(loads_update) - ALLOWED_UPDATE_COLUMNS:
        raise ValueError(status_code=400, detail="Unknown column was given")

    set_clause = ", ".join(
        f"{column} = ${i}" for i, column in enumerate(loads_update, start=1)
    )

    values = list(loads_update.values())

    edited_load = await db.pool.fetchrow(
        f"""UPDATE loads SET {set_clause}, updated_at = now() WHERE id = ${len(values) + 1} 
        RETURNING {LOAD_COLUMNS}""",
        *values,
        load_id,
    )
    if edited_load is None:
        return None

    return dict(edited_load)


async def assign_driver(
    driver_id: int, assigned_by: int, load_id: int
) -> dict[str, Any] | None:
    updated_load = await db.pool.fetchrow(
        f"""UPDATE loads
      SET assigned_driver_id = $1, assigned_by = $2, status = 'assigned', updated_at = now() WHERE id = $3 AND status != 'delivered'
      RETURNING {LOAD_COLUMNS}""",
        driver_id,
        assigned_by,
        load_id,
    )

    if updated_load is None:
        return None

    return dict(updated_load)


async def update_load_status(load_id: int, new_status: str) -> dict[str, Any] | None:
    updated_load = await db.pool.fetchrow(
        f"""UPDATE loads SET status = $1, updated_at = now() WHERE id = $2 AND status != 'delivered'
          RETURNING {LOAD_COLUMNS}""",
        new_status,
        load_id,
    )

    if updated_load is None:
        return None

    return dict(updated_load)
