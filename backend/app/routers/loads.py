from fastapi import APIRouter, Body, Depends

import app.services.loads as loads_service
from app.dependencies import require_role
from app.enums import LoadStatus, Roles
from app.schemas.loads_schemas import LoadCreate, LoadOut, LoadUpdate, UpdateStatus

loads_router = APIRouter(tags=["Loads"])


@loads_router.post("/loads", status_code=201, response_model=LoadOut)
async def create_load(load: LoadCreate, user=Depends(require_role(Roles.DISPATCHER))):
    response = await loads_service.create_load(
        origin=load.origin,
        destination=load.destination,
        pickup_date=load.pickup_date,
        rate=load.rate,
        weight=load.weight,
        created_by=user,
    )

    return response


@loads_router.get(
    "/loads",
    status_code=200,
    response_model=list[LoadOut],
)
async def get_loads(
    status: LoadStatus | None = None,
    user=Depends(require_role(Roles.DISPATCHER, Roles.DRIVER)),
):
    response = await loads_service.get_loads(user, status)

    return response


@loads_router.get(
    "/loads/{load_id}",
    status_code=200,
    response_model=LoadOut,
)
async def get_load_by_id(
    load_id: int, user=Depends(require_role(Roles.DISPATCHER, Roles.DRIVER))
):
    response = await loads_service.get_load_by_id(load_id, user)

    return response


@loads_router.patch(
    "/loads/{load_id}",
    status_code=200,
    response_model=LoadOut,
)
async def edit_loads(
    load_id: int, loads_update: LoadUpdate, user=Depends(require_role(Roles.DISPATCHER))
):

    response = await loads_service.edit_load(
        load_id=load_id,
        loads_update=loads_update.model_dump(exclude_unset=True, exclude_none=True),
        user=user,
    )

    return response


@loads_router.patch("/loads/{load_id}/assign", status_code=200, response_model=LoadOut)
async def assign_driver(
    load_id: int,
    driver_id: int = Body(embed=True),
    user=Depends(require_role(Roles.DISPATCHER)),
):
    response = await loads_service.assign_driver(
        driver_id=driver_id, assigned_by=user, load_id=load_id
    )

    return response


@loads_router.patch("/loads/{load_id}/status", status_code=200, response_model=LoadOut)
async def update_load_status(
    new_status: UpdateStatus, load_id: int, user=Depends(require_role(Roles.DRIVER))
):
    response = await loads_service.update_load_status(
        user=user, load_id=load_id, new_status=new_status.new_status
    )

    return response
