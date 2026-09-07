import logging
from decimal import Decimal
from typing import Any

from fastapi import HTTPException

import app.repositories.loads as loads_repo
import app.repositories.users as users_repo
from app.enums import LoadStatus, Roles, Statuses

logger = logging.getLogger(__name__)


async def create_load(
    origin: str,
    destination: str,
    pickup_date,
    weight: Decimal,
    rate: Decimal,
    created_by: dict,
):

    new_load = await loads_repo.create_load(
        origin=origin,
        destination=destination,
        pickup_date=pickup_date,
        weight=weight,
        rate=rate,
        created_by=created_by["id"],
    )

    logger.info(
        "New load: From %s To: %s | Created by %s", origin, destination, created_by
    )
    return new_load


async def get_loads(user: dict, status: str | None = None):

    if user["role"] == Roles.DRIVER:
        driver_id = user["id"]
    else:
        driver_id = None

    loads = await loads_repo.get_loads(status=status, driver_id=driver_id)

    return loads


async def get_load_by_id(load_id: int, user):
    load = await loads_repo.get_load_by_id(load_id=load_id)

    if load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    if user["role"] == Roles.DRIVER and load["assigned_driver_id"] != user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Driver is not allowed to check loads not assigned to him",
        )

    return load


ALLOWED_UPDATE_COLUMNS = {"origin", "destination", "pickup_date", "weight", "rate"}


async def edit_load(user, load_id: int, loads_update: dict) -> dict[str, Any]:

    if not loads_update:
        raise HTTPException(status_code=400, detail="No updates were sent")

    if set(loads_update) - ALLOWED_UPDATE_COLUMNS:
        raise HTTPException(status_code=400, detail="Unknown column was given")

    edited_load = await loads_repo.edit_load(load_id=load_id, loads_update=loads_update)

    if edited_load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    logger.info(
        "Edited load: id: %s | Updates : %s | Edited by: %s",
        load_id,
        loads_update,
        user["id"],
    )
    return edited_load


async def assign_driver(driver_id: int, assigned_by: dict, load_id: int):

    driver = await users_repo.get_user_by_id(user_id=driver_id)

    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    elif driver["role"] != Roles.DRIVER:
        raise HTTPException(status_code=400, detail="User with this id is not driver")
    elif driver["status"] != Statuses.APPROVED:
        raise HTTPException(status_code=400, detail="Driver is not approved")

    updated_load = await loads_repo.assign_driver(
        driver_id=driver_id, load_id=load_id, assigned_by=assigned_by["id"]
    )

    if updated_load is None:
        load = await loads_repo.get_load_by_id(load_id=load_id)

        if load is None:
            raise HTTPException(status_code=404, detail="Load not found")

        if load["status"] == LoadStatus.DELIVERED:
            raise HTTPException(status_code=409, detail="Load is already delivered")

        raise HTTPException(status_code=404, detail="Load not found")

    logger.info("Driver %s assigned to the load: %s", driver_id, load_id)

    return updated_load


async def update_load_status(user: dict, load_id: int, new_status: str):

    allowed_transit = {
        LoadStatus.ASSIGNED: LoadStatus.IN_TRANSIT,
        LoadStatus.IN_TRANSIT: LoadStatus.DELIVERED,
    }

    load = await loads_repo.get_load_by_id(load_id=load_id)

    if load is None:
        raise HTTPException(status_code=404, detail="Load not found")

    if user["id"] != load["assigned_driver_id"] and user["role"] != Roles.ADMIN:
        raise HTTPException(status_code=403, detail="This load is not assigned to you")

    if new_status != allowed_transit.get(load["status"]):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    updated_load = await loads_repo.update_load_status(
        load_id=load_id, new_status=new_status
    )

    logger.info(
        "Load %s has been updated to %s | Driver: %s", load_id, new_status, user["id"]
    )

    return updated_load
