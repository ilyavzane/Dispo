from decimal import Decimal
from typing import Any

from fastapi import HTTPException

from app import repository
from app.enums import LoadStatus, Roles, Statuses


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

    if user["role"] == Roles.DRIVER:
        driver_id = user["id"]
    else:
        driver_id = None

    loads = await repository.get_loads(status, driver_id)

    return loads


ALLOWED_UPDATE_COLUMNS = {"origin", "destination", "pickup_date", "weight", "rate"}


async def edit_load(load_id: int, loads_update: dict) -> dict[str, Any]:

    if not loads_update:
        raise HTTPException(status_code=400, detail="No updates were sent")

    if set(loads_update) - ALLOWED_UPDATE_COLUMNS:
        raise ValueError("Unknown column")

    edited_load = await repository.edit_load(load_id, loads_update)

    if edited_load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    return edited_load


async def assign_driver(driver_id: int, assigned_by: int, load_id: int):

    driver = await repository.get_user_by_id(driver_id)

    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    elif driver["role"] != Roles.DRIVER:
        raise HTTPException(status_code=400, detail="User with this id is not driver")
    elif driver["status"] != Statuses.APPROVED:
        raise HTTPException(status_code=400, detail="Driver is not approved")

    updated_load = await repository.assign_driver(driver_id, assigned_by, load_id)

    if updated_load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    return updated_load


async def update_load_status(user: dict, load_id: int, new_status: str):

    allowed_transit = {
        LoadStatus.ASSIGNED: LoadStatus.IN_TRANSIT,
        LoadStatus.IN_TRANSIT: LoadStatus.DELIVERED,
    }

    load = await repository.get_load_by_id(load_id)

    if load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    if user["id"] != load["assigned_driver_id"] and user["role"] != Roles.ADMIN:
        raise HTTPException(status_code=403, detail="This load is not assigned to you")

    if new_status != allowed_transit.get(load["status"]):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    updated_load = await repository.update_load_status(
        load_id=load_id, new_status=new_status
    )

    return updated_load
