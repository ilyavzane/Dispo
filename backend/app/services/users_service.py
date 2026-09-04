import logging

from fastapi import HTTPException

from app import repository
from app.enums import Roles

logger = logging.getLogger(__name__)


async def get_users(status: str):
    users = await repository.get_users(status=status)

    return users


async def update_user_status(user_id: int, new_status: str):
    user = await repository.get_user_by_id(user_id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] == Roles.ADMIN:
        raise HTTPException(status_code=403, detail="Admin's status can't be changed")

    new_user_data = await repository.update_user_status(
        user_id=user_id, new_status=new_status
    )

    logger.info("User's: %s  status has been changed to: %s", user_id, new_status)
    return new_user_data


async def get_drivers(available: bool | None = None):
    drivers = await repository.get_drivers(available=available)

    return drivers
