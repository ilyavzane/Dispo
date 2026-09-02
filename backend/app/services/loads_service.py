from decimal import Decimal
from typing import Any

from app import repository
from fastapi import HTTPException


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


async def get_loads(user: dict, status: str | None = None):

    if user["role"] == "driver":
        driver_id = user["id"]
    else:
        driver_id = None

    loads = await repository.get_loads(status, driver_id)

    return loads


async def edit_loads(load_id: int, loads_update: dict) -> dict[str, Any]:

    if not loads_update:
        raise HTTPException(status_code=400, detail="No updates were sent")

    edited_load = await repository.edit_load(load_id, loads_update)

    if edited_load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    return edited_load


async def assign_driver(driver_id: int, assigned_by: int, load_id: int):

    driver = await repository.get_user_by_id(driver_id)

    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    elif driver["role"] != "driver":
        raise HTTPException(status_code=400, detail="User with this id is not driver")

    updated_load = await repository.assign_driver(driver_id, assigned_by, load_id)

    if updated_load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    return updated_load


async def update_load_status(driver_id: int, load_id: int, new_status: str):

    allowed_transit = {"assigned": "in_transit", "in_transit": "delivered"}

    load = await repository.get_load_by_id(load_id)

    if load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    if driver_id != load["assigned_driver_id"]:
        raise HTTPException(status_code=403, detail="This load is not assigned to you")

    if new_status != allowed_transit.get(load["status"]):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    updated_load = await repository.update_load_status(
        load_id=load_id, new_status=new_status
    )

    return updated_load
