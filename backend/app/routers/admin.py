from fastapi import APIRouter, Depends
from app.dependencies import require_admin
from app.services import admin_service
from typing import Literal
from app.schemas.users_schemas import UserOut, UserStatusUpdate

admin_router = APIRouter(tags=["Admin"], dependencies=[Depends(require_admin)])


@admin_router.get("/users", response_model=list[UserOut])
async def get_users(status: Literal["pending", "approved", "rejected"]):
    response = await admin_service.get_users(status)

    return response


@admin_router.patch(
    "/users/{user_id}/status",
    response_model=UserOut,
)
async def update_user_status(user_id: int, status_update: UserStatusUpdate):
    response = await admin_service.update_user_status(
        user_id=user_id, new_status=status_update.new_status
    )

    return response
