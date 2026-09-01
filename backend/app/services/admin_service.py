import app.repository as repository
from fastapi import HTTPException


async def get_users(status: str):
    users = await repository.get_users(status)

    return users


async def update_user_status(user_id: int, new_status: str):
    new_user_data = await repository.update_user_status(user_id, new_status)

    if new_user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    return new_user_data
