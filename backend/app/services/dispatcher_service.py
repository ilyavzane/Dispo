from decimal import Decimal
import app.repository as repository
from fastapi import HTTPException
from typing import Any


async def create_load(
    origin: str,
    destination: str,
    pickup_date,
    weight: Decimal,
    rate: Decimal,
    created_by: int,
):

    new_load = await repository.create_load(
        origin, destination, pickup_date, weight, rate, created_by
    )

    return new_load


async def get_loads(status: str | None = None):
    loads = await repository.get_loads(status)

    return loads


async def edit_loads(load_id: int, loads_update: dict) -> dict[str, Any]:

    if not loads_update:
        raise HTTPException(status_code=400, detail="No updates were sent")

    edited_load = await repository.edit_load(load_id, loads_update)

    if edited_load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    return edited_load
