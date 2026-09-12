from typing import Literal

from fastapi import APIRouter, Depends

import app.services.users as users_service
from app.dependencies import require_role
from app.enums import Roles, Statuses
from app.schemas.users_schemas import UserOut, UserStatusUpdate

users_router = APIRouter(tags=["Users"])


@users_router.get("/me", response_model=UserOut)
async def get_myself(user=Depends(require_role(Roles.DISPATCHER, Roles.DRIVER))):
    return user


@users_router.get(
    "/users",
    response_model=list[UserOut],
    dependencies=[Depends(require_role(Roles.ADMIN))],
)
async def get_users(
    status: Literal[Statuses.PENDING, Statuses.APPROVED, Statuses.REJECTED]
    | None = None,
):
    response = await users_service.get_users(status)

    return response


@users_router.patch(
    "/users/{user_id}/status",
    response_model=UserOut,
    dependencies=[Depends(require_role(Roles.ADMIN))],
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
    dependencies=[Depends(require_role(Roles.DISPATCHER))],
)
async def get_drivers(available: bool | None = None):
    response = await users_service.get_drivers(available)

    return response
