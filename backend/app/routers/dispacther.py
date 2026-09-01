from fastapi import APIRouter, Depends
from app.schemas.loads_schemas import LoadCreate, LoadOut, LoadUpdate
import app.services.dispatcher_service as dispatcher_service
from app.dependencies import require_role
from typing import Literal

dispatcher_router = APIRouter(tags=["Dispatcher"])


@dispatcher_router.post("/loads", status_code=201, response_model=LoadOut)
async def create_load(
    load: LoadCreate, dispatcher_id=Depends(require_role(role="dispatcher"))
):
    response = await dispatcher_service.create_load(
        origin=load.origin,
        destination=load.destination,
        pickup_date=load.pickup_date,
        rate=load.rate,
        weight=load.weight,
        created_by=dispatcher_id,
    )

    return response


@dispatcher_router.get(
    "/loads",
    status_code=200,
    response_model=list[LoadOut],
    dependencies=[Depends(require_role(role="dispatcher"))],
)
async def get_loads(
    status: Literal["new", "in_transit", "delivered", "assigned"] | None = None,
):
    response = await dispatcher_service.get_loads(status)

    return response


@dispatcher_router.patch(
    "/loads/{load_id}",
    status_code=200,
    response_model=LoadOut,
    dependencies=[Depends(require_role(role="dispatcher"))],
)
async def edit_loads(load_id: int, loads_update: LoadUpdate):

    response = await dispatcher_service.edit_loads(
        load_id, loads_update.model_dump(exclude_unset=True)
    )

    return response
