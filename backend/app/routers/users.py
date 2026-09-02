from typing import Literal

from app.dependencies import require_role
from app.schemas.users_schemas import UserOut, UserStatusUpdate
from app.services import users_service
from fastapi import APIRouter, Depends

users_router = APIRouter(tags=["Users"])


@users_router.get(
    "/users",
    response_model=list[UserOut],
    dependencies=[Depends(require_role("admin"))],
)
async def get_users(status: Literal["pending", "approved", "rejected"]):
    response = await users_service.get_users(status)

    return response


@users_router.patch(
    "/users/{user_id}/status",
    response_model=UserOut,
    dependencies=[Depends(require_role("admin"))],
)
async def update_user_status(user_id: int, status_update: UserStatusUpdate):
    response = await users_service.update_user_status(
        user_id=user_id, new_status=status_update.new_status
    )

    return response


@users_router.get(
    "/drivers",
    response_model=list[UserOut],
    status_code=200,
    dependencies=[Depends(require_role("dispatcher"))],
)
async def get_drivers(available: bool | None = None):
    response = await users_service.get_drivers(available)

    return response
